#!/usr/bin/env python3
import requests
import json
import time

def test_mcp_server_properly():
    """Test the MCP server with proper session handling"""
    url = "http://127.0.0.1:8000/mcp"
    session = requests.Session()
    
    print("🔍 Testing LinkedIn MCP Server...")
    
    try:
        # Step 1: Get session ID with proper headers
        print("📡 Step 1: Getting session ID...")
        headers = {
            'Accept': 'application/json, text/event-stream',
            'Content-Type': 'application/json'
        }
        
        # Make initial request to get session
        init_response = session.post(url, json={
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client", 
                    "version": "1.0.0"
                }
            },
            "id": 1
        }, headers=headers, timeout=10)
        
        print(f"Initialize Status: {init_response.status_code}")
        print(f"Initialize Headers: {dict(init_response.headers)}")
        
        # Get session ID from headers
        session_id = init_response.headers.get('mcp-session-id')
        if session_id:
            print(f"✅ Got session ID: {session_id}")
            # The session ID should be maintained by the session object automatically
            # Let's also try setting it as a cookie
            session.cookies.set('mcp-session-id', session_id)
        else:
            print("⚠️ No session ID received")
        
        print(f"Initialize Response: {init_response.text}")
        
        # Step 2: Test tools/list
        print("\n📋 Step 2: Getting available tools...")
        tools_response = session.post(url, json={
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }, headers=headers, timeout=10)
        
        print(f"Tools Status: {tools_response.status_code}")
        if tools_response.status_code == 200:
            tools_data = tools_response.json()
            print("✅ Tools list successful!")
            print(f"Available tools: {json.dumps(tools_data, indent=2)}")
            
            # Step 3: Test job search
            print("\n🔍 Step 3: Testing job search...")
            search_response = session.post(url, json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "search_jobs",
                    "arguments": {"search_term": "python developer"}
                },
                "id": 3
            }, headers=headers, timeout=45)
            
            print(f"Search Status: {search_response.status_code}")
            if search_response.status_code == 200:
                search_data = search_response.json()
                print("✅ Job search successful!")
                print(f"Search results: {json.dumps(search_data, indent=2)}")
            else:
                print(f"❌ Job search failed: {search_response.text}")
        else:
            print(f"❌ Tools list failed: {tools_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def show_mcp_inspector_info():
    """Show how to access MCP inspector"""
    print("\n" + "="*50)
    print("🔍 MCP INSPECTOR ACCESS")
    print("="*50)
    print("The MCP Inspector is running!")
    print("You can access it at: http://localhost:5173")
    print("\nTo test the LinkedIn MCP server:")
    print("1. Open: http://localhost:5173")
    print("2. Select 'Streamable HTTP' transport")
    print("3. Set URL to: http://localhost:8000/mcp")
    print("4. Click 'Connect'")
    print("5. Test the LinkedIn tools!")
    print("="*50)

if __name__ == "__main__":
    print("⏳ Waiting for server to start...")
    time.sleep(5)
    
    # Test with proper client
    test_mcp_server_properly()
    
    # Show inspector info
    show_mcp_inspector_info() 