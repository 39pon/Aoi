# =============================================================================
# Aoi Core Agent - FastAPI Server
# =============================================================================

from typing import Dict, List, Optional, Any
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from loguru import logger

from ..core.config import AoiConfig
from ..core.agent import AoiAgent

# =============================================================================
# Request/Response Models
# =============================================================================

class ChatRequest(BaseModel):
    """
    Chat request model.
    """
    message: str = Field(..., description="User message")
    user_id: str = Field(..., description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    model: str = Field(default="gemini-2.5-flash", description="Model to use")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class ChatResponse(BaseModel):
    """
    Chat response model.
    """
    content: str = Field(..., description="Agent response")
    session_id: str = Field(..., description="Session identifier")
    agent_id: str = Field(..., description="Agent identifier")
    timestamp: str = Field(..., description="Response timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Response metadata")

class SessionRequest(BaseModel):
    """
    Session creation request model.
    """
    user_id: str = Field(..., description="User identifier")
    context: Optional[Dict[str, Any]] = Field(None, description="Session context")

class SessionResponse(BaseModel):
    """
    Session response model.
    """
    session_id: str = Field(..., description="Session identifier")
    user_id: str = Field(..., description="User identifier")
    created_at: str = Field(..., description="Session creation timestamp")
    status: str = Field(..., description="Session status")

class StatusResponse(BaseModel):
    """
    Agent status response model.
    """
    agent_id: str = Field(..., description="Agent identifier")
    status: str = Field(..., description="Agent status")
    is_initialized: bool = Field(..., description="Whether agent is initialized")
    session_id: Optional[str] = Field(None, description="Current session ID")
    config_valid: bool = Field(..., description="Whether configuration is valid")
    missing_keys: List[str] = Field(..., description="Missing API keys")
    timestamp: str = Field(..., description="Status timestamp")

class ToolListResponse(BaseModel):
    """
    Tool list response model.
    """
    tools: List[Dict[str, Any]] = Field(..., description="Available tools")
    categories: List[str] = Field(..., description="Tool categories")
    total_count: int = Field(..., description="Total number of tools")

class ToolExecuteRequest(BaseModel):
    """
    Tool execution request model.
    """
    tool_name: str = Field(..., description="Tool name")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Tool parameters")

class ErrorResponse(BaseModel):
    """
    Error response model.
    """
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# =============================================================================
# Global Variables
# =============================================================================

config = AoiConfig()
aoi_agent: Optional[AoiAgent] = None

# =============================================================================
# Lifespan Management
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan - startup and shutdown.
    """
    global aoi_agent
    
    # Startup
    logger.info("Starting Aoi Core Agent API...")
    
    try:
        # Initialize agent
        aoi_agent = AoiAgent(config)
        success = await aoi_agent.initialize()
        
        if not success:
            logger.error("Failed to initialize Aoi Agent")
            raise RuntimeError("Agent initialization failed")
        
        logger.success("Aoi Core Agent API started successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start Aoi Core Agent API: {e}")
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down Aoi Core Agent API...")
        
        if aoi_agent:
            await aoi_agent.shutdown()
        
        logger.success("Aoi Core Agent API shutdown completed")

# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="Aoi Core Agent API",
    description="RESTful API for the Aoi AI Agent Ecosystem",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Dependency Functions
# =============================================================================

async def get_agent() -> AoiAgent:
    """
    Get the global agent instance.
    """
    if not aoi_agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not initialized"
        )
    return aoi_agent

# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """
    Root endpoint - API information.
    """
    return {
        "name": "Aoi Core Agent API",
        "version": "0.1.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/status", response_model=StatusResponse)
async def get_status(agent: AoiAgent = Depends(get_agent)):
    """
    Get agent status.
    """
    try:
        status_data = agent.get_status()
        
        return StatusResponse(
            agent_id=status_data["agent_id"],
            status="running" if status_data["is_initialized"] else "initializing",
            is_initialized=status_data["is_initialized"],
            session_id=status_data.get("session_id"),
            config_valid=status_data["config_valid"],
            missing_keys=status_data["missing_keys"],
            timestamp=status_data["timestamp"]
        )
        
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/sessions", response_model=SessionResponse)
async def create_session(
    request: SessionRequest,
    agent: AoiAgent = Depends(get_agent)
):
    """
    Create a new conversation session.
    """
    try:
        session_id = await agent.start_session(
            user_id=request.user_id,
            session_context=request.context
        )
        
        return SessionResponse(
            session_id=session_id,
            user_id=request.user_id,
            created_at=datetime.now().isoformat(),
            status="active"
        )
        
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    agent: AoiAgent = Depends(get_agent)
):
    """
    Process a chat message.
    """
    try:
        # Start session if not provided
        if not request.session_id:
            session_id = await agent.start_session(
                user_id=request.user_id,
                session_context=request.context
            )
        else:
            session_id = request.session_id
            # Set the session if different from current
            if agent.session_id != session_id:
                await agent.start_session(
                    user_id=request.user_id,
                    session_context=request.context
                )
        
        # Process message
        response = await agent.process_message(
            message=request.message,
            context=request.context
        )
        
        return ChatResponse(
            content=response["content"],
            session_id=response["session_id"],
            agent_id=response["agent_id"],
            timestamp=response["timestamp"],
            metadata=response.get("metadata")
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.delete("/sessions/{session_id}")
async def end_session(
    session_id: str,
    agent: AoiAgent = Depends(get_agent)
):
    """
    End a conversation session.
    """
    try:
        if agent.session_id == session_id:
            success = await agent.end_session()
            if success:
                return {"message": f"Session {session_id} ended successfully"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to end session"
                )
        else:
            return {"message": f"Session {session_id} not active"}
            
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =============================================================================
# Playground API Endpoints
# =============================================================================

@app.get("/v1/playground/agents")
async def get_playground_agents(agent: AoiAgent = Depends(get_agent)):
    """
    Get available playground agents.
    """
    try:
        return [
            {
                "id": "aoi-agent",
                "name": "Aoi Agent",
                "description": "Aoi AI Agent for coding assistance",
                "version": "0.1.0",
                "status": "active" if agent.is_initialized else "inactive",
                "capabilities": [
                    "code_analysis",
                    "problem_solving",
                    "development_assistance"
                ]
            }
        ]
    except Exception as e:
        logger.error(f"Error getting playground agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/v1/playground/status")
async def get_playground_status(agent: AoiAgent = Depends(get_agent)):
    """
    Get playground status.
    """
    try:
        status_data = agent.get_status()
        return {
            "status": "running" if status_data["is_initialized"] else "initializing",
            "agent_count": 1,
            "active_sessions": 1 if status_data.get("session_id") else 0,
            "timestamp": status_data["timestamp"]
        }
    except Exception as e:
        logger.error(f"Error getting playground status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/v1/playground/agents/{agent_id}/sessions")
async def get_playground_sessions(
    agent_id: str,
    agent: AoiAgent = Depends(get_agent)
):
    """
    Get sessions for a specific agent.
    """
    try:
        if agent_id != "aoi-agent":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
        
        # Return current session if active
        sessions = []
        if agent.session_id:
            sessions.append({
                "id": agent.session_id,
                "agent_id": agent_id,
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat()
            })
        
        return sessions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting playground sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/v1/playground/agents/{agent_id}/sessions/{session_id}")
async def get_playground_session(
    agent_id: str,
    session_id: str,
    agent: AoiAgent = Depends(get_agent)
):
    """
    Get a specific session.
    """
    try:
        if agent_id != "aoi-agent":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
        
        if agent.session_id != session_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        return {
            "id": session_id,
            "agent_id": agent_id,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "message_count": 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting playground session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.delete("/v1/playground/agents/{agent_id}/sessions/{session_id}")
async def delete_playground_session(
    agent_id: str,
    session_id: str,
    agent: AoiAgent = Depends(get_agent)
):
    """
    Delete a specific session.
    """
    try:
        if agent_id != "aoi-agent":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
        
        if agent.session_id == session_id:
            success = await agent.end_session()
            if success:
                return {"message": f"Session {session_id} deleted successfully"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete session"
                )
        else:
            # Session not found or already deleted
            return {"message": f"Session {session_id} not found or already deleted"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting playground session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/v1/playground/models")
async def get_available_models():
    """
    Get available Gemini models.
    """
    try:
        # Gemini models list
        models = [
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
        ]
        
        return {
            "models": models,
            "total_count": len(models)
        }
        
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/v1/playground/agents/{agent_id}/runs")
async def create_agent_run(
    agent_id: str,
    request: ChatRequest,
    agent: AoiAgent = Depends(get_agent)
):
    """
    Create a new agent run (chat interaction).
    """
    try:
        if agent_id != "aoi-agent":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
        
        # Start session if not provided
        if not request.session_id:
            session_id = await agent.start_session(
                user_id=request.user_id,
                session_context=request.context
            )
        else:
            session_id = request.session_id
            # Set the session if different from current
            if agent.session_id != session_id:
                await agent.start_session(
                    user_id=request.user_id,
                    session_context=request.context
                )
        
        # Process message
        response = await agent.process_message(
            message=request.message,
            context=request.context
        )
        
        return ChatResponse(
            content=response["content"],
            session_id=response["session_id"],
            agent_id=response["agent_id"],
            timestamp=response["timestamp"],
            metadata=response.get("metadata")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating agent run: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/tools", response_model=ToolListResponse)
async def list_tools(
    category: Optional[str] = None,
    agent: AoiAgent = Depends(get_agent)
):
    """
    List available tools.
    """
    try:
        if not agent.tool_registry:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Tool registry not available"
            )
        
        tools = agent.tool_registry.list_tools(category=category)
        categories = agent.tool_registry.get_categories()
        
        tool_list = []
        for tool in tools:
            tool_list.append({
                "name": tool.name,
                "description": tool.description,
                "category": tool.category,
                "version": tool.version,
                "author": tool.author,
                "enabled": tool.enabled,
                "parameters": tool.parameters
            })
        
        return ToolListResponse(
            tools=tool_list,
            categories=categories,
            total_count=len(tool_list)
        )
        
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/tools/execute")
async def execute_tool(
    request: ToolExecuteRequest,
    agent: AoiAgent = Depends(get_agent)
):
    """
    Execute a tool.
    """
    try:
        if not agent.tool_registry:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Tool registry not available"
            )
        
        result = await agent.tool_registry.execute_tool(
            name=request.tool_name,
            parameters=request.parameters
        )
        
        return {
            "success": result.success,
            "result": result.result,
            "error": result.error,
            "execution_time": result.execution_time,
            "timestamp": result.timestamp
        }
        
    except Exception as e:
        logger.error(f"Error executing tool: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# =============================================================================
# Error Handlers
# =============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """
    Handle HTTP exceptions.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail or "HTTP Error",
            detail=f"Status: {exc.status_code}"
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """
    Handle general exceptions.
    """
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            detail=str(exc)
        ).dict()
    )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "aoi.api.server:app",
        host=config.api_host,
        port=config.api_port,
        workers=config.api_workers,
        log_level=config.log_level.lower(),
        reload=config.debug_mode
    )