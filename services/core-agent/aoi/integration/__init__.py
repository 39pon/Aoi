"""Aoi統合システム

クロスプラットフォーム統合、データ同期、イベント処理を提供する
スケーラブルな統合システムパッケージ
"""

from .cross_platform_system import (
    CrossPlatformSystem,
    PlatformType,
    SyncStatus,
    DataType,
    ConflictResolutionStrategy,
    PlatformInfo,
    SyncData,
    SyncOperation
)

from .platform_adapters import (
    BasePlatformAdapter,
    BrowserAdapter,
    ObsidianAdapter,
    RaycastAdapter,
    AdapterManager,
    AdapterConfig
)

from .integration_config import (
    ConfigurationManager,
    SyncFrequency,
    SecurityLevel,
    SyncRule,
    PlatformCredentials,
    IntegrationConfig
)

from .event_system import (
    EventBus,
    Event,
    EventType,
    EventPriority,
    EventHandler,
    FunctionEventHandler,
    get_event_bus,
    publish_event,
    subscribe_to_event,
    unsubscribe_from_event
)

__version__ = "1.0.0"
__author__ = "Aoi Development Team"

__all__ = [
    # Core System
    "CrossPlatformSystem",
    "PlatformType",
    "SyncStatus",
    "DataType",
    "ConflictResolutionStrategy",
    "PlatformInfo",
    "SyncData",
    "SyncOperation",
    
    # Platform Adapters
    "BasePlatformAdapter",
    "BrowserAdapter",
    "ObsidianAdapter",
    "RaycastAdapter",
    "AdapterManager",
    "AdapterConfig",
    
    # Configuration
    "ConfigurationManager",
    "SyncFrequency",
    "SecurityLevel",
    "SyncRule",
    "PlatformCredentials",
    "IntegrationConfig",
    
    # Event System
    "EventBus",
    "Event",
    "EventType",
    "EventPriority",
    "EventHandler",
    "FunctionEventHandler",
    "get_event_bus",
    "publish_event",
    "subscribe_to_event",
    "unsubscribe_from_event",
]


def create_integration_system(
    config_path: str = "integration_config.json",
    auto_start: bool = True
) -> CrossPlatformSystem:
    """統合システムを作成・初期化
    
    Args:
        config_path: 設定ファイルのパス
        auto_start: 自動的に同期サービスを開始するか
    
    Returns:
        CrossPlatformSystem: 初期化された統合システム
    """
    # 設定管理を初期化
    config_manager = ConfigurationManager(config_path)
    
    # イベントバスを初期化
    event_bus = get_event_bus()
    
    # 統合システムを作成
    system = CrossPlatformSystem(config_path)
    
    # アダプターマネージャーを初期化
    adapter_manager = AdapterManager()
    
    # デフォルトアダプター設定を登録
    adapter_manager.register_adapter_config(
        PlatformType.BROWSER,
        AdapterConfig(
            platform_type=PlatformType.BROWSER,
            connection_params={"websocket_url": "ws://localhost:8080/ws"},
            sync_capabilities=["bookmarks", "tabs", "history"]
        )
    )
    adapter_manager.register_adapter_config(
        PlatformType.OBSIDIAN,
        AdapterConfig(
            platform_type=PlatformType.OBSIDIAN,
            connection_params={"vault_path": "~/Documents/Obsidian"},
            sync_capabilities=["notes", "tags", "links"]
        )
    )
    adapter_manager.register_adapter_config(
        PlatformType.RAYCAST,
        AdapterConfig(
            platform_type=PlatformType.RAYCAST,
            connection_params={"extension_path": "~/Library/Application Support/com.raycast.macos/extensions"},
            sync_capabilities=["commands", "snippets", "quicklinks"]
        )
    )
    
    # システムにアダプターマネージャーを設定
    system.adapter_manager = adapter_manager
    
    if auto_start:
        # 非同期で開始（実際の使用時は await が必要）
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 既存のループで実行
                asyncio.create_task(system.start_sync_service())
                asyncio.create_task(event_bus.start())
            else:
                # 新しいループで実行
                loop.run_until_complete(system.start_sync_service())
                loop.run_until_complete(event_bus.start())
        except RuntimeError:
            # ループが存在しない場合は新しく作成
            asyncio.run(system.start_sync_service())
            asyncio.run(event_bus.start())
    
    return system


async def initialize_integration_system(
    config_path: str = "integration_config.json"
) -> CrossPlatformSystem:
    """統合システムを非同期で初期化
    
    Args:
        config_path: 設定ファイルのパス
    
    Returns:
        CrossPlatformSystem: 初期化された統合システム
    """
    # 設定管理を初期化（ファイルパスを使用）
    from pathlib import Path
    config_file = Path(config_path)
    
    # ファイルが存在する場合は削除してディレクトリとして作成
    if config_file.exists() and config_file.is_file():
        config_file.unlink()
    
    if config_file.suffix:  # ファイル拡張子がある場合はファイルパス
        config_dir = config_file.parent
        # 設定ディレクトリ名をファイル名から生成
        config_dir = config_dir / config_file.stem
    else:  # 拡張子がない場合はディレクトリパス
        config_dir = config_file
    
    config_manager = ConfigurationManager(config_dir)
    await config_manager.load_config()
    
    # イベントバスを初期化・開始
    event_bus = get_event_bus()
    await event_bus.start()
    
    # 統合システムを作成
    system = CrossPlatformSystem(config_path)
    
    # アダプターマネージャーを初期化
    adapter_manager = AdapterManager()
    
    # デフォルトアダプター設定を登録
    adapter_manager.register_adapter_config(
        PlatformType.BROWSER,
        AdapterConfig(
            platform_type=PlatformType.BROWSER,
            connection_params={"websocket_url": "ws://localhost:8080/ws"},
            sync_capabilities=["bookmarks", "tabs", "history"]
        )
    )
    
    adapter_manager.register_adapter_config(
        PlatformType.OBSIDIAN,
        AdapterConfig(
            platform_type=PlatformType.OBSIDIAN,
            connection_params={"vault_path": "~/Documents/Obsidian"},
            sync_capabilities=["notes", "tags", "links"]
        )
    )
    
    adapter_manager.register_adapter_config(
        PlatformType.RAYCAST,
        AdapterConfig(
            platform_type=PlatformType.RAYCAST,
            connection_params={"extension_path": "~/Library/Application Support/com.raycast.macos/extensions"},
            sync_capabilities=["commands", "snippets", "quicklinks"]
        )
    )
    
    # システムにアダプターマネージャーを設定
    system.adapter_manager = adapter_manager
    
    # 同期サービスを開始
    await system.start_sync_service()
    
    return system


def get_system_info() -> dict:
    """システム情報を取得
    
    Returns:
        dict: システム情報
    """
    return {
        "name": "Aoi Integration System",
        "version": __version__,
        "author": __author__,
        "description": "スケーラブルなクロスプラットフォーム統合システム",
        "components": {
            "cross_platform_system": "コアシステム",
            "platform_adapters": "プラットフォームアダプター",
            "integration_config": "設定管理",
            "event_system": "イベントシステム"
        },
        "supported_platforms": [
            "Browser (Chrome, Firefox, Safari)",
            "Obsidian",
            "Raycast"
        ],
        "features": [
            "リアルタイムデータ同期",
            "イベント駆動アーキテクチャ",
            "プラットフォーム間統合",
            "設定管理",
            "セキュリティ機能",
            "スケーラブル設計"
        ]
    }