# =============================================================================
# Aoi Core Agent - Tool Registry System
# =============================================================================

import inspect
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime
import logging

from pydantic import BaseModel, Field

from ..core.config import AoiConfig

logger = logging.getLogger(__name__)

class ToolDefinition(BaseModel):
    """
    Definition of a tool that can be used by the agent.
    """
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Tool parameters schema"
    )
    function: Optional[Callable] = Field(None, description="Tool function")
    category: str = Field(default="general", description="Tool category")
    version: str = Field(default="1.0.0", description="Tool version")
    author: str = Field(default="Aoi", description="Tool author")
    enabled: bool = Field(default=True, description="Whether tool is enabled")
    
    class Config:
        arbitrary_types_allowed = True

class ToolResult(BaseModel):
    """
    Result of a tool execution.
    """
    success: bool = Field(..., description="Whether execution was successful")
    result: Any = Field(None, description="Tool execution result")
    error: Optional[str] = Field(None, description="Error message if failed")
    execution_time: float = Field(
        ..., description="Execution time in seconds"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )

class ToolRegistry:
    """
    Registry for managing tools available to the Aoi agent.
    
    This class handles tool registration, discovery, and execution,
    providing a standardized interface for agent capabilities.
    """
    
    def __init__(self, config: AoiConfig):
        """
        Initialize the Tool Registry.
        
        Args:
            config: Configuration object.
        """
        self.config = config
        self.tools: Dict[str, ToolDefinition] = {}
        self.categories: Dict[str, List[str]] = {}
        self.is_initialized = False
        
        logger.info("Tool Registry initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize the tool registry and load default tools.
        
        Returns:
            bool: True if initialization successful.
        """
        try:
            logger.info("Initializing Tool Registry...")
            
            # Register default tools
            await self._register_default_tools()
            
            self.is_initialized = True
            logger.info(
                f"Tool Registry initialized with {len(self.tools)} tools"
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Tool Registry: {e}")
            return False
    
    async def _register_default_tools(self) -> None:
        """
        Register default tools available to the agent.
        """
        # System tools
        await self.register_tool(
            name="get_current_time",
            description="Get the current date and time",
            function=self._get_current_time,
            category="system",
            parameters={
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "description": "Time format (iso, human, timestamp)",
                        "default": "iso"
                    }
                }
            }
        )
        
        await self.register_tool(
            name="calculate",
            description="Perform basic mathematical calculations",
            function=self._calculate,
            category="math",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate"
                    }
                },
                "required": ["expression"]
            }
        )
        
        # Text processing tools
        await self.register_tool(
            name="text_summary",
            description="Summarize a given text",
            function=self._text_summary,
            category="text",
            parameters={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to summarize"
                    },
                    "max_length": {
                        "type": "integer",
                        "description": "Maximum summary length",
                        "default": 100
                    }
                },
                "required": ["text"]
            }
        )
        
        # Knowledge tools
        await self.register_tool(
            name="search_knowledge",
            description="Search the knowledge base for relevant information",
            function=self._search_knowledge,
            category="knowledge",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        )
    
    async def register_tool(
        self, 
        name: str, 
        description: str, 
        function: Callable, 
        category: str = "general", 
        parameters: Optional[Dict[str, Any]] = None,
        version: str = "1.0.0", 
        author: str = "Aoi"
    ) -> bool:
        """
        Register a new tool in the registry.
        
        Args:
            name: Tool name (must be unique).
            description: Tool description.
            function: Tool function to execute.
            category: Tool category.
            parameters: Tool parameters schema.
            version: Tool version.
            author: Tool author.
        
        Returns:
            bool: True if tool registered successfully.
        """
        try:
            if name in self.tools:
                logger.warning(f"Tool '{name}' already exists, overwriting")
            
            tool_def = ToolDefinition(
                name=name,
                description=description,
                function=function,
                category=category,
                parameters=parameters or {},
                version=version,
                author=author
            )
            
            self.tools[name] = tool_def
            
            # Update categories
            if category not in self.categories:
                self.categories[category] = []
            if name not in self.categories[category]:
                self.categories[category].append(name)
            
            logger.info(
                f"Tool registered: {name} (category: {category})"
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to register tool '{name}': {e}")
            return False
    
    async def execute_tool(
        self, name: str, parameters: Optional[Dict[str, Any]] = None
    ) -> ToolResult:
        """
        Execute a registered tool.
        
        Args:
            name: Tool name.
            parameters: Tool parameters.
        
        Returns:
            ToolResult: Execution result.
        """
        start_time = datetime.now()
        
        try:
            if name not in self.tools:
                return ToolResult(
                    success=False,
                    error=f"Tool '{name}' not found",
                    execution_time=0.0
                )
            
            tool = self.tools[name]
            
            if not tool.enabled:
                return ToolResult(
                    success=False,
                    error=f"Tool '{name}' is disabled",
                    execution_time=0.0
                )
            
            if not tool.function:
                return ToolResult(
                    success=False,
                    error=f"Tool '{name}' has no function",
                    execution_time=0.0
                )
            
            # Execute tool function
            if inspect.iscoroutinefunction(tool.function):
                result = await tool.function(**(parameters or {}))
            else:
                result = tool.function(**(parameters or {}))
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.debug(
                f"Tool '{name}' executed successfully in {execution_time:.3f}s"
            )
            
            return ToolResult(
                success=True,
                result=result,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Tool '{name}' execution failed: {e}")
            
            return ToolResult(
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """
        Get a tool definition by name.
        
        Args:
            name: Tool name.
        
        Returns:
            ToolDefinition or None if not found.
        """
        return self.tools.get(name)
    
    def list_tools(
        self, category: Optional[str] = None, enabled_only: bool = True
    ) -> List[ToolDefinition]:
        """
        List available tools.
        
        Args:
            category: Filter by category (optional).
            enabled_only: Only return enabled tools.
        
        Returns:
            List of tool definitions.
        """
        tools = list(self.tools.values())
        
        if enabled_only:
            tools = [tool for tool in tools if tool.enabled]
        
        if category:
            tools = [tool for tool in tools if tool.category == category]
        
        return tools
    
    def get_categories(self) -> List[str]:
        """
        Get list of available tool categories.
        
        Returns:
            List of category names.
        """
        return list(self.categories.keys())
    
    async def enable_tool(self, name: str) -> bool:
        """
        Enable a tool.
        
        Args:
            name: Tool name.
        
        Returns:
            bool: True if tool enabled successfully.
        """
        if name in self.tools:
            self.tools[name].enabled = True
            logger.info(f"Tool '{name}' enabled")
            return True
        return False
    
    async def disable_tool(self, name: str) -> bool:
        """
        Disable a tool.
        
        Args:
            name: Tool name.
        
        Returns:
            bool: True if tool disabled successfully.
        """
        if name in self.tools:
            self.tools[name].enabled = False
            logger.info(f"Tool '{name}' disabled")
            return True
        return False
    
    # =============================================================================
    # Default Tool Implementations
    # =============================================================================
    
    async def _get_current_time(self, format: str = "iso") -> str:
        """
        Get current time in specified format.
        """
        now = datetime.now()
        
        if format == "iso":
            return now.isoformat()
        elif format == "human":
            return now.strftime("%Y年%m月%d日 %H時%M分%S秒")
        elif format == "timestamp":
            return str(int(now.timestamp()))
        else:
            return now.isoformat()
    
    async def _calculate(self, expression: str) -> Union[float, str]:
        """
        Perform basic mathematical calculations.
        """
        try:
            # Simple evaluation (be careful with security in production)
            allowed_chars = set('0123456789+-*/()., ')
            if not all(c in allowed_chars for c in expression):
                return "Error: Invalid characters in expression"
            
            result = eval(expression)
            return float(result)
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def _text_summary(self, text: str, max_length: int = 100) -> str:
        """
        Create a simple text summary.
        """
        if len(text) <= max_length:
            return text
        
        # Simple truncation with ellipsis
        return text[:max_length-3] + "..."
    
    async def _search_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search knowledge base (placeholder implementation).
        """
        # TODO: Implement actual knowledge search
        return [
            {
                "title": f"Knowledge item for: {query}",
                "content": f"This is a placeholder result for the query: {query}",
                "relevance": 0.8,
                "source": "knowledge_base"
            }
        ]
    
    async def shutdown(self) -> bool:
        """
        Shutdown the tool registry.
        
        Returns:
            bool: True if shutdown successful.
        """
        try:
            logger.info("Shutting down Tool Registry...")
            
            # Clear tools
            self.tools.clear()
            self.categories.clear()
            
            self.is_initialized = False
            logger.info("Tool Registry shutdown completed")
            return True
            
        except Exception as e:
            logger.error(f"Error during Tool Registry shutdown: {e}")
            return False