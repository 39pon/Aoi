"""クロスプラットフォーム統合システム

ブラウザ、Obsidian、Raycast間での同一人格・記憶共有を実現する
スケーラブルなシステム実装
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import aiofiles
import aiohttp
from cryptography.fernet import Fernet
import hashlib
import base64


class PlatformType(Enum):
    """サポートするプラットフォームタイプ"""
    BROWSER = "browser"
    OBSIDIAN = "obsidian"
    RAYCAST = "raycast"
    TRAE_IDE = "trae_ide"
    MOBILE_APP = "mobile_app"
    DESKTOP_APP = "desktop_app"
    API_CLIENT = "api_client"


class SyncStatus(Enum):
    """同期ステータス"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


class DataType(Enum):
    """同期データタイプ"""
    PERSONALITY = "personality"
    MEMORY = "memory"
    CONVERSATION = "conversation"
    PREFERENCES = "preferences"
    CONTEXT = "context"
    TASK_STATE = "task_state"
    EVIDENCE = "evidence"
    NOTE = "note"


@dataclass
class PlatformInfo:
    """プラットフォーム情報"""
    platform_id: str
    platform_type: PlatformType
    version: str
    capabilities: List[str]
    last_seen: datetime
    is_active: bool
    endpoint_url: Optional[str] = None
    auth_token: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SyncData:
    """同期データ"""
    data_id: str
    data_type: DataType
    content: Dict[str, Any]
    version: int
    timestamp: datetime
    source_platform: str
    checksum: str
    encryption_key: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SyncOperation:
    """同期操作"""
    operation_id: str
    data_id: str
    operation_type: str  # create, update, delete
    source_platform: str
    target_platforms: List[str]
    status: SyncStatus
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


class ConflictResolutionStrategy(Enum):
    """競合解決戦略"""
    LATEST_WINS = "latest_wins"
    SOURCE_PRIORITY = "source_priority"
    MANUAL_RESOLUTION = "manual_resolution"
    MERGE_STRATEGY = "merge_strategy"


class CrossPlatformSystem:
    """クロスプラットフォーム統合システム"""

    def __init__(self, config_path: str = "config/cross_platform.json"):
        self.config_path = Path(config_path)
        self.platforms: Dict[str, PlatformInfo] = {}
        self.sync_data_store: Dict[str, SyncData] = {}
        self.sync_operations: Dict[str, SyncOperation] = {}
        self.encryption_key = self._generate_encryption_key()
        self.conflict_strategy = ConflictResolutionStrategy.LATEST_WINS
        self.sync_interval = 30  # seconds
        self.is_running = False
        self._sync_task: Optional[asyncio.Task] = None
        self._event_handlers: Dict[str, List[Callable]] = {}
        # 設定管理システム
        from .integration_config import ConfigurationManager
        
        config_file = Path(config_path)
        # ファイルが存在する場合は削除してディレクトリとして作成
        if config_file.exists() and config_file.is_file():
            config_file.unlink()
        
        if config_file.suffix:  # ファイル拡張子がある場合はファイルパス
            config_dir = config_file.parent / config_file.stem
            # プラットフォーム設定ファイルのパスを設定
            self.config_path = config_dir / "platforms.json"
        else:  # 拡張子がない場合はディレクトリパス
            config_dir = config_file
            self.config_path = config_dir / "platforms.json"
        
        self.config_manager = ConfigurationManager(config_dir)

    def _generate_encryption_key(self) -> Fernet:
        """暗号化キーを生成"""
        key = Fernet.generate_key()
        return Fernet(key)

    def _calculate_data_checksum(self, data: Dict[str, Any]) -> str:
        """データのチェックサムを計算"""
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(data_str.encode()).hexdigest()

    async def register_platform(
        self,
        platform_type: PlatformType,
        version: str,
        capabilities: List[str],
        endpoint_url: Optional[str] = None,
        auth_token: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """プラットフォームを登録"""
        platform_id = str(uuid.uuid4())
        
        platform_info = PlatformInfo(
            platform_id=platform_id,
            platform_type=platform_type,
            version=version,
            capabilities=capabilities,
            last_seen=datetime.now(),
            is_active=True,
            endpoint_url=endpoint_url,
            auth_token=auth_token,
            metadata=metadata or {}
        )
        
        self.platforms[platform_id] = platform_info
        await self._save_platform_config()
        
        # プラットフォーム登録イベントを発火
        await self._emit_event("platform_registered", {
            "platform_id": platform_id,
            "platform_type": platform_type.value
        })
        
        return platform_id

    async def unregister_platform(self, platform_id: str) -> bool:
        """プラットフォームの登録を解除"""
        if platform_id in self.platforms:
            platform_info = self.platforms[platform_id]
            platform_info.is_active = False
            
            # プラットフォーム登録解除イベントを発火
            await self._emit_event("platform_unregistered", {
                "platform_id": platform_id,
                "platform_type": platform_info.platform_type.value
            })
            
            del self.platforms[platform_id]
            await self._save_platform_config()
            return True
        return False

    async def sync_data(
        self,
        data_type: DataType,
        content: Dict[str, Any],
        source_platform: str,
        target_platforms: Optional[List[str]] = None
    ) -> str:
        """データを同期"""
        data_id = str(uuid.uuid4())
        
        # データの暗号化
        encrypted_content = self._encrypt_data(content)
        checksum = self._calculate_data_checksum(content)
        
        sync_data = SyncData(
            data_id=data_id,
            data_type=data_type,
            content=encrypted_content,
            version=1,
            timestamp=datetime.now(),
            source_platform=source_platform,
            checksum=checksum
        )
        
        self.sync_data_store[data_id] = sync_data
        
        # 同期操作を作成
        if target_platforms is None:
            target_platforms = [
                pid for pid in self.platforms.keys() 
                if pid != source_platform and self.platforms[pid].is_active
            ]
        
        operation_id = await self._create_sync_operation(
            data_id, "create", source_platform, target_platforms
        )
        
        # 非同期で同期実行
        asyncio.create_task(self._execute_sync_operation(operation_id))
        
        return data_id

    async def get_data(
        self, 
        data_id: str, 
        platform_id: str
    ) -> Optional[Dict[str, Any]]:
        """データを取得"""
        if data_id not in self.sync_data_store:
            return None
        
        sync_data = self.sync_data_store[data_id]
        
        # プラットフォームのアクセス権限をチェック
        if not await self._check_access_permission(platform_id, sync_data):
            return None
        
        # データを復号化
        decrypted_content = self._decrypt_data(sync_data.content)
        
        return {
            "data_id": data_id,
            "data_type": sync_data.data_type.value,
            "content": decrypted_content,
            "version": sync_data.version,
            "timestamp": sync_data.timestamp.isoformat(),
            "source_platform": sync_data.source_platform
        }

    async def update_data(
        self,
        data_id: str,
        content: Dict[str, Any],
        source_platform: str
    ) -> bool:
        """データを更新"""
        if data_id not in self.sync_data_store:
            return False
        
        existing_data = self.sync_data_store[data_id]
        
        # 競合チェック
        if await self._check_conflict(data_id, content, source_platform):
            await self._handle_conflict(data_id, content, source_platform)
            return False
        
        # データを更新
        encrypted_content = self._encrypt_data(content)
        checksum = self._calculate_data_checksum(content)
        
        existing_data.content = encrypted_content
        existing_data.version += 1
        existing_data.timestamp = datetime.now()
        existing_data.checksum = checksum
        
        # 同期操作を作成
        target_platforms = [
            pid for pid in self.platforms.keys() 
            if pid != source_platform and self.platforms[pid].is_active
        ]
        
        operation_id = await self._create_sync_operation(
            data_id, "update", source_platform, target_platforms
        )
        
        # 非同期で同期実行
        asyncio.create_task(self._execute_sync_operation(operation_id))
        
        return True

    async def delete_data(self, data_id: str, source_platform: str) -> bool:
        """データを削除"""
        if data_id not in self.sync_data_store:
            return False
        
        # 同期操作を作成
        target_platforms = [
            pid for pid in self.platforms.keys() 
            if pid != source_platform and self.platforms[pid].is_active
        ]
        
        operation_id = await self._create_sync_operation(
            data_id, "delete", source_platform, target_platforms
        )
        
        # 非同期で同期実行
        asyncio.create_task(self._execute_sync_operation(operation_id))
        
        # ローカルデータを削除
        del self.sync_data_store[data_id]
        
        return True

    async def start_sync_service(self) -> None:
        """同期サービスを開始"""
        if self.is_running:
            return
        
        self.is_running = True
        self._sync_task = asyncio.create_task(self._sync_loop())
        
        await self._emit_event("sync_service_started", {})

    async def stop_sync_service(self) -> None:
        """同期サービスを停止"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
        
        await self._emit_event("sync_service_stopped", {})

    def add_event_handler(self, event_type: str, handler: Callable) -> None:
        """イベントハンドラーを追加"""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)

    def remove_event_handler(self, event_type: str, handler: Callable) -> None:
        """イベントハンドラーを削除"""
        if event_type in self._event_handlers:
            try:
                self._event_handlers[event_type].remove(handler)
            except ValueError:
                pass

    async def get_sync_status(self) -> Dict[str, Any]:
        """同期ステータスを取得"""
        active_platforms = [
            p for p in self.platforms.values() if p.is_active
        ]
        
        pending_operations = [
            op for op in self.sync_operations.values() 
            if op.status in [SyncStatus.PENDING, SyncStatus.IN_PROGRESS]
        ]
        
        return {
            "is_running": self.is_running,
            "active_platforms": len(active_platforms),
            "total_data_items": len(self.sync_data_store),
            "pending_operations": len(pending_operations),
            "last_sync": datetime.now().isoformat(),
            "platforms": [
                {
                    "id": p.platform_id,
                    "type": p.platform_type.value,
                    "version": p.version,
                    "last_seen": p.last_seen.isoformat(),
                    "is_active": p.is_active
                }
                for p in self.platforms.values()
            ]
        }

    # プライベートメソッド
    
    def _encrypt_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """データを暗号化"""
        data_str = json.dumps(data, ensure_ascii=False)
        encrypted_bytes = self.encryption_key.encrypt(data_str.encode())
        return {
            "encrypted": base64.b64encode(encrypted_bytes).decode(),
            "algorithm": "fernet"
        }

    def _decrypt_data(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """データを復号化"""
        encrypted_bytes = base64.b64decode(
            encrypted_data["encrypted"].encode()
        )
        decrypted_bytes = self.encryption_key.decrypt(encrypted_bytes)
        return json.loads(decrypted_bytes.decode())

    async def _check_access_permission(
        self, 
        platform_id: str, 
        sync_data: SyncData
    ) -> bool:
        """アクセス権限をチェック"""
        # 基本的なアクセス制御ロジック
        if platform_id not in self.platforms:
            return False
        
        platform = self.platforms[platform_id]
        if not platform.is_active:
            return False
        
        # データタイプ別のアクセス制御
        required_capability = f"access_{sync_data.data_type.value}"
        return required_capability in platform.capabilities

    async def _check_conflict(
        self, 
        data_id: str, 
        new_content: Dict[str, Any], 
        source_platform: str
    ) -> bool:
        """データ競合をチェック"""
        existing_data = self.sync_data_store[data_id]
        new_checksum = self._calculate_data_checksum(new_content)
        
        # チェックサムが異なり、かつ最近更新されている場合は競合
        time_threshold = datetime.now() - timedelta(seconds=5)
        return (
            existing_data.checksum != new_checksum and
            existing_data.timestamp > time_threshold and
            existing_data.source_platform != source_platform
        )

    async def _handle_conflict(
        self, 
        data_id: str, 
        new_content: Dict[str, Any], 
        source_platform: str
    ) -> None:
        """データ競合を処理"""
        if self.conflict_strategy == ConflictResolutionStrategy.LATEST_WINS:
            # 最新のデータが勝利
            await self.update_data(data_id, new_content, source_platform)
        elif self.conflict_strategy == ConflictResolutionStrategy.MANUAL_RESOLUTION:
            # 手動解決のためにイベントを発火
            await self._emit_event("conflict_detected", {
                "data_id": data_id,
                "source_platform": source_platform,
                "new_content": new_content
            })

    async def _create_sync_operation(
        self,
        data_id: str,
        operation_type: str,
        source_platform: str,
        target_platforms: List[str]
    ) -> str:
        """同期操作を作成"""
        operation_id = str(uuid.uuid4())
        
        operation = SyncOperation(
            operation_id=operation_id,
            data_id=data_id,
            operation_type=operation_type,
            source_platform=source_platform,
            target_platforms=target_platforms,
            status=SyncStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.sync_operations[operation_id] = operation
        return operation_id

    async def _execute_sync_operation(self, operation_id: str) -> None:
        """同期操作を実行"""
        if operation_id not in self.sync_operations:
            return
        
        operation = self.sync_operations[operation_id]
        operation.status = SyncStatus.IN_PROGRESS
        operation.updated_at = datetime.now()
        
        try:
            for target_platform in operation.target_platforms:
                if target_platform not in self.platforms:
                    continue
                
                platform = self.platforms[target_platform]
                if not platform.is_active:
                    continue
                
                # プラットフォーム固有の同期ロジック
                success = await self._sync_to_platform(
                    operation, platform
                )
                
                if not success:
                    operation.retry_count += 1
                    if operation.retry_count >= operation.max_retries:
                        operation.status = SyncStatus.FAILED
                        operation.error_message = (
                            f"Failed to sync to {target_platform}"
                        )
                        break
                    else:
                        # リトライのために少し待機
                        await asyncio.sleep(2 ** operation.retry_count)
                        continue
            
            if operation.status != SyncStatus.FAILED:
                operation.status = SyncStatus.COMPLETED
            
        except Exception as e:
            operation.status = SyncStatus.FAILED
            operation.error_message = str(e)
        
        operation.updated_at = datetime.now()
        
        # 同期完了イベントを発火
        await self._emit_event("sync_operation_completed", {
            "operation_id": operation_id,
            "status": operation.status.value,
            "data_id": operation.data_id
        })

    async def _sync_to_platform(
        self, 
        operation: SyncOperation, 
        platform: PlatformInfo
    ) -> bool:
        """特定のプラットフォームに同期"""
        try:
            if platform.endpoint_url:
                # HTTP APIを使用した同期
                return await self._sync_via_http(operation, platform)
            else:
                # ローカルファイルシステムを使用した同期
                return await self._sync_via_filesystem(operation, platform)
        except Exception:
            return False

    async def _sync_via_http(
        self, 
        operation: SyncOperation, 
        platform: PlatformInfo
    ) -> bool:
        """HTTP API経由での同期"""
        headers = {}
        if platform.auth_token:
            headers["Authorization"] = f"Bearer {platform.auth_token}"
        
        data_payload = {
            "operation_id": operation.operation_id,
            "data_id": operation.data_id,
            "operation_type": operation.operation_type,
            "data": self.sync_data_store.get(operation.data_id)
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{platform.endpoint_url}/sync",
                json=data_payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                return response.status == 200

    async def _sync_via_filesystem(
        self, 
        operation: SyncOperation, 
        platform: PlatformInfo
    ) -> bool:
        """ファイルシステム経由での同期"""
        # プラットフォーム固有のディレクトリに同期
        sync_dir = Path(f"sync/{platform.platform_type.value}")
        sync_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = sync_dir / f"{operation.data_id}.json"
        
        if operation.operation_type == "delete":
            if file_path.exists():
                file_path.unlink()
            return True
        
        sync_data = self.sync_data_store.get(operation.data_id)
        if not sync_data:
            return False
        
        data_dict = asdict(sync_data)
        data_dict["timestamp"] = sync_data.timestamp.isoformat()
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data_dict, ensure_ascii=False, indent=2))
        
        return True

    async def _sync_loop(self) -> None:
        """同期ループ"""
        while self.is_running:
            try:
                # プラットフォームのヘルスチェック
                await self._health_check_platforms()
                
                # 失敗した操作のリトライ
                await self._retry_failed_operations()
                
                # 定期的なデータ整合性チェック
                await self._check_data_integrity()
                
                await asyncio.sleep(self.sync_interval)
                
            except Exception as e:
                await self._emit_event("sync_error", {
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                await asyncio.sleep(5)  # エラー時は短い間隔で再試行

    async def _health_check_platforms(self) -> None:
        """プラットフォームのヘルスチェック"""
        for platform in self.platforms.values():
            if not platform.is_active:
                continue
            
            # 最後に見た時間から一定時間経過していたら非アクティブに
            time_diff = (datetime.now() - platform.last_seen).seconds
            if time_diff > 300:  # 5分
                platform.is_active = False
                await self._emit_event("platform_inactive", {
                    "platform_id": platform.platform_id,
                    "platform_type": platform.platform_type.value
                })

    async def _retry_failed_operations(self) -> None:
        """失敗した操作をリトライ"""
        failed_operations = [
            op for op in self.sync_operations.values()
            if op.status == SyncStatus.FAILED and 
            op.retry_count < op.max_retries
        ]
        
        for operation in failed_operations:
            # 指数バックオフでリトライ
            wait_time = 2 ** operation.retry_count
            time_since_update = (
                datetime.now() - operation.updated_at
            ).seconds
            if time_since_update >= wait_time:
                asyncio.create_task(
                    self._execute_sync_operation(operation.operation_id)
                )

    async def _check_data_integrity(self) -> None:
        """データ整合性をチェック"""
        # チェックサムの検証
        for data_id, sync_data in self.sync_data_store.items():
            try:
                decrypted_content = self._decrypt_data(sync_data.content)
                calculated_checksum = self._calculate_data_checksum(
                    decrypted_content
                )
                
                if calculated_checksum != sync_data.checksum:
                    await self._emit_event("data_integrity_error", {
                        "data_id": data_id,
                        "expected_checksum": sync_data.checksum,
                        "calculated_checksum": calculated_checksum
                    })
            except Exception as e:
                await self._emit_event("data_integrity_error", {
                    "data_id": data_id,
                    "error": str(e)
                })

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

    async def _save_platform_config(self) -> None:
        """プラットフォーム設定を保存"""
        config_data = {
            "platforms": {
                pid: {
                    "platform_id": p.platform_id,
                    "platform_type": p.platform_type.value,
                    "version": p.version,
                    "capabilities": p.capabilities,
                    "last_seen": p.last_seen.isoformat(),
                    "is_active": p.is_active,
                    "endpoint_url": p.endpoint_url,
                    "metadata": p.metadata
                }
                for pid, p in self.platforms.items()
            }
        }
        
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(
            self.config_path, 'w', encoding='utf-8'
        ) as f:
            await f.write(
                json.dumps(config_data, ensure_ascii=False, indent=2)
            )

    async def load_platform_config(self) -> None:
        """プラットフォーム設定を読み込み"""
        if not self.config_path.exists():
            return
        
        try:
            async with aiofiles.open(
                self.config_path, 'r', encoding='utf-8'
            ) as f:
                config_data = json.loads(await f.read())
            
            for pid, p_data in config_data.get("platforms", {}).items():
                platform_info = PlatformInfo(
                    platform_id=p_data["platform_id"],
                    platform_type=PlatformType(p_data["platform_type"]),
                    version=p_data["version"],
                    capabilities=p_data["capabilities"],
                    last_seen=datetime.fromisoformat(p_data["last_seen"]),
                    is_active=p_data["is_active"],
                    endpoint_url=p_data.get("endpoint_url"),
                    metadata=p_data.get("metadata", {})
                )
                self.platforms[pid] = platform_info
                
        except Exception as e:
            await self._emit_event("config_load_error", {
                "error": str(e),
                "config_path": str(self.config_path)
            })
    
    async def _process_data(
        self, 
        data: Dict[str, Any], 
        operation_type: str = "process"
    ) -> Dict[str, Any]:
        """データを処理"""
        processed_data = data.copy()
        
        # データ処理のタイムスタンプを追加
        processed_data["processed_at"] = datetime.now().isoformat()
        processed_data["operation_type"] = operation_type
        
        # データの検証
        if "data_type" not in processed_data:
            processed_data["data_type"] = "unknown"
        
        # データサイズの計算
        data_size = len(json.dumps(processed_data, ensure_ascii=False))
        processed_data["data_size"] = data_size
        
        return processed_data