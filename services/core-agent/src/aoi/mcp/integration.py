# =============================================================================
# Aoi Core Agent - MCP Integration Module
# =============================================================================

from typing import Dict, Any, Optional, List
import logging

from .client import MCPClient, MCPRequest
from .servers import (
    SequentialThinkingServer,
    BraveSearchServer,
    GitHubServer,
    RefServer,
    DeepLServer
)

# Use standard logging instead of loguru for compatibility
logger = logging.getLogger(__name__)


class MCPIntegration:
    """
    Main integration class for MCP servers in Aoi Core Agent.
    
    This class manages the lifecycle and coordination of all MCP servers,
    providing a unified interface for the Aoi agent to interact with
    external capabilities.
    """
    
    def __init__(self):
        """
        Initialize MCP integration.
        """
        self.client: Optional[MCPClient] = None
        self.servers: Dict[str, Any] = {}
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize all MCP servers and client.
        
        Returns:
            bool: True if initialization successful.
        """
        try:
            logger.info("Initializing MCP integration...")
            
            # Initialize MCP client
            self.client = MCPClient()
            
            # Initialize and register MCP servers
            await self._initialize_servers()
            
            # Initialize the MCP client
            client_init_success = await self.client.initialize()
            if not client_init_success:
                raise RuntimeError("Failed to initialize MCP client")
            
            # Register servers with client
            await self._register_servers()
            
            self.is_initialized = True
            logger.info("MCP integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP integration: {e}")
            return False
    
    async def _initialize_servers(self) -> None:
        """
        Initialize all MCP servers.
        """
        # Initialize Sequential Thinking Server
        self.servers["sequential_thinking"] = SequentialThinkingServer()
        logger.debug("Sequential Thinking server initialized")
        
        # Initialize Brave Search Server
        self.servers["brave_search"] = BraveSearchServer()
        logger.debug("Brave Search server initialized")
        
        # Initialize GitHub Server
        self.servers["github"] = GitHubServer()
        logger.debug("GitHub server initialized")
        
        # Initialize Ref Server
        self.servers["ref"] = RefServer()
        logger.debug("Ref server initialized")
        
        # Initialize DeepL Server
        await self._initialize_deepl_server()
    
    async def _register_servers(self) -> None:
        """
        Register all servers with the MCP client.
        """
        if not self.client:
            raise RuntimeError("MCP client not initialized")
        
        for server_name, server in self.servers.items():
            await self.client.register_server(server_name, server)
            logger.debug(f"Registered {server_name} with MCP client")
    
    async def _initialize_deepl_server(self) -> None:
        """
        Initialize DeepL server with API credentials.
        """
        import os
        
        deepl_server = DeepLServer()
        
        # Get API key from environment
        api_key = os.getenv("DEEPL_API_KEY")
        api_url = os.getenv("DEEPL_API_URL", "https://api-free.deepl.com/v2")
        
        if api_key and api_key != "your-deepl-api-key-here":
            await deepl_server.initialize(api_key, api_url)
            logger.info("DeepL server initialized with API key")
        else:
            logger.warning(
                "DeepL API key not found or placeholder. "
                "Translation will use mock responses."
            )
            # Initialize with mock mode
            await deepl_server.initialize("mock-key", api_url)
        
        self.servers["deepl"] = deepl_server
        logger.debug("DeepL server initialized")
    
    async def execute_tool(
        self,
        server_name: str,
        tool_name: str,
        args: Dict[str, Any]
    ) -> Any:
        """
        Execute a tool on a specific MCP server.
        
        Args:
            server_name: Name of the MCP server.
            tool_name: Name of the tool to execute.
            args: Tool arguments.
        
        Returns:
            Tool execution result.
        
        Raises:
            RuntimeError: If MCP integration not initialized.
            ValueError: If server not found.
        """
        if not self.is_initialized or not self.client:
            raise RuntimeError("MCP integration not initialized")
        
        try:
            # Create MCPRequest object
            request = MCPRequest(
                server_name=server_name,
                tool_name=tool_name,
                args=args
            )
            
            result = await self.client.execute_tool(request)
            logger.debug(
                f"Executed {tool_name} on {server_name} successfully"
            )
            return result
            
        except Exception as e:
            logger.error(
                f"Failed to execute {tool_name} on {server_name}: {e}"
            )
            raise
    
    async def get_available_tools(self) -> Dict[str, List[str]]:
        """
        Get all available tools from all MCP servers.
        
        Returns:
            Dictionary mapping server names to their available tools.
        """
        if not self.is_initialized or not self.client:
            raise RuntimeError("MCP integration not initialized")
        
        tools = {}
        
        # Sequential Thinking tools
        tools["sequential_thinking"] = ["sequentialthinking"]
        
        # Brave Search tools
        tools["brave_search"] = ["brave_web_search", "brave_local_search"]
        
        # GitHub tools
        tools["github"] = [
            "search_repositories",
            "get_file_contents",
            "search_code"
        ]
        
        # Ref tools
        tools["ref"] = ["ref_search_documentation", "ref_read_url"]
        
        return tools
    
    async def enhance_response_with_thinking(
        self,
        user_query: str,
        initial_response: str
    ) -> Dict[str, Any]:
        """
        Enhance response using Sequential Thinking capabilities.
        
        Args:
            user_query: Original user query.
            initial_response: Initial AI response.
        
        Returns:
            Enhanced response with thinking process.
        """
        try:
            # Use Sequential Thinking to analyze the response
            thinking_result = await self.execute_tool(
                "sequential_thinking",
                "sequentialthinking",
                {
                    "thought": (
                        f"Analyzing user query: {user_query}\n"
                        f"Initial response: {initial_response}\n"
                        "How can this response be improved?"
                    ),
                    "thoughtNumber": 1,
                    "totalThoughts": 3,
                    "nextThoughtNeeded": True
                }
            )
            
            return {
                "original_response": initial_response,
                "thinking_analysis": thinking_result.get("analysis", ""),
                "suggestions": thinking_result.get("suggestions", []),
                "enhanced": True
            }
            
        except Exception as e:
            logger.error(f"Failed to enhance response with thinking: {e}")
            return {
                "original_response": initial_response,
                "enhanced": False,
                "error": str(e)
            }
    
    async def search_relevant_information(
        self,
        query: str,
        search_type: str = "web"
    ) -> Dict[str, Any]:
        """
        Search for relevant information to enhance responses.
        
        Args:
            query: Search query.
            search_type: Type of search ('web', 'code', 'docs').
        
        Returns:
            Search results.
        """
        try:
            if search_type == "web":
                return await self.execute_tool(
                    "brave_search",
                    "brave_web_search",
                    {"query": query, "count": 5}
                )
            elif search_type == "code":
                return await self.execute_tool(
                    "github",
                    "search_code",
                    {"q": query}
                )
            elif search_type == "docs":
                return await self.execute_tool(
                    "ref",
                    "ref_search_documentation",
                    {"query": query}
                )
            else:
                raise ValueError(f"Unknown search type: {search_type}")
                
        except Exception as e:
            logger.error(f"Failed to search information: {e}")
            return {"error": str(e), "results": []}
    
    async def shutdown(self) -> bool:
        """
        Shutdown MCP integration and all servers.
        
        Returns:
            bool: True if shutdown successful.
        """
        try:
            logger.info("Shutting down MCP integration...")
            
            # Shutdown all servers
            for server_name, server in self.servers.items():
                await server.shutdown()
                logger.debug(f"Shutdown {server_name} server")
            
            # Shutdown client
            if self.client:
                await self.client.shutdown()
                logger.debug("Shutdown MCP client")
            
            self.is_initialized = False
            self.servers.clear()
            self.client = None
            
            logger.info("MCP integration shutdown completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to shutdown MCP integration: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of MCP integration.
        
        Returns:
            Status information.
        """
        return {
            "initialized": self.is_initialized,
            "client_available": self.client is not None,
            "servers_count": len(self.servers),
            "available_servers": list(self.servers.keys())
        }