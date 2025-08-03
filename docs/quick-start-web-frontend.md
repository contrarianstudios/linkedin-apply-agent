# Quick Start: Web Frontend Setup

Get the LinkedIn Apply Agent web interface running in 5 minutes.

## 🚀 Prerequisites

- **Python 3.12+** with `uv` package manager
- **Chrome browser** installed
- **ChromeDriver** matching your Chrome version
- **LinkedIn account** with valid session

## ⚡ Quick Setup (5 Steps)

### 1. Install Dependencies
```bash
cd linkedin-apply-agent
uv sync
```

### 2. Get LinkedIn Cookie
```bash
uv run main.py --get-cookie
# Copy the cookie value that appears
```

### 3. Start All Services
Open **3 separate terminals**:

**Terminal 1 - MCP Server:**
```bash
LINKEDIN_COOKIE="your_cookie_here" uv run main.py --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp --log-level INFO --no-lazy-init
```

**Terminal 2 - CORS Proxy:**
```bash
python3 cors-proxy.py
```

**Terminal 3 - Web Server:**
```bash
python3 -m http.server 3000
```

### 4. Open Web App
```bash
open http://localhost:3000/linkedin-web-app.html
```

### 5. Test Connection
1. Click **"Connect to Server"** button
2. Should show green ✅ **"Connected"** status
3. Try searching for **"software engineer"**

## ✅ Success Checklist

- [ ] All 3 terminals running without errors
- [ ] Web app opens in browser
- [ ] Connection status shows "Connected" (green)
- [ ] Job search returns real LinkedIn results
- [ ] Profile lookup works (try "leong2001")
- [ ] Company research works (try "microsoft")

## 🔧 If Something Goes Wrong

### Connection Failed?
```bash
# Check all services are running
ps aux | grep -E "(main.py|cors-proxy|http.server)"

# Should see 3+ processes
```

### Port Conflicts?
```bash
# Kill existing processes
pkill -f "main.py|cors-proxy|http.server"

# Then restart all services
```

### Cookie Issues?
```bash
# Get fresh cookie
uv run main.py --get-cookie

# Restart MCP server with new cookie
```

### Still Broken?
See the [complete troubleshooting guide](troubleshooting-guide.md).

## 🎯 What Each Service Does

| Service | Port | Purpose |
|---------|------|---------|
| **MCP Server** | 8000 | LinkedIn data scraping & MCP protocol |
| **CORS Proxy** | 9000 | Adds CORS headers for browser access |
| **Web Server** | 3000 | Serves the HTML/JS frontend |

## 🌐 Architecture Overview

```
Browser (localhost:3000) 
    ↓ HTTP requests
CORS Proxy (localhost:9000)
    ↓ Forwards with CORS headers  
MCP Server (localhost:8000)
    ↓ Scrapes data
LinkedIn.com
```

## 📱 Using the Web App

### Job Search
- Enter keywords like "python developer"
- Get real LinkedIn job postings
- Click "View Job" to open on LinkedIn

### Profile Lookup  
- Enter LinkedIn username (e.g., "johndoe")
- Get detailed profile information
- Shows experience, education, skills

### Company Research
- Enter company name (e.g., "Google")
- Check "Include Employees" for staff info
- Get comprehensive company data

### Recommendations
- Click "Get My Recommendations"
- May be empty for new/inactive accounts
- Use job search as alternative

## 🔄 Daily Usage

### Starting Up
```bash
# Quick start script (save as start.sh)
#!/bin/bash
LINKEDIN_COOKIE="your_cookie" uv run main.py --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp --log-level INFO --no-lazy-init &
python3 cors-proxy.py &
python3 -m http.server 3000 &
echo "🚀 All services started!"
echo "🌐 Open: http://localhost:3000/linkedin-web-app.html"
```

### Stopping
```bash
# Kill all services
pkill -f "main.py|cors-proxy|http.server"
```

## 🎉 You're Ready!

Your LinkedIn Apply Agent web interface is now running! 

**Next Steps:**
- Bookmark: `http://localhost:3000/linkedin-web-app.html`
- Try all the features with real LinkedIn data
- Check [troubleshooting guide](troubleshooting-guide.md) if issues arise
- Explore [web integration guide](../web-integration-guide.md) for customization 