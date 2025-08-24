# =============================================================================
# Aoi Core Agent - Main Agent Class
# =============================================================================

from typing import Dict, Optional, Any
from datetime import datetime
import logging

from .config import AoiConfig
from .response_generator import AdvancedResponseGenerator
from ..memory.manager import MemoryManager
from ..tools.registry import ToolRegistry


class AoiAgent:
    """
    Main Aoi AI Agent class.
    
    This class orchestrates the core functionality of the Aoi agent,
    including conversation handling, memory management, and tool execution.
    """
    
    def __init__(self, config: Optional[AoiConfig] = None):
        """
        Initialize the Aoi Agent.
        
        Args:
            config: Configuration object. If None, uses global config.
        """
        self.config = config or AoiConfig()
        self.agent_id = f"aoi-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.session_id: Optional[str] = None
        
        # Initialize components
        self.memory_manager: Optional[MemoryManager] = None
        self.tool_registry: Optional[ToolRegistry] = None
        self.response_generator: Optional[AdvancedResponseGenerator] = None
        
        # Agent state
        self.is_initialized = False
        self.is_running = False
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Aoi Agent initialized with ID: {self.agent_id}")
    
    async def initialize(self) -> bool:
        """
        Initialize the agent and all its components.
        
        Returns:
            bool: True if initialization successful, False otherwise.
        """
        try:
            self.logger.info("Initializing Aoi Agent...")
            
            # Validate configuration
            missing_keys = self.config.get_missing_keys()
            if missing_keys:
                self.logger.warning(f"Missing API keys: {missing_keys}")
                self.logger.warning("Some features may not be available.")
            
            # Initialize memory manager
            self.memory_manager = MemoryManager(self.config)
            await self.memory_manager.initialize()
            
            # Initialize tool registry
            self.tool_registry = ToolRegistry(self.config)
            await self.tool_registry.initialize()
            
            # Initialize advanced response generator
            self.response_generator = AdvancedResponseGenerator(self.config)
            await self.response_generator.initialize()
            
            self.is_initialized = True
            self.logger.info(
                "Aoi Agent initialized successfully"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Aoi Agent: {e}")
            return False
    
    async def start_session(self, user_id: str, session_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Start a new conversation session.
        
        Args:
            user_id: Unique identifier for the user.
            session_context: Optional context data for the session.
        
        Returns:
            str: Session ID.
        """
        if not self.is_initialized:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        
        self.session_id = f"{user_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Initialize session in memory manager
        if self.memory_manager:
            await self.memory_manager.create_session(self.session_id, user_id, session_context)
        
        self.logger.info(
            f"Started session: {self.session_id} for user: {user_id}"
        )
        return self.session_id
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a user message and generate a response.
        
        Args:
            message: User input message.
            context: Optional context data.
        
        Returns:
            Dict containing the agent's response and metadata.
        """
        if not self.session_id:
            raise RuntimeError("No active session. Call start_session() first.")
        
        try:
            self.logger.info(f"Processing message in session {self.session_id}")
            
            # Store user message in memory
            if self.memory_manager:
                await self.memory_manager.store_message(
                    session_id=self.session_id,
                    role="user",
                    content=message,
                    metadata=context
                )
            
            # Retrieve relevant context from memory
            memory_context = await self._get_memory_context(message)
            
            # Generate response using LLM
            response = await self._generate_response(message, memory_context, context)
            
            # Store agent response in memory
            if self.memory_manager:
                await self.memory_manager.store_message(
                    session_id=self.session_id,
                    role="assistant",
                    content=response["content"],
                    metadata=response.get("metadata", {})
                )
            
            self.logger.info(
                f"Message processed successfully in session {self.session_id}"
            )
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return {
                "content": "申し訳ございません。メッセージの処理中にエラーが発生しました。",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _get_memory_context(self, message: str) -> Dict[str, Any]:
        """
        Retrieve relevant context from memory based on the current message.
        
        Args:
            message: Current user message.
        
        Returns:
            Dict containing relevant memory context.
        """
        if not self.memory_manager or not self.session_id:
            return {}
        
        try:
            # Get recent conversation history
            recent_messages = await self.memory_manager.get_recent_messages(
                session_id=self.session_id,
                limit=10
            )
            
            # Search for relevant memories
            relevant_memories = await self.memory_manager.search_memories(
                query=message,
                limit=5
            )
            
            return {
                "recent_messages": recent_messages,
                "relevant_memories": relevant_memories
            }
            
        except Exception as e:
            self.logger.warning(
                f"Failed to retrieve memory context: {e}"
            )
            return {}
    
    async def _generate_response(
        self, 
        message: str, 
        memory_context: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a response using the advanced response generator.
        
        Args:
            message: User input message.
            memory_context: Context from memory.
            context: Additional context data.
        
        Returns:
            Dict containing the generated response.
        """
        try:
            # Use advanced response generator if available
            if (self.response_generator and 
                self.response_generator.is_initialized):
                # Determine user level and task complexity from context
                user_level = (
                    context.get("user_level", "intermediate") 
                    if context else "intermediate"
                )
                task_complexity = (
                    context.get("task_complexity", "medium") 
                    if context else "medium"
                )
                
                response = await self.response_generator.generate_response(
                    message=message,
                    memory_context=memory_context,
                    context=context,
                    user_level=user_level,
                    task_complexity=task_complexity
                )
                
                # Add agent metadata
                response["agent_id"] = self.agent_id
                response["session_id"] = self.session_id
                
                return response
            
            # Fallback to simple response if advanced generator not available
            else:
                response_content = (
                    f"こんにちは！あなたのメッセージ「{message}」を受け取りました。"
                    "現在、Aoiエージェントは開発中です。"
                )
                
                return {
                    "content": response_content,
                    "timestamp": datetime.now().isoformat(),
                    "agent_id": self.agent_id,
                    "session_id": self.session_id,
                    "metadata": {
                        "memory_context_size": len(
                            memory_context.get("recent_messages", [])
                        ),
                        "relevant_memories_count": len(
                            memory_context.get("relevant_memories", [])
                        ),
                        "processing_time": "<1s",
                        "fallback_mode": True
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            # Return error response
            return {
                "content": (
                    f"申し訳ございません。応答生成中にエラーが発生しました: "
                    f"{str(e)}"
                ),
                "timestamp": datetime.now().isoformat(),
                "agent_id": self.agent_id,
                "session_id": self.session_id,
                "metadata": {
                    "error": True,
                    "error_message": str(e),
                    "processing_time": "<1s"
                }
            }
    
    async def end_session(self) -> bool:
        """
        End the current session.
        
        Returns:
            bool: True if session ended successfully.
        """
        if not self.session_id:
            return True
        
        try:
            if self.memory_manager:
                await self.memory_manager.close_session(self.session_id)
            
            self.logger.info(f"Session ended: {self.session_id}")
            self.session_id = None
            return True
            
        except Exception as e:
            self.logger.error(f"Error ending session: {e}")
            return False
    
    async def shutdown(self) -> bool:
        """
        Shutdown the agent and cleanup resources.
        
        Returns:
            bool: True if shutdown successful.
        """
        try:
            self.logger.info("Shutting down Aoi Agent...")
            
            # End current session if active
            if self.session_id:
                await self.end_session()
            
            # Cleanup components
            if self.response_generator:
                await self.response_generator.shutdown()
            
            if self.memory_manager:
                await self.memory_manager.shutdown()
            
            if self.tool_registry:
                await self.tool_registry.shutdown()
            
            self.is_initialized = False
            self.is_running = False
            
            self.logger.info("Aoi Agent shutdown completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the agent.
        
        Returns:
            Dict containing agent status information.
        """
        return {
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "is_initialized": self.is_initialized,
            "is_running": self.is_running,
            "config_valid": len(self.config.get_missing_keys()) == 0,
            "missing_keys": self.config.get_missing_keys(),
            "timestamp": datetime.now().isoformat()
        }