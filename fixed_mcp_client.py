#!/usr/bin/env python3
import requests
import json
import time

class ProperMCPClient:
    def __init__(self, base_url="http://127.0.0.1:8000/mcp"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session_id = None
        self.initialized = False

    def initialize(self):
        """Initialize the MCP connection and get session"""
        print("🔄 Initializing MCP connection...")
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'
        }
        
        payload = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "python-test-client",
                    "version": "1.0.0"
                }
            },
            "id": 1
        }
        
        try:
            response = self.session.post(self.base_url, json=payload, headers=headers, timeout=10)
            print(f"Initialize status: {response.status_code}")
            
            if response.status_code == 200:
                # Extract session ID from headers
                self.session_id = response.headers.get('mcp-session-id')
                print(f"✅ Session ID: {self.session_id}")
                
                # Parse the SSE response
                response_text = response.text
                if 'data:' in response_text:
                    # Extract JSON from SSE format
                    lines = response_text.strip().split('\n')
                    for line in lines:
                        if line.startswith('data:'):
                            data_json = line[5:].strip()  # Remove 'data:' prefix
                            try:
                                data = json.loads(data_json)
                                print(f"✅ Server info: {data.get('result', {}).get('serverInfo', {})}")
                                
                                # Send notifications/initialized as per MCP protocol
                                self._send_initialized_notification()
                                
                                self.initialized = True
                                return True
                            except json.JSONDecodeError:
                                continue
                
            print(f"❌ Initialize failed: {response.text}")
            return False
            
        except Exception as e:
            print(f"❌ Initialize error: {e}")
            return False

    def _send_initialized_notification(self):
        """Send the notifications/initialized message as per MCP protocol"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'
        }
        
        if self.session_id:
            headers['mcp-session-id'] = self.session_id
            
        payload = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        try:
            response = self.session.post(self.base_url, json=payload, headers=headers, timeout=5)
            print(f"✅ Sent initialized notification: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Failed to send initialized notification: {e}")

    def call_tool(self, tool_name, arguments=None):
        """Call a specific tool"""
        if not self.initialized:
            print("❌ Client not initialized. Call initialize() first.")
            return None
            
        if arguments is None:
            arguments = {}
            
        print(f"🔧 Calling tool: {tool_name}")
        
        # Use the same session with session ID in headers
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'
        }
        
        # Add session ID to headers if we have it
        if self.session_id:
            headers['mcp-session-id'] = self.session_id
        
        payload = {
            "jsonrpc": "2.0", 
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": int(time.time() * 1000)  # Unique ID
        }
        
        try:
            response = self.session.post(self.base_url, json=payload, headers=headers, timeout=60)
            print(f"Tool call status: {response.status_code}")
            
            if response.status_code == 200:
                # Handle SSE response
                response_text = response.text
                if 'data:' in response_text:
                    lines = response_text.strip().split('\n')
                    for line in lines:
                        if line.startswith('data:'):
                            data_json = line[5:].strip()
                            try:
                                data = json.loads(data_json)
                                return data
                            except json.JSONDecodeError:
                                continue
                                
                # Fallback to regular JSON
                try:
                    return response.json()
                except:
                    return {"raw_response": response_text}
            else:
                print(f"❌ Tool call failed: {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            print(f"❌ Tool call error: {e}")
            return {"error": str(e)}

    def list_tools(self):
        """List available tools"""
        print("📋 Getting available tools...")
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'
        }
        
        if self.session_id:
            headers['mcp-session-id'] = self.session_id
            
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/list", 
            "id": 2
        }
        
        try:
            response = self.session.post(self.base_url, json=payload, headers=headers, timeout=10)
            print(f"List tools status: {response.status_code}")
            
            if response.status_code == 200:
                # Handle SSE response
                response_text = response.text
                if 'data:' in response_text:
                    lines = response_text.strip().split('\n')
                    for line in lines:
                        if line.startswith('data:'):
                            data_json = line[5:].strip()
                            try:
                                data = json.loads(data_json)
                                return data
                            except json.JSONDecodeError:
                                continue
                return response.json()
            else:
                print(f"❌ List tools failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ List tools error: {e}")
            return None

def test_linkedin_mcp():
    """Test the LinkedIn MCP server properly"""
    print("🚀 Testing LinkedIn MCP Server with Fixed Client")
    print("=" * 50)
    
    client = ProperMCPClient()
    
    # Step 1: Initialize
    if not client.initialize():
        print("❌ Failed to initialize")
        return
    
    # Step 2: List tools
    tools = client.list_tools()
    if tools and 'result' in tools:
        print("✅ Tools list successful!")
        tool_names = [tool['name'] for tool in tools['result'].get('tools', [])]
        print(f"Available tools: {tool_names}")
    else:
        print(f"❌ Tools list failed: {tools}")
        return
    
    # Step 3: Test search_jobs
    print("\n🔍 Testing job search...")
    job_result = client.call_tool('search_jobs', {'search_term': 'software engineer'})
    
    if job_result and 'result' in job_result:
        print("✅ Job search successful!")
        print(f"Result: {json.dumps(job_result, indent=2)}")
    else:
        print(f"❌ Job search failed: {job_result}")

if __name__ == "__main__":
    test_linkedin_mcp() 