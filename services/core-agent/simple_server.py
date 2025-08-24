#!/usr/bin/env python3
"""
Simple FastAPI server for testing Enconvo integration
"""

from typing import Dict, Any, Optional
from datetime import datetime
import json
import sys
import os

# Load environment variables from .env file
env_file_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_file_path):
    with open(env_file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                os.environ[key] = value
                print(f"Set {key}={value[:10]}...")  # noqa: T201
    print(f"Loaded environment variables from {env_file_path}")  # noqa: T201
else:
    print(f"Environment file not found: {env_file_path}")

# Add src directory to path for imports
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)
print(f"Added to sys.path: {src_path}")
print(f"Current sys.path: {sys.path[:3]}...")  # Show first 3 entries

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    from aoi.core.agent import AoiAgent
    from aoi.core.config import AoiConfig
except ImportError:
    print("FastAPI not available, using simple HTTP server")
    import socketserver
    from http.server import BaseHTTPRequestHandler
    
    # Try to import AoiAgent for simple server too
    try:
        from aoi.core.agent import AoiAgent
        from aoi.core.config import AoiConfig
        AOI_AVAILABLE = True
        print("AoiAgent imported successfully for simple server")
    except ImportError as e:
        AOI_AVAILABLE = False
        print(f"AoiAgent not available: {e}")
        import traceback
        print(f"Import traceback: {traceback.format_exc()}")
        print("Using fallback responses")
    
    class SimpleHandler(BaseHTTPRequestHandler):
        # Class variable to store the AoiAgent instance
        _aoi_agent = None
        _agent_initialized = False
        
        @classmethod
        def initialize_agent(cls):
            """Initialize the AoiAgent once"""
            if not cls._agent_initialized and AOI_AVAILABLE:
                try:
                    # Create config after environment variables are loaded
                    config = AoiConfig()
                    cls._aoi_agent = AoiAgent(config)
                    # Initialize the agent synchronously
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(cls._aoi_agent.initialize())
                    loop.close()
                    cls._agent_initialized = True
                    print("AoiAgent initialized successfully")
                except Exception as e:
                    print(f"Failed to initialize AoiAgent: {e}")
                    import traceback
                    print(f"Error: {traceback.format_exc()}")  # noqa: T201
                    cls._aoi_agent = None
                finally:
                    cls._agent_initialized = True
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Initialize agent if not already done
            if not self.__class__._agent_initialized:
                self.__class__.initialize_agent()
        
        @property
        def aoi_agent(self):
            """Property to access the class-level AoiAgent instance"""
            return self.__class__._aoi_agent

        def generate_ai_response(self, user_message: str) -> str:
            """
            Generate AI response using AoiAgent or fallback to simple rules.
            """
            if self.aoi_agent:
                try:
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    async def get_response():
                        if not self.aoi_agent.session_id:
                            await self.aoi_agent.start_session(
                                user_id="simple-server-user",
                                session_context={"model": "simple-server"}
                            )
                        response = await self.aoi_agent.process_message(
                            user_message)
                        return response.get('content', user_message)
                    
                    result = loop.run_until_complete(get_response())
                    loop.close()
                    return result
                except Exception as e:
                    print(f"AoiAgent error: {e}, falling back")
            
            # Fallback to simple rule-based responses
            message_lower = user_message.lower().strip()
            
            # Greeting responses
            greetings = ['こんにちは', 'hello', 'hi', 'おはよう', 'こんばんは']
            if any(greeting in message_lower for greeting in greetings):
                return "こんにちは！私はAoi（葵）です。何かお手伝いできることはありますか？"
            
            # Question about identity
            identity_words = ['あなたは', 'who are you', '誰', 'what are you']
            if any(word in message_lower for word in identity_words):
                return ("私はAoi（葵）、あなたのコーディングサポートアシスタントです。"
                        "プログラミングやコード作成のお手伝いをします。")
            
            # Programming related questions
            prog_words = ['コード', 'プログラム', 'code', 'programming', 
                          'python', 'javascript', 'typescript']
            if any(word in message_lower for word in prog_words):
                return ("プログラミングに関するご質問ですね。"
                        "具体的にどのような言語や技術についてお聞きしたいですか？"
                        "詳細を教えていただければ、より具体的なアドバイスができます。")
            
            # Help requests
            help_words = ['助けて', 'help', 'ヘルプ', '手伝って']
            if any(word in message_lower for word in help_words):
                return ("もちろんお手伝いします！どのような問題でお困りですか？"
                        "エラーメッセージ、コードの問題、または新しい機能の実装など、"
                        "詳しく教えてください。")
            
            # Thank you responses
            thanks_words = ['ありがとう', 'thank you', 'thanks', 'サンキュー']
            if any(word in message_lower for word in thanks_words):
                return ("どういたしまして！他にも何かお手伝いできることがあれば、"
                        "いつでもお声かけください。")
            
            # Default intelligent response
            return (f"「{user_message}」について理解しました。"
                    "より具体的な情報や詳細があれば、さらに適切なサポートを提供できます。"
                    "どのような点でお手伝いが必要でしょうか？")

        def do_GET(self):
            if self.path == "/":
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    "name": "Aoi Core Agent API",
                    "version": "0.1.0",
                    "status": "running",
                    "timestamp": datetime.now().isoformat()
                }
                self.wfile.write(json.dumps(response).encode())
            elif self.path == "/health":
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat()
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.end_headers()
        
        def do_POST(self):
            if self.path == "/chat":
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                try:
                    data = json.loads(post_data.decode('utf-8'))
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    message = data.get('message', 'No message')
                    
                    # Generate AI response using AoiAgent
                    ai_response = self.generate_ai_response(message)
                    
                    response = {
                        "content": ai_response,
                        "session_id": data.get('session_id', 'test-session'),
                        "agent_id": "aoi-agent",
                        "timestamp": datetime.now().isoformat(),
                        "metadata": {
                            "model": data.get('model', 'test-model')
                        }
                    }
                    response_json = json.dumps(response)
                    print(f"Sending response: {response_json[:200]}...")
                    self.wfile.write(response_json.encode())
                except Exception as e:
                    print(f"Error in /chat endpoint: {e}")
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    error_response = {"error": str(e)}
                    self.wfile.write(json.dumps(error_response).encode())
            elif self.path == "/chat/completions":
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                try:
                    data = json.loads(post_data.decode('utf-8'))
                    messages = data.get('messages', [])
                    model = data.get('model', 'gemini-2.5-flash')
                    
                    # Extract user message
                    user_message = "No message"
                    for msg in messages:
                        if msg.get('role') == 'user':
                            content = msg.get('content', 'No message')
                            # Handle both string and list content formats
                            if isinstance(content, list):
                                # Extract text from list format
                                text_parts = []
                                for item in content:
                                    if (isinstance(item, dict) and 
                                            'text' in item):
                                        text_parts.append(item['text'])
                                    elif isinstance(item, str):
                                        text_parts.append(item)
                                user_message = (' '.join(text_parts)
                                                if text_parts
                                                else 'No message')
                            else:
                                user_message = str(content)
                            break
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    # Generate AI-like response instead of echo
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    ai_response = self.generate_ai_response(user_message)
                    prompt_tokens = len(user_message.split())
                    completion_tokens = len(ai_response.split())
                    
                    response = {
                        "id": f"chatcmpl-{timestamp}",
                        "object": "chat.completion",
                        "created": int(datetime.now().timestamp()),
                        "model": model,
                        "choices": [{
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": ai_response
                            },
                            "finish_reason": "stop"
                        }],
                        "usage": {
                            "prompt_tokens": prompt_tokens,
                            "completion_tokens": completion_tokens,
                            "total_tokens": prompt_tokens + completion_tokens
                        }
                    }
                    response_json = json.dumps(response)
                    print(f"Sending response: {response_json[:200]}...")
                    self.wfile.write(response_json.encode())
                except Exception as e:
                    print(f"Error in /chat/completions endpoint: {e}")
                    print(f"Error type: {type(e).__name__}")
                    try:
                        data_str = post_data.decode('utf-8')
                        print(f"Request data length: {len(data_str)} chars")
                        print(f"Request data preview: {data_str[:500]}...")
                    except Exception as decode_error:
                        print(f"Failed to decode request data: {decode_error}")
                    
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    error_response = {"error": str(e)}
                    self.wfile.write(json.dumps(error_response).encode())
            else:
                self.send_response(404)
                self.end_headers()
        
        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods',
                             'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
    
    if __name__ == "__main__":
        PORT = 8001
        with socketserver.TCPServer(("", PORT), SimpleHandler) as httpd:
            print(f"Simple server running at http://localhost:{PORT}")
            httpd.serve_forever()

else:
    # FastAPI version
    app = FastAPI(
        title="Aoi Core Agent API",
        description="Simple API for Enconvo integration testing",
        version="0.1.0"
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    class ChatRequest(BaseModel):
        message: str = Field(..., description="User message")
        user_id: str = Field(..., description="User identifier")
        session_id: Optional[str] = Field(
            None, description="Session identifier")
        model: str = Field(
            default="gemini-2.5-flash", description="Model to use")
        context: Optional[Dict[str, Any]] = Field(
            None, description="Additional context")
    
    class ChatResponse(BaseModel):
        content: str = Field(..., description="Agent response")
        session_id: str = Field(..., description="Session identifier")
        agent_id: str = Field(..., description="Agent identifier")
        timestamp: str = Field(..., description="Response timestamp")
        metadata: Optional[Dict[str, Any]] = Field(
            None, description="Response metadata")
    
    @app.get("/")
    async def root():
        return {
            "name": "Aoi Core Agent API",
            "version": "0.1.0",
            "status": "running",
            "timestamp": datetime.now().isoformat()
        }
    
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        }
    
    # Initialize Aoi Agent - will be initialized after startup
    aoi_config = None
    aoi_agent = None
    
    @app.on_event("startup")
    async def startup_event():
        """Initialize the Aoi agent on startup."""
        global aoi_config, aoi_agent
        # Initialize config and agent after env load  # noqa: T201
        aoi_config = AoiConfig()
        aoi_agent = AoiAgent(aoi_config)
        await aoi_agent.initialize()
        print("Aoi Agent initialized successfully")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Shutdown the Aoi agent on server shutdown."""
        await aoi_agent.shutdown()
        print("Aoi Agent shutdown completed")
    
    @app.post("/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest):
        try:
            # Start session if not exists
            if not aoi_agent.session_id:
                session_id = await aoi_agent.start_session(
                    user_id=request.user_id,
                    session_context={"model": request.model}
                )
            else:
                session_id = aoi_agent.session_id
            
            # Process message with Aoi Agent
            response_data = await aoi_agent.process_message(
                message=request.message,
                context=request.context
            )
            
            return ChatResponse(
                content=response_data.get(
                    "response", "申し訳ございません。応答の生成に失敗しました。"),
                session_id=session_id,
                agent_id=aoi_agent.agent_id,
                timestamp=datetime.now().isoformat(),
                metadata={
                    "model": request.model,
                    "thinking_used": response_data.get(
                        "thinking_used", False
                    ),
                    "context_sources": response_data.get(
                        "context_sources", []
                    ),
                    "processing_time": response_data.get("processing_time", 0)
                }
            )
            
        except Exception as e:
            print(f"Error processing chat request: {e}")
            return ChatResponse(
                content=f"申し訳ございません。エラーが発生しました: {str(e)}",
                session_id=request.session_id or "error-session",
                agent_id="aoi-agent-error",
                timestamp=datetime.now().isoformat(),
                metadata={"error": str(e), "model": request.model}
            )
    
    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)