# =============================================================================
# Aoi Core Agent - Memory Management System
# =============================================================================

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..core.config import AoiConfig

try:
    import redis.asyncio as redis
except ImportError:
    redis = None

try:
    import weaviate
except ImportError:
    weaviate = None

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Memory management system for the Aoi agent.
    
    This class handles both short-term (Redis) and long-term (Weaviate) memory,
    providing conversation history, semantic search, and knowledge persistence.
    """
    
    def __init__(self, config: AoiConfig):
        """
        Initialize the Memory Manager.
        
        Args:
            config: Configuration object containing database settings.
        """
        self.config = config
        
        # Database connections
        self.redis_client: Optional[redis.Redis] = None
        self.weaviate_client: Optional[weaviate.WeaviateClient] = None
        
        # Memory collections
        self.conversation_collection = "AoiConversations"
        self.knowledge_collection = "AoiKnowledge"
        
        # State
        self.is_initialized = False
        
        logger.info("Memory Manager initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize database connections and create necessary collections.
        
        Returns:
            bool: True if initialization successful.
        """
        try:
            logger.info("Initializing Memory Manager...")
            
            # Initialize Redis connection
            await self._initialize_redis()
            
            # Initialize Weaviate connection
            await self._initialize_weaviate()
            
            self.is_initialized = True
            logger.success("Memory Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Memory Manager: {e}")
            return False
    
    async def _initialize_redis(self) -> None:
        """
        Initialize Redis connection for session storage.
        """
        try:
            self.redis_client = redis.from_url(
                self.config.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.success("Redis connection established")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def _initialize_weaviate(self) -> None:
        """
        Initialize Weaviate connection for vector storage.
        """
        try:
            # Create Weaviate client
            self.weaviate_client = weaviate.connect_to_local(
                host=self.config.weaviate_host,
                port=self.config.weaviate_port,
                grpc_port=self.config.weaviate_grpc_port
            )
            
            # Test connection
            if self.weaviate_client.is_ready():
                logger.success("Weaviate connection established")
                
                # Create collections if they don't exist
                await self._create_weaviate_collections()
            else:
                raise Exception("Weaviate is not ready")
                
        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {e}")
            raise
    
    async def _create_weaviate_collections(self) -> None:
        """
        Create necessary Weaviate collections for memory storage.
        """
        try:
            collections = self.weaviate_client.collections
            
            # Create conversation collection
            if not collections.exists(self.conversation_collection):
                collections.create(
                    name=self.conversation_collection,
                    properties=[
                        weaviate.classes.config.Property(
                            name="session_id",
                            data_type=weaviate.classes.config.DataType.TEXT
                        ),
                        weaviate.classes.config.Property(
                            name="role",
                            data_type=weaviate.classes.config.DataType.TEXT
                        ),
                        weaviate.classes.config.Property(
                            name="content",
                            data_type=weaviate.classes.config.DataType.TEXT
                        ),
                        weaviate.classes.config.Property(
                            name="timestamp",
                            data_type=weaviate.classes.config.DataType.DATE
                        ),
                        weaviate.classes.config.Property(
                            name="metadata",
                            data_type=weaviate.classes.config.DataType.TEXT
                        )
                    ]
                )
                logger.info(f"Created collection: {self.conversation_collection}")
            
            # Create knowledge collection
            if not collections.exists(self.knowledge_collection):
                collections.create(
                    name=self.knowledge_collection,
                    properties=[
                        weaviate.classes.config.Property(
                            name="title",
                            data_type=weaviate.classes.config.DataType.TEXT
                        ),
                        weaviate.classes.config.Property(
                            name="content",
                            data_type=weaviate.classes.config.DataType.TEXT
                        ),
                        weaviate.classes.config.Property(
                            name="source",
                            data_type=weaviate.classes.config.DataType.TEXT
                        ),
                        weaviate.classes.config.Property(
                            name="tags",
                            data_type=weaviate.classes.config.DataType.TEXT_ARRAY
                        ),
                        weaviate.classes.config.Property(
                            name="created_at",
                            data_type=weaviate.classes.config.DataType.DATE
                        )
                    ]
                )
                logger.info(f"Created collection: {self.knowledge_collection}")
                
        except Exception as e:
            logger.warning(f"Error creating Weaviate collections: {e}")
    
    async def create_session(self, session_id: str, user_id: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create a new conversation session.
        
        Args:
            session_id: Unique session identifier.
            user_id: User identifier.
            context: Optional session context.
        
        Returns:
            bool: True if session created successfully.
        """
        if not self.redis_client:
            return False
        
        try:
            session_data = {
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "context": context or {},
                "message_count": 0
            }
            
            await self.redis_client.hset(
                f"session:{session_id}",
                mapping={k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) for k, v in session_data.items()}
            )
            
            # Set session expiration (24 hours)
            await self.redis_client.expire(f"session:{session_id}", 86400)
            
            logger.info(f"Session created: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create session {session_id}: {e}")
            return False
    
    async def store_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Store a message in both short-term and long-term memory.
        
        Args:
            session_id: Session identifier.
            role: Message role (user/assistant).
            content: Message content.
            metadata: Optional message metadata.
        
        Returns:
            bool: True if message stored successfully.
        """
        try:
            timestamp = datetime.now()
            
            # Store in Redis for quick access
            await self._store_message_redis(session_id, role, content, timestamp, metadata)
            
            # Store in Weaviate for semantic search
            await self._store_message_weaviate(session_id, role, content, timestamp, metadata)
            
            # Update session message count
            if self.redis_client:
                await self.redis_client.hincrby(f"session:{session_id}", "message_count", 1)
            
            logger.debug(f"Message stored for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store message: {e}")
            return False
    
    async def _store_message_redis(self, session_id: str, role: str, content: str, timestamp: datetime, metadata: Optional[Dict[str, Any]]) -> None:
        """
        Store message in Redis for quick retrieval.
        """
        if not self.redis_client:
            return
        
        message_data = {
            "role": role,
            "content": content,
            "timestamp": timestamp.isoformat(),
            "metadata": json.dumps(metadata or {})
        }
        
        # Store in session message list
        await self.redis_client.lpush(
            f"messages:{session_id}",
            json.dumps(message_data)
        )
        
        # Keep only recent messages (limit to 100)
        await self.redis_client.ltrim(f"messages:{session_id}", 0, 99)
    
    async def _store_message_weaviate(self, session_id: str, role: str, content: str, timestamp: datetime, metadata: Optional[Dict[str, Any]]) -> None:
        """
        Store message in Weaviate for semantic search.
        """
        if not self.weaviate_client:
            return
        
        try:
            collection = self.weaviate_client.collections.get(self.conversation_collection)
            
            collection.data.insert(
                properties={
                    "session_id": session_id,
                    "role": role,
                    "content": content,
                    "timestamp": timestamp,
                    "metadata": json.dumps(metadata or {})
                }
            )
            
        except Exception as e:
            logger.warning(f"Failed to store message in Weaviate: {e}")
    
    async def get_recent_messages(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent messages from a session.
        
        Args:
            session_id: Session identifier.
            limit: Maximum number of messages to retrieve.
        
        Returns:
            List of recent messages.
        """
        if not self.redis_client:
            return []
        
        try:
            messages = await self.redis_client.lrange(f"messages:{session_id}", 0, limit - 1)
            return [json.loads(msg) for msg in messages]
            
        except Exception as e:
            logger.error(f"Failed to get recent messages: {e}")
            return []
    
    async def search_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant memories using semantic similarity.
        
        Args:
            query: Search query.
            limit: Maximum number of results.
        
        Returns:
            List of relevant memories.
        """
        if not self.weaviate_client:
            return []
        
        try:
            collection = self.weaviate_client.collections.get(self.conversation_collection)
            
            response = collection.query.near_text(
                query=query,
                limit=limit,
                return_metadata=["score"]
            )
            
            results = []
            for obj in response.objects:
                results.append({
                    "content": obj.properties.get("content", ""),
                    "role": obj.properties.get("role", ""),
                    "session_id": obj.properties.get("session_id", ""),
                    "timestamp": obj.properties.get("timestamp", ""),
                    "score": obj.metadata.score if obj.metadata else 0.0
                })
            
            return results
            
        except Exception as e:
            logger.warning(f"Failed to search memories: {e}")
            return []
    
    async def close_session(self, session_id: str) -> bool:
        """
        Close a conversation session.
        
        Args:
            session_id: Session identifier.
        
        Returns:
            bool: True if session closed successfully.
        """
        if not self.redis_client:
            return False
        
        try:
            # Update session end time
            await self.redis_client.hset(
                f"session:{session_id}",
                "ended_at",
                datetime.now().isoformat()
            )
            
            logger.info(f"Session closed: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to close session {session_id}: {e}")
            return False
    
    async def shutdown(self) -> bool:
        """
        Shutdown the memory manager and close connections.
        
        Returns:
            bool: True if shutdown successful.
        """
        try:
            logger.info("Shutting down Memory Manager...")
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            # Close Weaviate connection
            if self.weaviate_client:
                self.weaviate_client.close()
            
            self.is_initialized = False
            logger.success("Memory Manager shutdown completed")
            return True
            
        except Exception as e:
            logger.error(f"Error during Memory Manager shutdown: {e}")
            return False