#!/usr/bin/env python3
import requests
import json
import time

def test_server():
    url = "http://127.0.0.1:8000/mcp"
    session = requests.Session()
    
    # Test 1: Check if server is responsive
    print("🔍 Testing server connectivity...")
    try:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        response = session.post(url, json={
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 1
        }, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        # Extract session ID from headers
        session_id = response.headers.get('mcp-session-id')
        if session_id:
            print(f"Got session ID: {session_id}")
            headers['X-MCP-Session-ID'] = session_id
        
        # Try again with session ID if we got one
        if session_id and response.status_code != 200:
            print("\n🔄 Retrying with session ID...")
            response = session.post(url, json={
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 1
            }, headers=headers, timeout=10)
            print(f"Retry Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is responding!")
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Test 2: Search for jobs
            print("\n🔍 Testing job search...")
            job_response = session.post(url, json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "search_jobs",
                    "arguments": {"search_term": "python developer"}
                },
                "id": 2
            }, headers=headers, timeout=30)
            
            if job_response.status_code == 200:
                job_data = job_response.json()
                print("✅ Job search successful!")
                print(f"Jobs found: {json.dumps(job_data, indent=2)}")
            else:
                print(f"❌ Job search failed: {job_response.status_code}")
                print(f"Response: {job_response.text}")
                
        else:
            print(f"❌ Server error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
    except requests.exceptions.Timeout:
        print("❌ Server timeout")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(10)
    test_server() 