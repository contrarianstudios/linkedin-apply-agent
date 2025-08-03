#!/usr/bin/env python3
import requests
import json
import time
import sseclient

def test_mcp_sse_server():
    """Test the MCP server using Server-Sent Events"""
    url = "http://127.0.0.1:8000/mcp"
    
    print("🔍 Testing MCP Server with SSE...")
    
    try:
        # Create SSE connection
        headers = {
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache'
        }
        
        print("📡 Connecting to SSE stream...")
        response = requests.get(url, headers=headers, stream=True)
        
        if response.status_code != 200:
            print(f"❌ Failed to connect: {response.status_code}")
            print(f"Response: {response.text}")
            return
            
        print("✅ Connected to SSE stream!")
        
        # Parse SSE events
        client = sseclient.SSEClient(response)
        
        for event in client.events():
            print(f"📨 Event: {event.event}")
            print(f"📄 Data: {event.data}")
            
            if event.data:
                try:
                    data = json.loads(event.data)
                    print(f"🔍 Parsed: {json.dumps(data, indent=2)}")
                except json.JSONDecodeError:
                    print("⚠️ Could not parse as JSON")
            
            # Break after first few events for testing
            time.sleep(1)
            break
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_mcp_websocket():
    """Alternative test using different approach"""
    url = "http://127.0.0.1:8000/mcp"
    
    print("\n🔗 Testing direct HTTP POST to MCP endpoint...")
    
    try:
        # Try direct JSON-RPC call
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        payload = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            },
            "id": 1
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("⏳ Waiting for server to start...")
    time.sleep(8)
    
    # Try SSE approach
    test_mcp_sse_server()
    
    # Try direct HTTP approach
    test_mcp_websocket() 