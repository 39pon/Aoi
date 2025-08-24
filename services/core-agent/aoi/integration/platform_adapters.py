"""プラットフォーム固有のアダプターシステム

ブラウザ、Obsidian、Raycast等の各プラットフォームとの
統合を管理するアダプターの実装
"""

import asyncio
import json
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from pathlib import Path
import aiofiles
import aiohttp
from urllib.parse import urljoin

from .cross_platform_system import (
    PlatformType, DataType
)


@dataclass
class AdapterConfig:
    """アダプター設定"""
    platform_type: PlatformType
    connection_params: Dict[str, Any]
    sync_capabilities: List[str]
    auth_config: Optional[Dict[str, str]] = None
    custom_settings: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.custom_settings is None:
            self.custom_settings = {}


class BasePlatformAdapter(ABC):
    """プラットフォームアダプターの基底クラス"""

    def __init__(self, config: AdapterConfig):
        self.config = config
        self.platform_id: Optional[str] = None
        self.is_connected = False
        self.last_sync = datetime.now()
        self._event_handlers: Dict[str, List[Callable]] = {}

    @abstractmethod
    async def connect(self) -> bool:
        """プラットフォームに接続"""
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """プラットフォームから切断"""
        pass

    @abstractmethod
    async def sync_data(
        self, 
        data_type: DataType, 
        data: Dict[str, Any]
    ) -> bool:
        """データを同期"""
        pass

    @abstractmethod
    async def get_data(
        self, 
        data_type: DataType, 
        data_id: str
    ) -> Optional[Dict[str, Any]]:
        """データを取得"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """ヘルスチェック"""
        pass

    def add_event_handler(self, event_type: str, handler: Callable) -> None:
        """イベントハンドラーを追加"""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)

    async def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """イベントを発火"""
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception:
                    # イベントハンドラーのエラーは無視
                    pass


class BrowserAdapter(BasePlatformAdapter):
    """ブラウザ統合アダプター"""

    def __init__(self, config: AdapterConfig):
        super().__init__(config)
        self.websocket_url = config.connection_params.get(
            "websocket_url", "ws://localhost:8080/ws"
        )
        self.api_base_url = config.connection_params.get(
            "api_base_url", "http://localhost:8080/api"
        )
        self.extension_id = config.connection_params.get("extension_id")
        self._websocket = None
        self._session = None

    async def connect(self) -> bool:
        """ブラウザ拡張機能に接続"""
        try:
            # HTTP セッションを作成
            self._session = aiohttp.ClientSession()
            
            # ヘルスチェック
            if not await self.health_check():
                return False
            
            # WebSocket接続を確立
            self._websocket = await self._session.ws_connect(
                self.websocket_url
            )
            
            self.is_connected = True
            await self._emit_event("browser_connected", {
                "platform_id": self.platform_id,
                "extension_id": self.extension_id
            })
            
            # メッセージ受信ループを開始
            asyncio.create_task(self._message_loop())
            
            return True
            
        except Exception as e:
            await self._emit_event("browser_connection_error", {
                "error": str(e)
            })
            return False

    async def disconnect(self) -> bool:
        """ブラウザ拡張機能から切断"""
        try:
            if self._websocket:
                await self._websocket.close()
                self._websocket = None
            
            if self._session:
                await self._session.close()
                self._session = None
            
            self.is_connected = False
            await self._emit_event("browser_disconnected", {
                "platform_id": self.platform_id
            })
            
            return True
            
        except Exception:
            return False

    async def sync_data(
        self, 
        data_type: DataType, 
        data: Dict[str, Any]
    ) -> bool:
        """ブラウザにデータを同期"""
        if not self.is_connected or not self._session:
            return False
        
        try:
            # データタイプに応じた同期処理
            if data_type == DataType.PERSONALITY:
                return await self._sync_personality(data)
            elif data_type == DataType.MEMORY:
                return await self._sync_memory(data)
            elif data_type == DataType.CONVERSATION:
                return await self._sync_conversation(data)
            elif data_type == DataType.PREFERENCES:
                return await self._sync_preferences(data)
            else:
                return await self._sync_generic_data(data_type, data)
                
        except Exception as e:
            await self._emit_event("browser_sync_error", {
                "data_type": data_type.value,
                "error": str(e)
            })
            return False

    async def get_data(
        self, 
        data_type: DataType, 
        data_id: str
    ) -> Optional[Dict[str, Any]]:
        """ブラウザからデータを取得"""
        if not self.is_connected or not self._session:
            return None
        
        try:
            url = urljoin(self.api_base_url, f"data/{data_type.value}/{data_id}")
            async with self._session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return None
                
        except Exception:
            return None

    async def health_check(self) -> bool:
        """ブラウザ拡張機能のヘルスチェック"""
        if not self._session:
            return False
        
        try:
            url = urljoin(self.api_base_url, "health")
            timeout = aiohttp.ClientTimeout(total=5)
            async with self._session.get(url, timeout=timeout) as response:
                return response.status == 200
                
        except Exception:
            return False

    async def _message_loop(self) -> None:
        """WebSocketメッセージ受信ループ"""
        if not self._websocket:
            return
        
        try:
            async for msg in self._websocket:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self._handle_message(data)
                    except json.JSONDecodeError:
                        continue
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break
                    
        except Exception as e:
            await self._emit_event("browser_message_error", {
                "error": str(e)
            })
        finally:
            self.is_connected = False

    async def _handle_message(self, message: Dict[str, Any]) -> None:
        """WebSocketメッセージを処理"""
        msg_type = message.get("type")
        
        if msg_type == "data_update":
            await self._emit_event("browser_data_updated", message)
        elif msg_type == "user_action":
            await self._emit_event("browser_user_action", message)
        elif msg_type == "error":
            await self._emit_event("browser_error", message)

    async def _sync_personality(self, data: Dict[str, Any]) -> bool:
        """人格データを同期"""
        url = urljoin(self.api_base_url, "personality")
        async with self._session.post(url, json=data) as response:
            return response.status == 200

    async def _sync_memory(self, data: Dict[str, Any]) -> bool:
        """記憶データを同期"""
        url = urljoin(self.api_base_url, "memory")
        async with self._session.post(url, json=data) as response:
            return response.status == 200

    async def _sync_conversation(self, data: Dict[str, Any]) -> bool:
        """会話データを同期"""
        url = urljoin(self.api_base_url, "conversation")
        async with self._session.post(url, json=data) as response:
            return response.status == 200

    async def _sync_preferences(self, data: Dict[str, Any]) -> bool:
        """設定データを同期"""
        url = urljoin(self.api_base_url, "preferences")
        async with self._session.post(url, json=data) as response:
            return response.status == 200

    async def _sync_generic_data(
        self, 
        data_type: DataType, 
        data: Dict[str, Any]
    ) -> bool:
        """汎用データを同期"""
        url = urljoin(self.api_base_url, f"data/{data_type.value}")
        async with self._session.post(url, json=data) as response:
            return response.status == 200


class ObsidianAdapter(BasePlatformAdapter):
    """Obsidian統合アダプター"""

    def __init__(self, config: AdapterConfig):
        super().__init__(config)
        self.vault_path = Path(
            config.connection_params.get("vault_path", "~/Documents/Obsidian")
        ).expanduser()
        self.plugin_port = config.connection_params.get("plugin_port", 8081)
        self.api_base_url = f"http://localhost:{self.plugin_port}/api"
        self._session = None

    async def connect(self) -> bool:
        """Obsidianプラグインに接続"""
        try:
            self._session = aiohttp.ClientSession()
            
            # プラグインのヘルスチェック
            if not await self.health_check():
                # プラグインが起動していない場合はファイルベースで動作
                await self._emit_event("obsidian_plugin_unavailable", {
                    "fallback_mode": "file_based"
                })
            
            self.is_connected = True
            await self._emit_event("obsidian_connected", {
                "platform_id": self.platform_id,
                "vault_path": str(self.vault_path)
            })
            
            return True
            
        except Exception as e:
            await self._emit_event("obsidian_connection_error", {
                "error": str(e)
            })
            return False

    async def disconnect(self) -> bool:
        """Obsidianプラグインから切断"""
        try:
            if self._session:
                await self._session.close()
                self._session = None
            
            self.is_connected = False
            await self._emit_event("obsidian_disconnected", {
                "platform_id": self.platform_id
            })
            
            return True
            
        except Exception:
            return False

    async def sync_data(
        self, 
        data_type: DataType, 
        data: Dict[str, Any]
    ) -> bool:
        """Obsidianにデータを同期"""
        if not self.is_connected:
            return False
        
        try:
            # プラグイン経由での同期を試行
            if self._session and await self.health_check():
                return await self._sync_via_plugin(data_type, data)
            else:
                # ファイルベースでの同期にフォールバック
                return await self._sync_via_files(data_type, data)
                
        except Exception as e:
            await self._emit_event("obsidian_sync_error", {
                "data_type": data_type.value,
                "error": str(e)
            })
            return False

    async def get_data(
        self, 
        data_type: DataType, 
        data_id: str
    ) -> Optional[Dict[str, Any]]:
        """Obsidianからデータを取得"""
        if not self.is_connected:
            return None
        
        try:
            # プラグイン経由での取得を試行
            if self._session and await self.health_check():
                return await self._get_via_plugin(data_type, data_id)
            else:
                # ファイルベースでの取得にフォールバック
                return await self._get_via_files(data_type, data_id)
                
        except Exception:
            return None

    async def health_check(self) -> bool:
        """Obsidianプラグインのヘルスチェック"""
        if not self._session:
            return False
        
        try:
            url = f"{self.api_base_url}/health"
            async with self._session.get(
                url, timeout=aiohttp.ClientTimeout(total=3)
            ) as response:
                return response.status == 200
                
        except Exception:
            return False

    async def _sync_via_plugin(
        self, 
        data_type: DataType, 
        data: Dict[str, Any]
    ) -> bool:
        """プラグイン経由でデータを同期"""
        url = f"{self.api_base_url}/sync/{data_type.value}"
        async with self._session.post(url, json=data) as response:
            return response.status == 200

    async def _sync_via_files(
        self, 
        data_type: DataType, 
        data: Dict[str, Any]
    ) -> bool:
        """ファイル経由でデータを同期"""
        # データタイプに応じたディレクトリを作成
        sync_dir = self.vault_path / ".aoi" / data_type.value
        sync_dir.mkdir(parents=True, exist_ok=True)
        
        # データをMarkdownファイルとして保存
        if data_type == DataType.MEMORY:
            return await self._save_memory_as_markdown(sync_dir, data)
        elif data_type == DataType.CONVERSATION:
            return await self._save_conversation_as_markdown(sync_dir, data)
        else:
            return await self._save_generic_data(sync_dir, data)

    async def _get_via_plugin(
        self, 
        data_type: DataType, 
        data_id: str
    ) -> Optional[Dict[str, Any]]:
        """プラグイン経由でデータを取得"""
        url = f"{self.api_base_url}/data/{data_type.value}/{data_id}"
        async with self._session.get(url) as response:
            if response.status == 200:
                return await response.json()
            return None

    async def _get_via_files(
        self, 
        data_type: DataType, 
        data_id: str
    ) -> Optional[Dict[str, Any]]:
        """ファイル経由でデータを取得"""
        sync_dir = self.vault_path / ".aoi" / data_type.value
        file_path = sync_dir / f"{data_id}.json"
        
        if not file_path.exists():
            return None
        
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except Exception:
            return None

    async def _save_memory_as_markdown(
        self, 
        sync_dir: Path, 
        data: Dict[str, Any]
    ) -> bool:
        """記憶データをMarkdownとして保存"""
        try:
            memory_id = data.get("id", str(uuid.uuid4()))
            title = data.get("title", "Untitled Memory")
            content = data.get("content", "")
            tags = data.get("tags", [])
            timestamp = data.get("timestamp", datetime.now().isoformat())
            
            markdown_content = f"""# {title}

**Created:** {timestamp}
**Tags:** {', '.join(tags)}
**ID:** {memory_id}

---

{content}
"""
            
            file_path = sync_dir / f"{memory_id}.md"
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(markdown_content)
            
            # JSONメタデータも保存
            json_path = sync_dir / f"{memory_id}.json"
            async with aiofiles.open(json_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
            
            return True
            
        except Exception:
            return False

    async def _save_conversation_as_markdown(
        self, 
        sync_dir: Path, 
        data: Dict[str, Any]
    ) -> bool:
        """会話データをMarkdownとして保存"""
        try:
            conversation_id = data.get("id", str(uuid.uuid4()))
            title = data.get("title", "Conversation")
            messages = data.get("messages", [])
            timestamp = data.get("timestamp", datetime.now().isoformat())
            
            markdown_content = f"""# {title}

**Date:** {timestamp}
**ID:** {conversation_id}

---

"""
            
            for msg in messages:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                msg_time = msg.get("timestamp", "")
                
                markdown_content += f"""## {role.title()}
*{msg_time}*

{content}

---

"""
            
            file_path = sync_dir / f"{conversation_id}.md"
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(markdown_content)
            
            # JSONメタデータも保存
            json_path = sync_dir / f"{conversation_id}.json"
            async with aiofiles.open(json_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
            
            return True
            
        except Exception:
            return False

    async def _save_generic_data(
        self, 
        sync_dir: Path, 
        data: Dict[str, Any]
    ) -> bool:
        """汎用データを保存"""
        try:
            data_id = data.get("id", str(uuid.uuid4()))
            file_path = sync_dir / f"{data_id}.json"
            
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
            
            return True
            
        except Exception:
            return False


class RaycastAdapter(BasePlatformAdapter):
    """Raycast統合アダプター"""

    def __init__(self, config: AdapterConfig):
        super().__init__(config)
        self.extension_path = Path(
            config.connection_params.get(
                "extension_path", 
                "~/Library/Application Support/com.raycast.macos/extensions"
            )
        ).expanduser()
        self.api_port = config.connection_params.get("api_port", 8082)
        self.api_base_url = f"http://localhost:{self.api_port}/api"
        self._session = None

    async def connect(self) -> bool:
        """Raycast拡張機能に接続"""
        try:
            self._session = aiohttp.ClientSession()
            
            # 拡張機能のヘルスチェック
            if not await self.health_check():
                # 拡張機能が起動していない場合はファイルベースで動作
                await self._emit_event("raycast_extension_unavailable", {
                    "fallback_mode": "file_based"
                })
            
            self.is_connected = True
            await self._emit_event("raycast_connected", {
                "platform_id": self.platform_id,
                "extension_path": str(self.extension_path)
            })
            
            return True
            
        except Exception as e:
            await self._emit_event("raycast_connection_error", {
                "error": str(e)
            })
            return False

    async def disconnect(self) -> bool:
        """Raycast拡張機能から切断"""
        try:
            if self._session:
                await self._session.close()
                self._session = None
            
            self.is_connected = False
            await self._emit_event("raycast_disconnected", {
                "platform_id": self.platform_id
            })
            
            return True
            
        except Exception:
            return False

    async def sync_data(
        self, 
        data_type: DataType, 
        data: Dict[str, Any]
    ) -> bool:
        """Raycastにデータを同期"""
        if not self.is_connected:
            return False
        
        try:
            # 拡張機能経由での同期を試行
            if self._session and await self.health_check():
                return await self._sync_via_extension(data_type, data)
            else:
                # ファイルベースでの同期にフォールバック
                return await self._sync_via_files(data_type, data)
                
        except Exception as e:
            await self._emit_event("raycast_sync_error", {
                "data_type": data_type.value,
                "error": str(e)
            })
            return False

    async def get_data(
        self, 
        data_type: DataType, 
        data_id: str
    ) -> Optional[Dict[str, Any]]:
        """Raycastからデータを取得"""
        if not self.is_connected:
            return None
        
        try:
            # 拡張機能経由での取得を試行
            if self._session and await self.health_check():
                return await self._get_via_extension(data_type, data_id)
            else:
                # ファイルベースでの取得にフォールバック
                return await self._get_via_files(data_type, data_id)
                
        except Exception:
            return None

    async def health_check(self) -> bool:
        """Raycast拡張機能のヘルスチェック"""
        if not self._session:
            return False
        
        try:
            url = f"{self.api_base_url}/health"
            async with self._session.get(
                url, timeout=aiohttp.ClientTimeout(total=3)
            ) as response:
                return response.status == 200
                
        except Exception:
            return False

    async def _sync_via_extension(
        self, 
        data_type: DataType, 
        data: Dict[str, Any]
    ) -> bool:
        """拡張機能経由でデータを同期"""
        url = f"{self.api_base_url}/sync/{data_type.value}"
        async with self._session.post(url, json=data) as response:
            return response.status == 200

    async def _sync_via_files(
        self, 
        data_type: DataType, 
        data: Dict[str, Any]
    ) -> bool:
        """ファイル経由でデータを同期"""
        # Raycast拡張機能のデータディレクトリ
        sync_dir = self.extension_path / "aoi-integration" / data_type.value
        sync_dir.mkdir(parents=True, exist_ok=True)
        
        data_id = data.get("id", str(uuid.uuid4()))
        file_path = sync_dir / f"{data_id}.json"
        
        try:
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
            return True
        except Exception:
            return False

    async def _get_via_extension(
        self, 
        data_type: DataType, 
        data_id: str
    ) -> Optional[Dict[str, Any]]:
        """拡張機能経由でデータを取得"""
        url = f"{self.api_base_url}/data/{data_type.value}/{data_id}"
        async with self._session.get(url) as response:
            if response.status == 200:
                return await response.json()
            return None

    async def _get_via_files(
        self, 
        data_type: DataType, 
        data_id: str
    ) -> Optional[Dict[str, Any]]:
        """ファイル経由でデータを取得"""
        sync_dir = self.extension_path / "aoi-integration" / data_type.value
        file_path = sync_dir / f"{data_id}.json"
        
        if not file_path.exists():
            return None
        
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except Exception:
            return None


class AdapterManager:
    """アダプター管理システム"""

    def __init__(self):
        self.adapters: Dict[str, BasePlatformAdapter] = {}
        self.adapter_configs: Dict[PlatformType, AdapterConfig] = {}
        self._event_handlers: Dict[str, List[Callable]] = {}

    def register_adapter_config(
        self, 
        platform_type: PlatformType, 
        config: AdapterConfig
    ) -> None:
        """アダプター設定を登録"""
        self.adapter_configs[platform_type] = config

    async def create_adapter(
        self, 
        platform_type: PlatformType, 
        platform_id: str
    ) -> Optional[BasePlatformAdapter]:
        """アダプターを作成"""
        if platform_type not in self.adapter_configs:
            return None
        
        config = self.adapter_configs[platform_type]
        
        # プラットフォームタイプに応じたアダプターを作成
        if platform_type == PlatformType.BROWSER:
            adapter = BrowserAdapter(config)
        elif platform_type == PlatformType.OBSIDIAN:
            adapter = ObsidianAdapter(config)
        elif platform_type == PlatformType.RAYCAST:
            adapter = RaycastAdapter(config)
        else:
            return None
        
        adapter.platform_id = platform_id
        
        # イベントハンドラーを設定
        for event_type, handlers in self._event_handlers.items():
            for handler in handlers:
                adapter.add_event_handler(event_type, handler)
        
        # 接続を試行
        if await adapter.connect():
            self.adapters[platform_id] = adapter
            return adapter
        
        return None

    async def remove_adapter(self, platform_id: str) -> bool:
        """アダプターを削除"""
        if platform_id in self.adapters:
            adapter = self.adapters[platform_id]
            await adapter.disconnect()
            del self.adapters[platform_id]
            return True
        return False

    def get_adapter(self, platform_id: str) -> Optional[BasePlatformAdapter]:
        """アダプターを取得"""
        return self.adapters.get(platform_id)

    async def sync_to_all(
        self, 
        data_type: DataType, 
        data: Dict[str, Any], 
        exclude_platforms: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """全アダプターにデータを同期"""
        exclude_platforms = exclude_platforms or []
        results = {}
        
        for platform_id, adapter in self.adapters.items():
            if platform_id in exclude_platforms:
                continue
            
            try:
                success = await adapter.sync_data(data_type, data)
                results[platform_id] = success
            except Exception:
                results[platform_id] = False
        
        return results

    async def health_check_all(self) -> Dict[str, bool]:
        """全アダプターのヘルスチェック"""
        results = {}
        
        for platform_id, adapter in self.adapters.items():
            try:
                is_healthy = await adapter.health_check()
                results[platform_id] = is_healthy
            except Exception:
                results[platform_id] = False
        
        return results

    def add_event_handler(self, event_type: str, handler: Callable) -> None:
        """イベントハンドラーを追加"""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
        
        # 既存のアダプターにもハンドラーを追加
        for adapter in self.adapters.values():
            adapter.add_event_handler(event_type, handler)

    async def get_status(self) -> Dict[str, Any]:
        """アダプター管理システムのステータスを取得"""
        adapter_status = {}
        
        for platform_id, adapter in self.adapters.items():
            adapter_status[platform_id] = {
                "platform_type": adapter.config.platform_type.value,
                "is_connected": adapter.is_connected,
                "last_sync": adapter.last_sync.isoformat(),
                "capabilities": adapter.config.sync_capabilities
            }
        
        return {
            "total_adapters": len(self.adapters),
            "connected_adapters": sum(
                1 for a in self.adapters.values() if a.is_connected
            ),
            "registered_configs": len(self.adapter_configs),
            "adapters": adapter_status
        }