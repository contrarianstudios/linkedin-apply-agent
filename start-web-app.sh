#!/bin/bash

# LinkedIn Apply Agent - Web Frontend Startup Script
# This script starts all three required services for the web frontend

set -e

echo "🚀 LinkedIn Apply Agent - Web Frontend Startup"
echo "=============================================="

# Check if LinkedIn cookie is provided
if [ -z "$LINKEDIN_COOKIE" ]; then
    echo "❌ Error: LINKEDIN_COOKIE environment variable not set"
    echo ""
    echo "To get your LinkedIn cookie, run:"
    echo "  uv run main.py --get-cookie"
    echo ""
    echo "Then set it as an environment variable:"
    echo "  export LINKEDIN_COOKIE='your_cookie_here'"
    echo "  ./start-web-app.sh"
    echo ""
    exit 1
fi

echo "✅ LinkedIn cookie found"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv package manager not found"
    echo "Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uv package manager found"

# Check if Chrome is installed (basic check)
if ! command -v google-chrome &> /dev/null && ! command -v chromium &> /dev/null && ! ls /Applications/Google\ Chrome.app &> /dev/null; then
    echo "⚠️  Warning: Chrome browser not detected"
    echo "Make sure Chrome is installed for LinkedIn scraping to work"
fi

# Check if ChromeDriver is available
if ! command -v chromedriver &> /dev/null; then
    echo "⚠️  Warning: chromedriver not found in PATH"
    echo "You may need to install ChromeDriver matching your Chrome version"
fi

echo ""
echo "🔄 Installing dependencies..."
uv sync --quiet

echo "🔄 Starting services..."

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    pkill -f "main.py --transport streamable-http" 2>/dev/null || true
    pkill -f "cors-proxy.py" 2>/dev/null || true
    pkill -f "python.*http.server.*3000" 2>/dev/null || true
    echo "✅ All services stopped"
}

# Setup cleanup trap
trap cleanup EXIT INT TERM

# Start MCP Server
echo "📡 Starting MCP Server (port 8000)..."
LINKEDIN_COOKIE="$LINKEDIN_COOKIE" uv run main.py --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp --log-level INFO --no-lazy-init > mcp-server.log 2>&1 &
MCP_PID=$!

# Wait a moment for MCP server to start
sleep 3

# Check if MCP server started successfully
if ! kill -0 $MCP_PID 2>/dev/null; then
    echo "❌ Error: MCP Server failed to start"
    echo "Check mcp-server.log for details"
    exit 1
fi

# Start CORS Proxy
echo "🔗 Starting CORS Proxy (port 9000)..."
python3 cors-proxy.py > cors-proxy.log 2>&1 &
CORS_PID=$!

# Wait a moment for CORS proxy to start
sleep 2

# Check if CORS proxy started successfully
if ! kill -0 $CORS_PID 2>/dev/null; then
    echo "❌ Error: CORS Proxy failed to start"
    echo "Check cors-proxy.log for details"
    exit 1
fi

# Start Web Server
echo "🌐 Starting Web Server (port 3000)..."
python3 -m http.server 3000 > web-server.log 2>&1 &
WEB_PID=$!

# Wait a moment for web server to start
sleep 2

# Check if web server started successfully
if ! kill -0 $WEB_PID 2>/dev/null; then
    echo "❌ Error: Web Server failed to start"
    echo "Check web-server.log for details"
    exit 1
fi

echo ""
echo "🎉 All services started successfully!"
echo ""
echo "📱 Web App: http://localhost:3000/linkedin-web-app.html"
echo "📊 Server Status:"
echo "  - MCP Server: http://127.0.0.1:8000/mcp"
echo "  - CORS Proxy: http://localhost:9000"
echo "  - Web Server: http://localhost:3000"
echo ""
echo "📋 Next Steps:"
echo "  1. Open: http://localhost:3000/linkedin-web-app.html"
echo "  2. Click 'Connect to Server'"
echo "  3. Try searching for 'software engineer'"
echo ""
echo "📄 Logs:"
echo "  - MCP Server: tail -f mcp-server.log"
echo "  - CORS Proxy: tail -f cors-proxy.log"
echo "  - Web Server: tail -f web-server.log"
echo ""
echo "Press Ctrl+C to stop all services"

# Open web app automatically (on macOS)
if command -v open &> /dev/null; then
    echo "🚀 Opening web app..."
    sleep 2
    open http://localhost:3000/linkedin-web-app.html
fi

# Keep script running to maintain background processes
echo "🔄 Services running... (Ctrl+C to stop)"
wait 