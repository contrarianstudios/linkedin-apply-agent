# LinkedIn Apply Agent - Troubleshooting Guide

This guide documents common issues encountered during setup and their solutions, based on real implementation experience.

## 🎯 Quick Diagnosis

### System Status Check
```bash
# Check all services are running
ps aux | grep -E "(main.py|cors-proxy|http.server)"

# Check ports
lsof -i :3000  # Web server
lsof -i :8000  # MCP server  
lsof -i :9000  # CORS proxy

# Test connectivity
curl -s http://localhost:3000/linkedin-web-app.html | head -5
curl -s http://localhost:9000 | head -5
curl -s http://127.0.0.1:8000/mcp/ | head -5
```

## 🐛 Major Issues & Solutions

### 1. CORS Policy Errors

**❌ Error:**
```
Access to fetch at 'http://127.0.0.1:8000/mcp' from origin 'null' has been blocked by CORS policy
```

**🔍 Root Cause:**
- Browser security blocks requests between different origins
- MCP server doesn't include CORS headers
- Opening HTML file directly creates `origin: null`

**✅ Solution:**
1. **Create CORS Proxy** (`cors-proxy.py`)
2. **Serve via HTTP server** instead of opening file directly
3. **Update web app** to use proxy URL

**Implementation:**
```bash
# Start CORS proxy
python3 cors-proxy.py  # Runs on port 9000

# Serve web app via HTTP
python3 -m http.server 3000

# Update web app config
baseUrl: 'http://localhost:9000'  # Not http://127.0.0.1:8000/mcp/
```

### 2. ChromeDriver Issues

**❌ Error:**
```
chromedriver not found
Bad CPU type in executable
```

**🔍 Root Cause:**
- ChromeDriver not installed
- Wrong architecture (Intel vs ARM64 on macOS)
- Version mismatch with Chrome browser

**✅ Solution:**
```bash
# 1. Check Chrome version
google-chrome --version  # or Chrome → About Chrome

# 2. Download matching ChromeDriver for your architecture
# macOS ARM64:
curl -o chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/138.0.7204.184/mac-arm64/chromedriver-mac-arm64.zip"

# 3. Install and make executable
unzip chromedriver.zip
sudo mv chromedriver-mac-arm64/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# 4. Verify
chromedriver --version
```

### 3. LinkedIn Cookie Expiration

**❌ Error:**
```
invalid session id
Failed to execute search_jobs: Message: invalid session id
```

**🔍 Root Cause:**
- LinkedIn cookie expired (~30 days)
- Chrome WebDriver session died
- Multiple concurrent sessions with same cookie

**✅ Solution:**
```bash
# Get fresh cookie
uv run main.py --get-cookie

# Restart server with new cookie
LINKEDIN_COOKIE="new_cookie_here" uv run main.py --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp --log-level INFO --no-lazy-init
```

### 4. MCP Protocol Implementation Issues

**❌ Error:**
```
Bad Request: Missing session ID
Not Acceptable: Client must accept text/event-stream
```

**🔍 Root Cause:**
- Incomplete MCP protocol handshake
- Missing required headers
- Incorrect session management

**✅ Solution:**
Proper MCP client implementation:
```javascript
// 1. Include required headers
headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json, text/event-stream'
}

// 2. Initialize with session ID extraction
const response = await fetch(url, {method: 'POST', headers, body});
const sessionId = response.headers.get('mcp-session-id');

// 3. Send notifications/initialized
await fetch(url, {
    headers: {...headers, 'mcp-session-id': sessionId},
    body: JSON.stringify({
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    })
});

// 4. Include session ID in subsequent requests
headers['mcp-session-id'] = sessionId;
```

### 5. Data Parsing Issues

**❌ Error:**
- Data fetched successfully but shows "Unknown Name", "No job title"
- Console shows rich data but UI displays empty fields

**🔍 Root Cause:**
- Incorrect response structure access
- Looking for `result.result` when data is in `result.structuredContent`
- Missing optional chaining for safety

**✅ Solution:**
```javascript
// Before (incorrect)
const profile = result.result.structuredContent?.result || result.result;

// After (correct)  
const profile = result.result.structuredContent || result.result;

// Safe field access
<h4>${profile?.name || 'Unknown Name'}</h4>
<p>${profile?.job_title || 'No job title'}</p>
```

### 6. Port Conflicts

**❌ Error:**
```
[Errno 48] address already in use
```

**🔍 Root Cause:**
- Previous server instance still running
- Another service using the same port

**✅ Solution:**
```bash
# Find what's using the port
lsof -i :8000

# Kill specific process
kill -9 <PID>

# Or kill all main.py processes
ps aux | grep "main.py" | grep -v grep | awk '{print $2}' | xargs kill
```

### 7. Docker Desktop Issues

**❌ Error:**
```
Cannot connect to the Docker daemon
permission denied: cannot resize Docker.raw
```

**🔍 Root Cause:**
- Docker Desktop not running
- VM disk permission issues
- Conflicting with local setup

**✅ Solution:**
- **Recommended:** Use local Python setup instead
- **Alternative:** Restart Docker, reset to factory defaults
- **Bypass:** Focus on local `uv` installation

### 8. Missing UV Command

**❌ Error:**
```
spawn uv ENOENT
zsh: command not found: uv
```

**🔍 Root Cause:**
- UV installed in user directory not accessible to Claude Desktop
- PATH not set correctly

**✅ Solution:**
```bash
# Create system-wide symlink
sudo ln -sf ~/.local/bin/uv /usr/local/bin/uv

# Verify
which uv
uv --version
```

## 🔧 Advanced Debugging

### Server Logs Analysis
```bash
# Start server with debug logging
LINKEDIN_COOKIE="cookie" uv run main.py --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp --log-level DEBUG --no-lazy-init

# Watch for key log patterns:
# ✅ "Successfully logged in to LinkedIn" 
# ✅ "Using existing Chrome WebDriver session"
# ✅ "Processing request of type CallToolRequest"
# ❌ "invalid session id"
# ❌ "Failed to find element"
```

### Browser Console Debugging
```javascript
// Check connection status
console.log('Connected:', app.initialized);
console.log('Session ID:', app.sessionId);

// Debug response structure
console.log('Raw response:', result);
console.log('Structured content:', result.result.structuredContent);

// Test direct API calls
fetch('http://localhost:9000', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream'
    },
    body: JSON.stringify({
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "debug", "version": "1.0.0"}
        },
        "id": 1
    })
}).then(r => r.text()).then(console.log);
```

### Network Analysis
```bash
# Test CORS proxy
curl -X OPTIONS http://localhost:9000 \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -v

# Test MCP server directly
curl -X POST http://127.0.0.1:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}' \
  | head -5
```

## 🎯 Best Practices

### Startup Sequence
1. **Clean slate:** Kill any existing processes
2. **MCP Server:** Start with fresh cookie and debug logging
3. **CORS Proxy:** Start in separate terminal
4. **Web Server:** Start HTTP server for frontend
5. **Browser:** Open web app and check console
6. **Test:** Connect and verify each tool works

### Development Workflow
```bash
# Terminal 1: MCP Server
LINKEDIN_COOKIE="cookie" uv run main.py --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp --log-level INFO --no-lazy-init

# Terminal 2: CORS Proxy  
python3 cors-proxy.py

# Terminal 3: Web Server
python3 -m http.server 3000

# Browser: http://localhost:3000/linkedin-web-app.html
```

### Maintenance
- **Refresh cookie** every 2-3 weeks
- **Update ChromeDriver** when Chrome updates
- **Monitor logs** for rate limiting warnings
- **Test connection** before long automation sessions

## 🚨 Emergency Recovery

If everything breaks:
```bash
# 1. Nuclear option - kill everything
pkill -f "main.py|cors-proxy|http.server"

# 2. Get fresh cookie
uv run main.py --get-cookie

# 3. Restart all services with new cookie
# (Use commands from startup sequence above)

# 4. If still broken, check:
# - Chrome browser version vs ChromeDriver version
# - LinkedIn account status (logged in on web)
# - Network connectivity
# - Available disk space and memory
```

## 📊 Success Indicators

When everything works correctly:
- ✅ **Browser Console:** No red errors, successful API calls logged
- ✅ **Server Logs:** "Using existing Chrome WebDriver session", successful tool calls
- ✅ **Web UI:** Green "Connected" status, data displays correctly
- ✅ **Network:** All three services responding on their ports
- ✅ **Data:** Job search returns results, profiles display rich information

## 🔗 Related Documentation

- [Web Integration Guide](../web-integration-guide.md) - Complete web app integration
- [Main README](../README.md) - Setup and usage instructions
- [MCP Protocol Docs](https://modelcontextprotocol.io/) - Official MCP documentation 