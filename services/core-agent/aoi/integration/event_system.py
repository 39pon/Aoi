"""統合システムのイベント管理

クロスプラットフォーム統合でのイベント処理、
リアルタイム通信、状態変更通知を管理するシステム
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import weakref
from collections import defaultdict


class EventType(Enum):
    """イベントタイプ"""
    # データ関連
    DATA_CREATED = "data_created"
    DATA_UPDATED = "data_updated"
    DATA_DELETED = "data_deleted"
    DATA_SYNCED = "data_synced"
    
    # プラットフォーム関連
    PLATFORM_CONNECTED = "platform_connected"
    PLATFORM_DISCONNECTED = "platform_disconnected"
    PLATFORM_ERROR = "platform_error"
    PLATFORM_STATUS_CHANGED = "platform_status_changed"
    
    # 同期関連
    SYNC_STARTED = "sync_started"
    SYNC_COMPLETED = "sync_completed"
    SYNC_FAILED = "sync_failed"
    SYNC_CONFLICT = "sync_conflict"
    
    # 設定関連
    CONFIG_UPDATED = "config_updated"
    RULE_ADDED = "rule_added"
    RULE_UPDATED = "rule_updated"
    RULE_DELETED = "rule_deleted"
    
    # システム関連
    SYSTEM_STARTED = "system_started"
    SYSTEM_STOPPED = "system_stopped"
    HEALTH_CHECK = "health_check"
    ERROR_OCCURRED = "error_occurred"
    
    # カスタムイベント
    CUSTOM = "custom"


class EventPriority(Enum):
    """イベント優先度"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Event:
    """イベントデータ"""
    id: str
    type: EventType
    source: str  # イベント発生源（プラットフォーム名など）
    target: Optional[str] = None  # イベント対象
    data: Dict[str, Any] = field(default_factory=dict)
    priority: EventPriority = EventPriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None  # 関連イベントのグループ化
    retry_count: int = 0
    max_retries: int = 3
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)
        if isinstance(self.expires_at, str):
            self.expires_at = datetime.fromisoformat(self.expires_at)

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "id": self.id,
            "type": self.type.value,
            "source": self.source,
            "target": self.target,
            "data": self.data,
            "priority": self.priority.value,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "expires_at": (
                self.expires_at.isoformat() if self.expires_at else None
            ),
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """辞書から作成"""
        data = data.copy()
        data["type"] = EventType(data["type"])
        data["priority"] = EventPriority(data["priority"])
        return cls(**data)


class EventHandler:
    """イベントハンドラーの基底クラス"""
    
    def __init__(self, handler_id: str):
        self.handler_id = handler_id
        self.is_active = True
        self.handled_count = 0
        self.error_count = 0
        self.last_handled = None
    
    async def handle(self, event: Event) -> bool:
        """イベントを処理
        
        Returns:
            bool: 処理が成功したかどうか
        """
        try:
            if not self.is_active:
                return False
            
            result = await self._handle_event(event)
            if result:
                self.handled_count += 1
                self.last_handled = datetime.now()
            else:
                self.error_count += 1
            
            return result
            
        except Exception:
            self.error_count += 1
            return False
    
    async def _handle_event(self, event: Event) -> bool:
        """実際のイベント処理（サブクラスで実装）"""
        raise NotImplementedError
    
    def activate(self):
        """ハンドラーを有効化"""
        self.is_active = True
    
    def deactivate(self):
        """ハンドラーを無効化"""
        self.is_active = False
    
    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        return {
            "handler_id": self.handler_id,
            "is_active": self.is_active,
            "handled_count": self.handled_count,
            "error_count": self.error_count,
            "last_handled": (
                self.last_handled.isoformat() if self.last_handled else None
            )
        }


class FunctionEventHandler(EventHandler):
    """関数ベースのイベントハンドラー"""
    
    def __init__(self, handler_id: str, handler_func: Callable[[Event], bool]):
        super().__init__(handler_id)
        self.handler_func = handler_func
    
    async def _handle_event(self, event: Event) -> bool:
        """関数を呼び出してイベントを処理"""
        if asyncio.iscoroutinefunction(self.handler_func):
            return await self.handler_func(event)
        else:
            return self.handler_func(event)


class EventBus:
    """イベントバスシステム"""
    
    def __init__(self, max_queue_size: int = 10000):
        self.max_queue_size = max_queue_size
        
        # イベントキューと処理
        self.event_queue: asyncio.Queue = asyncio.Queue(
            maxsize=max_queue_size
        )
        self.processing_task: Optional[asyncio.Task] = None
        self.is_running = False
        
        # ハンドラー管理
        self.handlers: Dict[EventType, List[EventHandler]] = defaultdict(list)
        self.global_handlers: List[EventHandler] = []
        self.handler_refs: Dict[str, weakref.ref] = {}
        
        # 統計情報
        self.stats = {
            "events_published": 0,
            "events_processed": 0,
            "events_failed": 0,
            "events_dropped": 0,
            "handlers_registered": 0,
            "handlers_active": 0
        }
        
        # イベント履歴（デバッグ用）
        self.event_history: List[Event] = []
        self.max_history_size = 1000
        
        # フィルター
        self.event_filters: List[Callable[[Event], bool]] = []
        
        # リトライ設定
        self.retry_queue: asyncio.Queue = asyncio.Queue()
        self.retry_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """イベントバスを開始"""
        if self.is_running:
            return
        
        self.is_running = True
        self.processing_task = asyncio.create_task(self._process_events())
        self.retry_task = asyncio.create_task(self._process_retries())
        
        # システム開始イベントを発行
        await self.publish(Event(
            id=str(uuid.uuid4()),
            type=EventType.SYSTEM_STARTED,
            source="event_bus",
            data={"timestamp": datetime.now().isoformat()}
        ))
    
    async def stop(self):
        """イベントバスを停止"""
        if not self.is_running:
            return
        
        # システム停止イベントを発行
        await self.publish(Event(
            id=str(uuid.uuid4()),
            type=EventType.SYSTEM_STOPPED,
            source="event_bus",
            data={"timestamp": datetime.now().isoformat()}
        ))
        
        self.is_running = False
        
        # 処理中のタスクを停止
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        
        if self.retry_task:
            self.retry_task.cancel()
            try:
                await self.retry_task
            except asyncio.CancelledError:
                pass
    
    async def publish(self, event: Event) -> bool:
        """イベントを発行"""
        if not self.is_running:
            return False
        
        # フィルターをチェック
        for filter_func in self.event_filters:
            if not filter_func(event):
                return False
        
        # 期限切れチェック
        if event.expires_at and event.expires_at < datetime.now():
            return False
        
        try:
            # キューに追加（ノンブロッキング）
            self.event_queue.put_nowait(event)
            self.stats["events_published"] += 1
            
            # 履歴に追加
            self._add_to_history(event)
            
            return True
            
        except asyncio.QueueFull:
            self.stats["events_dropped"] += 1
            return False
    
    def subscribe(
        self, 
        event_type: EventType, 
        handler: EventHandler
    ) -> str:
        """イベントタイプにハンドラーを登録"""
        self.handlers[event_type].append(handler)
        self.handler_refs[handler.handler_id] = weakref.ref(handler)
        self.stats["handlers_registered"] += 1
        self._update_active_handlers_count()
        return handler.handler_id
    
    def subscribe_function(
        self, 
        event_type: EventType, 
        handler_func: Callable[[Event], bool],
        handler_id: Optional[str] = None
    ) -> str:
        """関数をイベントハンドラーとして登録"""
        if not handler_id:
            handler_id = str(uuid.uuid4())
        
        handler = FunctionEventHandler(handler_id, handler_func)
        return self.subscribe(event_type, handler)
    
    def subscribe_global(self, handler: EventHandler) -> str:
        """全イベントタイプにハンドラーを登録"""
        self.global_handlers.append(handler)
        self.handler_refs[handler.handler_id] = weakref.ref(handler)
        self.stats["handlers_registered"] += 1
        self._update_active_handlers_count()
        return handler.handler_id
    
    def unsubscribe(self, handler_id: str) -> bool:
        """ハンドラーの登録を解除"""
        removed = False
        
        # 特定イベントタイプのハンドラーから削除
        for event_type, handler_list in self.handlers.items():
            self.handlers[event_type] = [
                h for h in handler_list if h.handler_id != handler_id
            ]
            if len(handler_list) != len(self.handlers[event_type]):
                removed = True
        
        # グローバルハンドラーから削除
        original_count = len(self.global_handlers)
        self.global_handlers = [
            h for h in self.global_handlers if h.handler_id != handler_id
        ]
        if len(self.global_handlers) != original_count:
            removed = True
        
        # 参照を削除
        if handler_id in self.handler_refs:
            del self.handler_refs[handler_id]
        
        if removed:
            self.stats["handlers_registered"] -= 1
            self._update_active_handlers_count()
        
        return removed
    
    def add_filter(self, filter_func: Callable[[Event], bool]):
        """イベントフィルターを追加"""
        self.event_filters.append(filter_func)
    
    def remove_filter(self, filter_func: Callable[[Event], bool]):
        """イベントフィルターを削除"""
        if filter_func in self.event_filters:
            self.event_filters.remove(filter_func)
    
    async def _process_events(self):
        """イベント処理ループ"""
        while self.is_running:
            try:
                # イベントを取得（タイムアウト付き）
                event = await asyncio.wait_for(
                    self.event_queue.get(), timeout=1.0
                )
                
                # イベントを処理
                await self._handle_event(event)
                
            except asyncio.TimeoutError:
                # タイムアウトは正常（継続）
                continue
            except Exception:
                # エラーが発生した場合も継続
                continue
    
    async def _handle_event(self, event: Event):
        """単一イベントの処理"""
        try:
            handlers_to_run = []
            
            # 特定イベントタイプのハンドラーを取得
            if event.type in self.handlers:
                handlers_to_run.extend(self.handlers[event.type])
            
            # グローバルハンドラーを追加
            handlers_to_run.extend(self.global_handlers)
            
            # 優先度順にソート
            if event.priority == EventPriority.CRITICAL:
                # クリティカルイベントは即座に処理
                await self._run_handlers(event, handlers_to_run)
            else:
                # 通常イベントは非同期で処理
                asyncio.create_task(
                    self._run_handlers(event, handlers_to_run)
                )
            
            self.stats["events_processed"] += 1
            
        except Exception:
            self.stats["events_failed"] += 1
            
            # リトライが必要な場合
            if event.retry_count < event.max_retries:
                event.retry_count += 1
                await self.retry_queue.put(event)
    
    async def _run_handlers(self, event: Event, handlers: List[EventHandler]):
        """ハンドラーを実行"""
        tasks = []
        
        for handler in handlers:
            if handler.is_active:
                task = asyncio.create_task(handler.handle(event))
                tasks.append(task)
        
        if tasks:
            # 全ハンドラーの完了を待機
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _process_retries(self):
        """リトライ処理ループ"""
        while self.is_running:
            try:
                # リトライイベントを取得
                event = await asyncio.wait_for(
                    self.retry_queue.get(), timeout=5.0
                )
                
                # 少し待ってからリトライ
                await asyncio.sleep(1.0 * event.retry_count)
                
                # 再度処理
                await self._handle_event(event)
                
            except asyncio.TimeoutError:
                continue
            except Exception:
                continue
    
    def _add_to_history(self, event: Event):
        """イベント履歴に追加"""
        self.event_history.append(event)
        
        # 履歴サイズを制限
        if len(self.event_history) > self.max_history_size:
            self.event_history = self.event_history[-self.max_history_size:]
    
    def _update_active_handlers_count(self):
        """アクティブハンドラー数を更新"""
        active_count = 0
        
        # 特定イベントタイプのハンドラー
        for handler_list in self.handlers.values():
            active_count += sum(1 for h in handler_list if h.is_active)
        
        # グローバルハンドラー
        active_count += sum(1 for h in self.global_handlers if h.is_active)
        
        self.stats["handlers_active"] = active_count
    
    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        self._update_active_handlers_count()
        
        return {
            **self.stats,
            "is_running": self.is_running,
            "queue_size": self.event_queue.qsize(),
            "retry_queue_size": self.retry_queue.qsize(),
            "history_size": len(self.event_history),
            "event_types_subscribed": len(self.handlers),
            "global_handlers": len(self.global_handlers)
        }
    
    def get_recent_events(
        self, 
        limit: int = 100, 
        event_type: Optional[EventType] = None
    ) -> List[Event]:
        """最近のイベントを取得"""
        events = self.event_history[-limit:]
        
        if event_type:
            events = [e for e in events if e.type == event_type]
        
        return events
    
    def get_handler_stats(self) -> List[Dict[str, Any]]:
        """全ハンドラーの統計情報を取得"""
        stats = []
        
        # 特定イベントタイプのハンドラー
        for event_type, handler_list in self.handlers.items():
            for handler in handler_list:
                handler_stats = handler.get_stats()
                handler_stats["event_type"] = event_type.value
                handler_stats["is_global"] = False
                stats.append(handler_stats)
        
        # グローバルハンドラー
        for handler in self.global_handlers:
            handler_stats = handler.get_stats()
            handler_stats["event_type"] = "*"
            handler_stats["is_global"] = True
            stats.append(handler_stats)
        
        return stats
    
    async def wait_for_event(
        self, 
        event_type: EventType, 
        timeout: Optional[float] = None,
        filter_func: Optional[Callable[[Event], bool]] = None
    ) -> Optional[Event]:
        """特定のイベントを待機"""
        event_received = asyncio.Event()
        received_event = None
        
        def handler(event: Event) -> bool:
            nonlocal received_event
            if not filter_func or filter_func(event):
                received_event = event
                event_received.set()
            return True
        
        # 一時的なハンドラーを登録
        handler_id = self.subscribe_function(event_type, handler)
        
        try:
            # イベントを待機
            await asyncio.wait_for(event_received.wait(), timeout=timeout)
            return received_event
        except asyncio.TimeoutError:
            return None
        finally:
            # ハンドラーを削除
            self.unsubscribe(handler_id)
    
    async def emit_and_wait(
        self, 
        event: Event, 
        response_type: EventType,
        timeout: float = 10.0
    ) -> Optional[Event]:
        """イベントを発行して応答を待機"""
        # 相関IDを設定
        if not event.correlation_id:
            event.correlation_id = str(uuid.uuid4())
        
        # 応答フィルター
        def response_filter(response_event: Event) -> bool:
            return response_event.correlation_id == event.correlation_id
        
        # 応答待機を開始
        wait_task = asyncio.create_task(
            self.wait_for_event(response_type, timeout, response_filter)
        )
        
        # イベントを発行
        await self.publish(event)
        
        # 応答を待機
        return await wait_task


# グローバルイベントバスインスタンス
_global_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """グローバルイベントバスを取得"""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


async def publish_event(
    event_type: EventType,
    source: str,
    data: Optional[Dict[str, Any]] = None,
    target: Optional[str] = None,
    priority: EventPriority = EventPriority.NORMAL,
    correlation_id: Optional[str] = None
) -> bool:
    """便利関数：イベントを発行"""
    event = Event(
        id=str(uuid.uuid4()),
        type=event_type,
        source=source,
        target=target,
        data=data or {},
        priority=priority,
        correlation_id=correlation_id
    )
    
    event_bus = get_event_bus()
    return await event_bus.publish(event)


def subscribe_to_event(
    event_type: EventType,
    handler_func: Callable[[Event], bool],
    handler_id: Optional[str] = None
) -> str:
    """便利関数：イベントハンドラーを登録"""
    event_bus = get_event_bus()
    return event_bus.subscribe_function(event_type, handler_func, handler_id)


def unsubscribe_from_event(handler_id: str) -> bool:
    """便利関数：イベントハンドラーの登録を解除"""
    event_bus = get_event_bus()
    return event_bus.unsubscribe(handler_id)