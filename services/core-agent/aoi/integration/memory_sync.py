"""クロスプラットフォーム記憶同期システム

メモリ管理システムとクロスプラットフォーム統合を連携し、
会話履歴、知識、コンテキストの同期を実現する
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
# aiofilesのインポート（オプション）
try:
    import aiofiles
except ImportError:
    aiofiles = None

from .cross_platform_system import (
    CrossPlatformSystem, 
    DataType
)
# メモリマネージャーのインポート
try:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent / "src"))
    from aoi.memory.manager import MemoryManager
except ImportError:
    # フォールバック: 型ヒント用のダミークラス
    class MemoryManager:
        pass


@dataclass
class MemorySnapshot:
    """メモリスナップショット"""
    snapshot_id: str
    platform_id: str
    conversation_history: List[Dict[str, Any]]
    knowledge_base: List[Dict[str, Any]]
    context_data: Dict[str, Any]
    personality_state: Dict[str, Any]
    timestamp: datetime
    version: str = "1.0"


@dataclass
class SyncConflict:
    """同期競合情報"""
    conflict_id: str
    data_type: DataType
    platform_a: str
    platform_b: str
    data_a: Dict[str, Any]
    data_b: Dict[str, Any]
    timestamp: datetime
    resolution_strategy: Optional[str] = None
    resolved: bool = False


class MemorySyncManager:
    """記憶同期管理システム"""

    def __init__(
        self, 
        cross_platform_system: CrossPlatformSystem,
        memory_manager: Optional[MemoryManager] = None
    ):
        self.cross_platform = cross_platform_system
        self.memory_manager = memory_manager
        self.sync_conflicts: Dict[str, SyncConflict] = {}
        self.last_sync_timestamps: Dict[str, datetime] = {}
        self.sync_in_progress: Set[str] = set()
        
        # 同期設定
        self.auto_sync_enabled = True
        self.sync_interval = 60  # seconds
        self.max_history_items = 1000
        self.conflict_resolution_timeout = 300  # seconds
        
        # イベントハンドラー登録
        self._register_event_handlers()

    def _register_event_handlers(self) -> None:
        """イベントハンドラーを登録"""
        self.cross_platform.add_event_handler(
            "platform_connected", 
            self._on_platform_connected
        )
        self.cross_platform.add_event_handler(
            "data_updated", 
            self._on_data_updated
        )
        self.cross_platform.add_event_handler(
            "sync_conflict", 
            self._on_sync_conflict
        )

    async def _on_platform_connected(self, event_data: Dict[str, Any]) -> None:
        """プラットフォーム接続時の処理"""
        platform_id = event_data.get("platform_id")
        if platform_id and self.auto_sync_enabled:
            await self.sync_platform_memory(platform_id)

    async def _on_data_updated(self, event_data: Dict[str, Any]) -> None:
        """データ更新時の処理"""
        data_type = event_data.get("data_type")
        if data_type in [DataType.MEMORY.value, DataType.CONVERSATION.value]:
            await self._propagate_memory_update(event_data)

    async def _on_sync_conflict(self, event_data: Dict[str, Any]) -> None:
        """同期競合時の処理"""
        conflict = SyncConflict(
            conflict_id=str(uuid.uuid4()),
            data_type=DataType(event_data["data_type"]),
            platform_a=event_data["platform_a"],
            platform_b=event_data["platform_b"],
            data_a=event_data["data_a"],
            data_b=event_data["data_b"],
            timestamp=datetime.now()
        )
        
        self.sync_conflicts[conflict.conflict_id] = conflict
        await self._resolve_conflict(conflict)

    async def create_memory_snapshot(
        self, 
        platform_id: str
    ) -> MemorySnapshot:
        """メモリスナップショットを作成"""
        snapshot_id = str(uuid.uuid4())
        
        # 会話履歴を取得
        conversation_history = []
        if self.memory_manager:
            # メモリマネージャーから会話履歴を取得
            recent_conversations = await self._get_recent_conversations(
                limit=self.max_history_items
            )
            conversation_history = recent_conversations
        
        # 知識ベースを取得
        knowledge_base = await self._get_knowledge_base()
        
        # コンテキストデータを取得
        context_data = await self._get_context_data(platform_id)
        
        # 人格状態を取得
        personality_state = await self._get_personality_state(platform_id)
        
        snapshot = MemorySnapshot(
            snapshot_id=snapshot_id,
            platform_id=platform_id,
            conversation_history=conversation_history,
            knowledge_base=knowledge_base,
            context_data=context_data,
            personality_state=personality_state,
            timestamp=datetime.now()
        )
        
        return snapshot

    async def sync_platform_memory(
        self, 
        platform_id: str,
        force_sync: bool = False
    ) -> bool:
        """プラットフォームのメモリを同期"""
        if platform_id in self.sync_in_progress and not force_sync:
            return False
        
        self.sync_in_progress.add(platform_id)
        
        try:
            # 最新のメモリスナップショットを作成
            snapshot = await self.create_memory_snapshot(platform_id)
            
            # クロスプラットフォームシステムに同期データとして登録
            await self._sync_conversation_history(
                snapshot.conversation_history, 
                platform_id
            )
            await self._sync_knowledge_base(
                snapshot.knowledge_base, 
                platform_id
            )
            await self._sync_context_data(
                snapshot.context_data, 
                platform_id
            )
            await self._sync_personality_state(
                snapshot.personality_state, 
                platform_id
            )
            
            # 同期タイムスタンプを更新
            self.last_sync_timestamps[platform_id] = datetime.now()
            
            return True
            
        except Exception as e:
            print(f"メモリ同期エラー: {e}")
            return False
        finally:
            self.sync_in_progress.discard(platform_id)

    async def _sync_conversation_history(
        self, 
        conversations: List[Dict[str, Any]], 
        platform_id: str
    ) -> None:
        """会話履歴を同期"""
        for conversation in conversations:
            data_id = f"conversation_{conversation.get('id', uuid.uuid4())}"
            
            await self.cross_platform.sync_data(
                data_type=DataType.CONVERSATION,
                data_id=data_id,
                data=conversation,
                source_platform=platform_id,
                target_platforms=await self._get_target_platforms(platform_id)
            )

    async def _sync_knowledge_base(
        self, 
        knowledge: List[Dict[str, Any]], 
        platform_id: str
    ) -> None:
        """知識ベースを同期"""
        for knowledge_item in knowledge:
            data_id = f"knowledge_{knowledge_item.get('id', uuid.uuid4())}"
            
            await self.cross_platform.sync_data(
                data_type=DataType.MEMORY,
                data_id=data_id,
                data=knowledge_item,
                source_platform=platform_id,
                target_platforms=await self._get_target_platforms(platform_id)
            )

    async def _sync_context_data(
        self, 
        context: Dict[str, Any], 
        platform_id: str
    ) -> None:
        """コンテキストデータを同期"""
        data_id = f"context_{platform_id}"
        
        await self.cross_platform.sync_data(
            data_type=DataType.CONTEXT,
            data_id=data_id,
            data=context,
            source_platform=platform_id,
            target_platforms=await self._get_target_platforms(platform_id)
        )

    async def _sync_personality_state(
        self, 
        personality: Dict[str, Any], 
        platform_id: str
    ) -> None:
        """人格状態を同期"""
        data_id = f"personality_{platform_id}"
        
        await self.cross_platform.sync_data(
            data_type=DataType.PERSONALITY,
            data_id=data_id,
            data=personality,
            source_platform=platform_id,
            target_platforms=await self._get_target_platforms(platform_id)
        )

    async def _get_recent_conversations(
        self, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """最近の会話履歴を取得"""
        if not self.memory_manager:
            return []
        
        try:
            # メモリマネージャーから会話履歴を取得
            # 実装は memory_manager の API に依存
            conversations = []
            # TODO: memory_manager.get_recent_conversations(limit) の実装
            return conversations
        except Exception as e:
            print(f"会話履歴取得エラー: {e}")
            return []

    async def _get_knowledge_base(self) -> List[Dict[str, Any]]:
        """知識ベースを取得"""
        if not self.memory_manager:
            return []
        
        try:
            # メモリマネージャーから知識ベースを取得
            knowledge = []
            # TODO: memory_manager.get_knowledge_base() の実装
            return knowledge
        except Exception as e:
            print(f"知識ベース取得エラー: {e}")
            return []

    async def _get_context_data(self, platform_id: str) -> Dict[str, Any]:
        """コンテキストデータを取得"""
        return {
            "platform_id": platform_id,
            "last_activity": datetime.now().isoformat(),
            "session_data": {},
            "user_preferences": {},
            "active_tasks": []
        }

    async def _get_personality_state(self, platform_id: str) -> Dict[str, Any]:
        """人格状態を取得"""
        return {
            "personality_type": "caring_sister",
            "mood_state": "helpful",
            "conversation_style": "theoretical_gentle",
            "evidence_preference": "detailed",
            "platform_adaptations": {
                platform_id: {
                    "ui_preferences": {},
                    "interaction_style": "default"
                }
            }
        }

    async def _get_target_platforms(self, source_platform: str) -> List[str]:
        """同期対象プラットフォームを取得"""
        if hasattr(self.cross_platform.platforms, 'keys'):
            all_platforms = list(self.cross_platform.platforms.keys())
        else:
            all_platforms = self.cross_platform.platforms
        return [p for p in all_platforms if p != source_platform]

    async def _propagate_memory_update(
        self, 
        event_data: Dict[str, Any]
    ) -> None:
        """メモリ更新を他のプラットフォームに伝播"""
        source_platform = event_data.get("source_platform")
        if source_platform:
            await self.sync_platform_memory(source_platform)

    async def _resolve_conflict(self, conflict: SyncConflict) -> None:
        """同期競合を解決"""
        # 最新タイムスタンプ優先戦略
        timestamp_a = conflict.data_a.get("timestamp")
        timestamp_b = conflict.data_b.get("timestamp")
        
        if timestamp_a and timestamp_b:
            if timestamp_a > timestamp_b:
                winning_data = conflict.data_a
                winning_platform = conflict.platform_a
            else:
                winning_data = conflict.data_b
                winning_platform = conflict.platform_b
        else:
            # タイムスタンプがない場合はプラットフォーム優先度で決定
            winning_data = conflict.data_a
            winning_platform = conflict.platform_a
        
        # 勝利データで同期を実行
        data_id = f"resolved_{conflict.conflict_id}"
        await self.cross_platform.sync_data(
            data_id=data_id,
            data_type=conflict.data_type,
            content=winning_data,
            source_platform=winning_platform,
            target_platforms=[conflict.platform_a, conflict.platform_b]
        )
        
        conflict.resolved = True
        conflict.resolution_strategy = "latest_timestamp"

    async def get_sync_status(self, platform_id: str) -> Dict[str, Any]:
        """同期ステータスを取得"""
        last_sync = self.last_sync_timestamps.get(platform_id)
        is_syncing = platform_id in self.sync_in_progress
        
        return {
            "platform_id": platform_id,
            "last_sync": last_sync.isoformat() if last_sync else None,
            "is_syncing": is_syncing,
            "auto_sync_enabled": self.auto_sync_enabled,
            "sync_interval": self.sync_interval,
            "pending_conflicts": len([
                c for c in self.sync_conflicts.values() 
                if not c.resolved and (
                    c.platform_a == platform_id or c.platform_b == platform_id
                )
            ])
        }

    async def force_full_sync(self) -> Dict[str, bool]:
        """全プラットフォームの強制同期"""
        results = {}
        
        for platform_id in self.cross_platform.platforms.keys():
            try:
                success = await self.sync_platform_memory(
                    platform_id, 
                    force_sync=True
                )
                results[platform_id] = success
            except Exception as e:
                print(f"プラットフォーム {platform_id} の同期エラー: {e}")
                results[platform_id] = False
        
        return results

    async def cleanup_old_conflicts(self, max_age_hours: int = 24) -> int:
        """古い競合を清理"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        old_conflicts = [
            conflict_id for conflict_id, conflict in self.sync_conflicts.items()
            if conflict.timestamp < cutoff_time and conflict.resolved
        ]
        
        for conflict_id in old_conflicts:
            del self.sync_conflicts[conflict_id]
        
        return len(old_conflicts)

    async def export_memory_snapshot(
        self, 
        platform_id: str, 
        file_path: str
    ) -> bool:
        """メモリスナップショットをエクスポート"""
        try:
            snapshot = await self.create_memory_snapshot(platform_id)
            snapshot_dict = asdict(snapshot)
            snapshot_dict["timestamp"] = snapshot.timestamp.isoformat()
            
            if aiofiles:
                async with aiofiles.open(
                    file_path, 'w', encoding='utf-8'
                ) as f:
                    await f.write(
                        json.dumps(snapshot_dict, ensure_ascii=False, indent=2)
                    )
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(json.dumps(snapshot_dict, ensure_ascii=False, indent=2))
            
            return True
        except Exception as e:
            print(f"スナップショットエクスポートエラー: {e}")
            return False

    async def import_memory_snapshot(
        self, 
        platform_id: str, 
        file_path: str
    ) -> bool:
        """メモリスナップショットをインポート"""
        try:
            if aiofiles:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    snapshot_dict = json.loads(await f.read())
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    snapshot_dict = json.loads(f.read())
            
            # タイムスタンプを復元
            snapshot_dict["timestamp"] = datetime.fromisoformat(
                snapshot_dict["timestamp"]
            )
            
            snapshot = MemorySnapshot(**snapshot_dict)
            
            # スナップショットから同期を実行
            await self._sync_conversation_history(
                snapshot.conversation_history, 
                platform_id
            )
            await self._sync_knowledge_base(
                snapshot.knowledge_base, 
                platform_id
            )
            await self._sync_context_data(
                snapshot.context_data, 
                platform_id
            )
            await self._sync_personality_state(
                snapshot.personality_state, 
                platform_id
            )
            
            return True
        except Exception as e:
            print(f"スナップショットインポートエラー: {e}")
            return False