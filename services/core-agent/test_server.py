#!/usr/bin/env python3
# =============================================================================
# Aoi Core Agent - Simple Test Server
# =============================================================================

import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

class AoiTestHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for testing Aoi Core Agent."""
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Aoi Core Agent - Test Server</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .status { padding: 20px; background: #e8f5e8; border-radius: 5px; }
        .endpoint { margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 5px; }
        .method { color: #007acc; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Aoi Core Agent - Test Server</h1>
        <div class="status">
            <h2>Status: Running</h2>
            <p>Core Agent service is operational and ready for testing.</p>
        </div>
        
        <h2>Available Endpoints:</h2>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> /health</h3>
            <p>Health check endpoint</p>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> /status</h3>
            <p>Service status information</p>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">POST</span> /chat</h3>
            <p>Chat with the AI agent (placeholder)</p>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> /tools</h3>
            <p>List available tools</p>
        </div>
    </div>
</body>
</html>
"""
            self.wfile.write(html_content.encode('utf-8'))
            
        elif path == "/health":
            self.send_json_response({
                "status": "healthy",
                "service": "aoi-core-agent"
            })
            
        elif path == "/status":
            self.send_json_response({
                "service": "aoi-core-agent",
                "version": "0.1.0",
                "status": "running",
                "mode": "test",
                "endpoints": [
                    "/health",
                    "/status",
                    "/chat",
                    "/tools"
                ]
            })
            
        elif path == "/tools":
            self.send_json_response({
                "tools": [
                    {
                        "name": "get_current_time",
                        "description": "Get the current date and time",
                        "parameters": {}
                    },
                    {
                        "name": "calculate",
                        "description": (
                            "Perform basic mathematical calculations"
                        ),
                        "parameters": {
                            "expression": "string"
                        }
                    },
                    {
                        "name": "text_summary",
                        "description": "Summarize text content",
                        "parameters": {
                            "text": "string",
                            "max_length": "integer"
                        }
                    }
                ]
            })
            
        # Playground API endpoints
        elif path == "/v1/playground/status":
            self.send_json_response({
                "status": "healthy",
                "service": "aoi-core-agent",
                "version": "0.1.0"
            })
            
        elif path == "/v1/playground/agents":
            self.send_json_response([
                {
                    "agent_id": "aoi-agent",
                    "name": "Aoi Core Agent",
                    "model": "gemini-pro",
                    "storage": True,
                    "description": "万能型AIエージェント"
                }
            ])
            
        elif path == "/v1/playground/models":
            self.send_json_response({
                "models": [
                    {
                        "id": "gemini-2.5-pro",
                        "name": "Gemini 2.5 Pro",
                        "provider": "google",
                        "description": (
                            "Latest and most capable model for complex reasoning tasks"
                        ),
                        "context_length": 2000000,
                        "supports_vision": True,
                        "supports_function_calling": True
                    },
                    {
                        "id": "gemini-2.5-flash",
                        "name": "Gemini 2.5 Flash",
                        "provider": "google",
                        "description": (
                            "Latest fast and efficient model for everyday tasks"
                        ),
                        "context_length": 1000000,
                        "supports_vision": True,
                        "supports_function_calling": True
                    },
                    {
                        "id": "gemini-1.5-pro",
                        "name": "Gemini 1.5 Pro",
                        "provider": "google",
                        "description": (
                            "Most capable model for complex reasoning tasks"
                        ),
                        "context_length": 2000000,
                        "supports_vision": True,
                        "supports_function_calling": True
                    },
                    {
                        "id": "gemini-1.5-flash",
                        "name": "Gemini 1.5 Flash",
                        "provider": "google",
                        "description": (
                            "Fast and efficient model for everyday tasks"
                        ),
                        "context_length": 1000000,
                        "supports_vision": True,
                        "supports_function_calling": True
                    },
                    {
                        "id": "gemini-1.0-pro",
                        "name": "Gemini 1.0 Pro",
                        "provider": "google",
                        "description": (
                            "Previous generation model for general tasks"
                        ),
                        "context_length": 30720,
                        "supports_vision": False,
                        "supports_function_calling": True
                    }
                ],
                "total_count": 5
            })
            
        elif path == "/v1/playground/agents/aoi-agent/sessions":
            self.send_json_response([])
            
        elif path.startswith("/v1/playground/agents/aoi-agent/sessions/"):
            session_id = path.split("/")[-1]
            self.send_json_response({
                "id": session_id,
                "agent_id": "aoi-agent",
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z",
                "last_activity": "2024-01-01T00:00:00Z",
                "message_count": 0
            })
            
        else:
            self.send_error(404, "Endpoint not found")
    
    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == "/chat":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                message = data.get('message', '')
                model = data.get(
                    'model', 'gemini-2.5-flash'
                )
                
                response = {
                    "response": (
                        f"Echo: {message} "
                        f"(Using model: {model}) "
                        "(This is a test response from Aoi Core Agent)"
                    ),
                    "session_id": data.get('session_id', 'test-session'),
                    "model": model,
                    "timestamp": "2024-01-01T00:00:00Z",
                    "mode": "test"
                }
                
                self.send_json_response(response)
                
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
                
        elif path == "/v1/playground/agents/aoi-agent/runs":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                message = data.get('message', '')
                
                response = {
                    "content": f"Test response: {message}",
                    "session_id": data.get('session_id', 'test-session'),
                    "agent_id": "aoi-agent",
                    "timestamp": "2024-01-01T00:00:00Z",
                    "metadata": {"mode": "test"}
                }
                
                self.send_json_response(response)
                
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
                
        else:
            self.send_error(404, "Endpoint not found")
    
    def send_json_response(self, data):
        """Send JSON response."""
        self.send_response(200)
        self.send_header(
            'Content-type', 'application/json'
        )
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Custom log message format."""
        print(f"[{self.date_time_string()}] {format % args}")

def main():
    """Start the test server."""
    host = '0.0.0.0'
    port = 8000
    
    print("="*60)
    print("🤖 Aoi Core Agent - Test Server Starting...")
    print("="*60)
    print(f"Server: http://{host}:{port}")
    print(f"Local: http://localhost:{port}")
    print("Press Ctrl+C to stop")
    print("="*60)
    
    try:
        server = HTTPServer((host, port), AoiTestHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🤖 Aoi Core Agent - Test Server Stopped")
        print("="*60)

if __name__ == "__main__":
    main()