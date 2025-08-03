#!/usr/bin/env python3
"""
CORS Proxy for LinkedIn MCP Server

This proxy adds CORS headers to allow web browsers to connect to the MCP server.
Forwards all requests to the MCP server at http://127.0.0.1:8000/mcp/
"""

import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import urllib.error

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CORSProxyHandler(BaseHTTPRequestHandler):
    
    MCP_SERVER_URL = "http://127.0.0.1:8000/mcp/"
    
    def _add_cors_headers(self):
        """Add CORS headers to the response"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Accept, mcp-session-id, X-MCP-Session-ID')
        self.send_header('Access-Control-Expose-Headers', 'mcp-session-id')
        self.send_header('Access-Control-Max-Age', '3600')
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        logger.info(f"CORS Preflight: {self.path}")
        self.send_response(200)
        self._add_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        self._proxy_request('GET')
    
    def do_POST(self):
        """Handle POST requests"""
        self._proxy_request('POST')
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        self._proxy_request('DELETE')
    
    def _proxy_request(self, method):
        """Proxy the request to the MCP server and return response with CORS headers"""
        try:
            # Read request body if present
            content_length = int(self.headers.get('Content-Length', 0))
            request_body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Prepare headers for the target server
            target_headers = {}
            for header_name, header_value in self.headers.items():
                if header_name.lower() not in ['host', 'connection']:
                    target_headers[header_name] = header_value
            
            # Create request to MCP server
            request = urllib.request.Request(
                self.MCP_SERVER_URL,
                data=request_body,
                headers=target_headers,
                method=method
            )
            
            logger.info(f"Proxying {method} request to {self.MCP_SERVER_URL}")
            
            # Forward request to MCP server
            with urllib.request.urlopen(request) as response:
                # Get response data
                response_data = response.read()
                response_headers = dict(response.headers)
                
                # Send response back to client with CORS headers
                self.send_response(response.getcode())
                self._add_cors_headers()
                
                # Forward response headers (except CORS-related ones)
                for header_name, header_value in response_headers.items():
                    if header_name.lower() not in ['access-control-allow-origin', 'access-control-allow-methods']:
                        self.send_header(header_name, header_value)
                
                self.end_headers()
                self.wfile.write(response_data)
                
                logger.info(f"Successfully proxied {method} request - Status: {response.getcode()}")
        
        except urllib.error.HTTPError as e:
            logger.error(f"HTTP error from MCP server: {e.code} - {e.reason}")
            self.send_response(e.code)
            self._add_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            error_response = {
                "jsonrpc": "2.0",
                "id": "proxy-error",
                "error": {
                    "code": e.code,
                    "message": f"MCP Server Error: {e.reason}"
                }
            }
            self.wfile.write(json.dumps(error_response).encode())
        
        except Exception as e:
            logger.error(f"Proxy error: {str(e)}")
            self.send_response(500)
            self._add_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            error_response = {
                "jsonrpc": "2.0",
                "id": "proxy-error", 
                "error": {
                    "code": 500,
                    "message": f"Proxy Error: {str(e)}"
                }
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(format % args)

def run_cors_proxy(host='localhost', port=9000):
    """Run the CORS proxy server"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, CORSProxyHandler)
    
    logger.info(f"🚀 CORS Proxy Server starting on http://{host}:{port}")
    logger.info(f"📡 Forwarding requests to {CORSProxyHandler.MCP_SERVER_URL}")
    logger.info("🌐 Web app should connect to: http://localhost:9000")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("🛑 CORS Proxy Server stopped")
        httpd.shutdown()

if __name__ == "__main__":
    run_cors_proxy() 