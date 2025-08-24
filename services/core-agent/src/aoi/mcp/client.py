# =============================================================================
# Aoi Core Agent - MCP Client Implementation
# =============================================================================

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MCPRequest(BaseModel):
    """
    MCP request model.
    """
    server_name: str = Field(..., description="MCP server name")
    tool_name: str = Field(..., description="Tool name to execute")
    args: Dict[str, Any] = Field(
        default_factory=dict, description="Tool arguments"
    )
    request_id: Optional[str] = Field(None, description="Request identifier")


class MCPResponse(BaseModel):
    """
    MCP response model.
    """
    success: bool = Field(..., description="Whether request was successful")
    result: Any = Field(None, description="Tool execution result")
    error: Optional[str] = Field(None, description="Error message if failed")
    execution_time: float = Field(..., description="Execution time in seconds")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    request_id: Optional[str] = Field(None, description="Request identifier")


class MCPClient:
    """
    MCP Client for communicating with external MCP servers.
    
    This client provides a unified interface for interacting with various
    MCP servers like Sequential Thinking, Brave Search, GitHub, and Ref.
    """
    
    def __init__(self):
        """
        Initialize the MCP Client.
        """
        self.servers: Dict[str, Any] = {}
        self.is_initialized = False
        
        logger.info("MCP Client initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize the MCP client and register available servers.
        
        Returns:
            bool: True if initialization successful.
        """
        try:
            logger.info("Initializing MCP Client...")
            
            # Register available MCP servers
            await self._register_servers()
            
            self.is_initialized = True
            logger.info(
                f"MCP Client initialized with {len(self.servers)} servers"
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP Client: {e}")
            return False
    
    async def _register_servers(self) -> None:
        """
        Register available MCP servers.
        """
        # MCP servers will be registered when available
        logger.info("MCP servers registration placeholder")
        
        # MCP servers will be implemented when available
        self.servers = {
            "sequential_thinking": None,
            "brave_search": None,
            "github": None,
            "ref": None,
            "deepl": None
        }
        
        logger.info(f"Registered {len(self.servers)} MCP servers")
    
    async def register_server(
        self, server_name: str, server_instance: Any
    ) -> bool:
        """
        Register an MCP server instance.
        
        Args:
            server_name: Name of the server to register.
            server_instance: Server instance to register.
        
        Returns:
            bool: True if registration successful.
        """
        try:
            self.servers[server_name] = server_instance
            logger.info(f"Registered MCP server: {server_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register server {server_name}: {e}")
            return False
    
    async def execute_tool(self, request: MCPRequest) -> MCPResponse:
        """
        Execute a tool on the specified MCP server.
        
        Args:
            request: MCP request containing server, tool, and arguments.
        
        Returns:
            MCPResponse: Tool execution result.
        """
        if not self.is_initialized:
            return MCPResponse(
                success=False,
                error="MCP Client not initialized",
                execution_time=0.0,
                request_id=request.request_id
            )
        
        start_time = datetime.now()
        
        try:
            # Check if server exists
            if request.server_name not in self.servers:
                return MCPResponse(
                    success=False,
                    error=f"Server '{request.server_name}' not found",
                    execution_time=0.0,
                    request_id=request.request_id
                )
            
            server = self.servers[request.server_name]
            
            # Execute tool on server
            result = await server.execute_tool(request.tool_name, request.args)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return MCPResponse(
                success=True,
                result=result,
                execution_time=execution_time,
                request_id=request.request_id
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"MCP tool execution failed: {e}")
            
            return MCPResponse(
                success=False,
                error=str(e),
                execution_time=execution_time,
                request_id=request.request_id
            )
    
    async def deepl_translate(
        self,
        text: str,
        target_lang: str = "EN",
        source_lang: str = "auto"
    ) -> MCPResponse:
        """
        Translate text using DeepL.
        
        Args:
            text: Text to translate.
            target_lang: Target language code (e.g., 'EN', 'JA').
            source_lang: Source language code ('auto' for detection).
        
        Returns:
            MCPResponse: Translation result.
        """
        request = MCPRequest(
            server_name="deepl",
            tool_name="translate",
            args={
                "text": text,
                "target_lang": target_lang,
                "source_lang": source_lang
            }
        )
        
        return await self.execute_tool(request)
    
    async def deepl_detect_language(self, text: str) -> MCPResponse:
        """
        Detect language of given text using DeepL.
        
        Args:
            text: Text to analyze.
        
        Returns:
            MCPResponse: Language detection result.
        """
        request = MCPRequest(
            server_name="deepl",
            tool_name="detect_language",
            args={"text": text}
        )
        
        return await self.execute_tool(request)
    
    async def deepl_get_languages(self) -> MCPResponse:
        """
        Get supported languages from DeepL.
        
        Returns:
            MCPResponse: Supported languages list.
        """
        request = MCPRequest(
            server_name="deepl",
            tool_name="get_languages",
            args={}
        )
        
        return await self.execute_tool(request)
    
    async def sequential_thinking(self,
                                  thought: str,
                                  thought_number: int = 1,
                                  total_thoughts: int = 5,
                                  next_thought_needed: bool = True
                                  ) -> MCPResponse:
        """
        Execute sequential thinking process.
        
        Args:
            thought: Current thinking step.
            thought_number: Current thought number.
            total_thoughts: Estimated total thoughts needed.
            next_thought_needed: Whether another thought step is needed.
        
        Returns:
            MCPResponse: Thinking process result.
        """
        request = MCPRequest(
            server_name="sequential_thinking",
            tool_name="sequentialthinking",
            args={
                "thought": thought,
                "thoughtNumber": thought_number,
                "totalThoughts": total_thoughts,
                "nextThoughtNeeded": next_thought_needed
            }
        )
        
        return await self.execute_tool(request)

    async def brave_search(self, query: str, count: int = 10) -> MCPResponse:
        """
        Execute web search using Brave Search.
        
        Args:
            query: Search query.
            count: Number of results to return.
        
        Returns:
            MCPResponse: Search results.
        """
        request = MCPRequest(
            server_name="brave_search",
            tool_name="brave_web_search",
            args={
                "query": query,
                "count": count
            }
        )
        
        return await self.execute_tool(request)

    async def github_search(self, query: str, per_page: int = 30
                            ) -> MCPResponse:
        """
        Search GitHub repositories.
        
        Args:
            query: Search query.
            per_page: Number of results per page.
        
        Returns:
            MCPResponse: Search results.
        """
        request = MCPRequest(
            server_name="github",
            tool_name="search_repositories",
            args={
                "query": query,
                "perPage": per_page
            }
        )
        
        return await self.execute_tool(request)
    
    async def ref_search(self, query: str) -> MCPResponse:
        """
        Search documentation using Ref.
        
        Args:
            query: Documentation search query.
        
        Returns:
            MCPResponse: Documentation search results.
        """
        request = MCPRequest(
            server_name="ref",
            tool_name="ref_search_documentation",
            args={
                "query": query
            }
        )
        
        return await self.execute_tool(request)
    
    def get_available_servers(self) -> List[str]:
        """
        Get list of available MCP servers.
        
        Returns:
            List[str]: Available server names.
        """
        return list(self.servers.keys())
    
    async def shutdown(self) -> bool:
        """
        Shutdown the MCP client and cleanup resources.
        
        Returns:
            bool: True if shutdown successful.
        """
        try:
            logger.info("Shutting down MCP Client...")
            
            # Shutdown all servers
            for server_name, server in self.servers.items():
                if hasattr(server, 'shutdown'):
                    await server.shutdown()
            
            self.servers.clear()
            self.is_initialized = False
            
            logger.info("MCP Client shutdown complete")
            return True
            
        except Exception as e:
            logger.error(f"Error during MCP Client shutdown: {e}")
            return False