"""統合システムの設定管理

クロスプラットフォーム統合の設定、認証情報、
同期ルールなどを管理するシステム
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import aiofiles
from cryptography.fernet import Fernet

from aoi.integration.cross_platform_system import PlatformType, DataType


class SyncFrequency(Enum):
    """同期頻度"""
    REAL_TIME = "real_time"
    EVERY_MINUTE = "every_minute"
    EVERY_5_MINUTES = "every_5_minutes"
    EVERY_15_MINUTES = "every_15_minutes"
    EVERY_HOUR = "every_hour"
    DAILY = "daily"
    MANUAL = "manual"


class SecurityLevel(Enum):
    """セキュリティレベル"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


@dataclass
class SyncRule:
    """同期ルール"""
    id: str
    name: str
    data_type: DataType
    source_platforms: List[PlatformType]
    target_platforms: List[PlatformType]
    frequency: SyncFrequency
    security_level: SecurityLevel
    filters: Dict[str, Any] = field(default_factory=dict)
    transformations: List[str] = field(default_factory=list)
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)


@dataclass
class PlatformCredentials:
    """プラットフォーム認証情報"""
    platform_type: PlatformType
    platform_id: str
    auth_type: str  # "api_key", "oauth", "basic", "custom"
    credentials: Dict[str, str]  # 暗号化された認証情報
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None

    def __post_init__(self):
        if isinstance(self.expires_at, str):
            self.expires_at = datetime.fromisoformat(self.expires_at)
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.last_used, str):
            self.last_used = datetime.fromisoformat(self.last_used)


@dataclass
class IntegrationSettings:
    """統合設定"""
    user_id: str
    encryption_enabled: bool = True
    auto_sync_enabled: bool = True
    conflict_resolution: str = "latest_wins"  # "latest_wins", "manual", "merge"
    max_sync_retries: int = 3
    sync_timeout: int = 30  # seconds
    sync_interval: int = 30  # seconds
    data_retention_days: int = 365
    allowed_platforms: Set[PlatformType] = field(
        default_factory=lambda: set(PlatformType)
    )
    blocked_data_types: Set[DataType] = field(default_factory=set)
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if isinstance(self.allowed_platforms, list):
            self.allowed_platforms = set(self.allowed_platforms)
        if isinstance(self.blocked_data_types, list):
            self.blocked_data_types = set(self.blocked_data_types)
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)


@dataclass
class IntegrationConfig:
    """統合システム全体の設定"""
    settings: IntegrationSettings
    sync_rules: List[SyncRule] = field(default_factory=list)
    credentials: List[PlatformCredentials] = field(default_factory=list)
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)


class ConfigurationManager:
    """設定管理システム"""

    def __init__(self, config_dir: Path):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 設定ファイルのパス
        self.settings_file = self.config_dir / "integration_settings.json"
        self.sync_rules_file = self.config_dir / "sync_rules.json"
        self.credentials_file = self.config_dir / "credentials.json"
        self.encryption_key_file = self.config_dir / ".encryption_key"
        
        # 暗号化キー
        self._encryption_key: Optional[bytes] = None
        self._fernet: Optional[Fernet] = None
        
        # キャッシュ
        self._settings_cache: Optional[IntegrationSettings] = None
        self._sync_rules_cache: Dict[str, SyncRule] = {}
        self._credentials_cache: Dict[str, PlatformCredentials] = {}

    async def initialize(self) -> None:
        """設定管理システムを初期化"""
        await self._load_encryption_key()
        await self._load_settings()
        await self._load_sync_rules()
        await self._load_credentials()

    async def _load_encryption_key(self) -> None:
        """暗号化キーを読み込み"""
        if self.encryption_key_file.exists():
            async with aiofiles.open(self.encryption_key_file, 'rb') as f:
                self._encryption_key = await f.read()
        else:
            # 新しい暗号化キーを生成
            self._encryption_key = Fernet.generate_key()
            async with aiofiles.open(self.encryption_key_file, 'wb') as f:
                await f.write(self._encryption_key)
            
            # ファイルのパーミッションを制限
            self.encryption_key_file.chmod(0o600)
        
        self._fernet = Fernet(self._encryption_key)

    async def _load_settings(self) -> None:
        """統合設定を読み込み"""
        if self.settings_file.exists():
            try:
                async with aiofiles.open(
                    self.settings_file, 'r', encoding='utf-8'
                ) as f:
                    content = await f.read()
                    data = json.loads(content)
                    self._settings_cache = IntegrationSettings(**data)
            except Exception:
                # デフォルト設定を作成
                self._settings_cache = IntegrationSettings(
                    user_id=str(uuid.uuid4())
                )
                await self._save_settings()
        else:
            # デフォルト設定を作成
            self._settings_cache = IntegrationSettings(
                user_id=str(uuid.uuid4())
            )
            await self._save_settings()

    async def _save_settings(self) -> None:
        """統合設定を保存"""
        if not self._settings_cache:
            return
        
        # Set型をリストに変換
        data = {
            "user_id": self._settings_cache.user_id,
            "encryption_enabled": self._settings_cache.encryption_enabled,
            "auto_sync_enabled": self._settings_cache.auto_sync_enabled,
            "conflict_resolution": self._settings_cache.conflict_resolution,
            "max_sync_retries": self._settings_cache.max_sync_retries,
            "sync_timeout": self._settings_cache.sync_timeout,
            "sync_interval": self._settings_cache.sync_interval,
            "data_retention_days": self._settings_cache.data_retention_days,
            "allowed_platforms": [
                p.value if hasattr(p, 'value') else p 
                for p in self._settings_cache.allowed_platforms
            ],
            "blocked_data_types": [
                d.value if hasattr(d, 'value') else d 
                for d in self._settings_cache.blocked_data_types
            ],
            "custom_settings": self._settings_cache.custom_settings,
            "created_at": self._settings_cache.created_at.isoformat(),
            "updated_at": self._settings_cache.updated_at.isoformat()
        }
        
        async with aiofiles.open(
            self.settings_file, 'w', encoding='utf-8'
        ) as f:
            await f.write(
                json.dumps(data, ensure_ascii=False, indent=2)
            )

    async def _load_sync_rules(self) -> None:
        """同期ルールを読み込み"""
        if self.sync_rules_file.exists():
            try:
                async with aiofiles.open(
                    self.sync_rules_file, 'r', encoding='utf-8'
                ) as f:
                    content = await f.read()
                    data = json.loads(content)
                    
                    for rule_data in data:
                        # Enum型に変換
                        rule_data["data_type"] = DataType(
                            rule_data["data_type"]
                        )
                        rule_data["source_platforms"] = [
                            PlatformType(p)
                            for p in rule_data["source_platforms"]
                        ]
                        rule_data["target_platforms"] = [
                            PlatformType(p)
                            for p in rule_data["target_platforms"]
                        ]
                        rule_data["frequency"] = SyncFrequency(
                            rule_data["frequency"]
                        )
                        rule_data["security_level"] = SecurityLevel(
                            rule_data["security_level"]
                        )
                        
                        rule = SyncRule(**rule_data)
                        self._sync_rules_cache[rule.id] = rule
                        
            except Exception:
                # デフォルトルールを作成
                await self._create_default_sync_rules()
        else:
            # デフォルトルールを作成
            await self._create_default_sync_rules()

    async def _create_default_sync_rules(self) -> None:
        """デフォルト同期ルールを作成"""
        default_rules = [
            SyncRule(
                id=str(uuid.uuid4()),
                name="人格データ同期",
                data_type=DataType.PERSONALITY,
                source_platforms=[PlatformType.TRAE_IDE],
                target_platforms=[
                    PlatformType.BROWSER,
                    PlatformType.OBSIDIAN,
                    PlatformType.RAYCAST
                ],
                frequency=SyncFrequency.REAL_TIME,
                security_level=SecurityLevel.INTERNAL
            ),
            SyncRule(
                id=str(uuid.uuid4()),
                name="記憶データ同期",
                data_type=DataType.MEMORY,
                source_platforms=list(PlatformType),
                target_platforms=list(PlatformType),
                frequency=SyncFrequency.EVERY_5_MINUTES,
                security_level=SecurityLevel.CONFIDENTIAL
            ),
            SyncRule(
                id=str(uuid.uuid4()),
                name="設定同期",
                data_type=DataType.PREFERENCES,
                source_platforms=list(PlatformType),
                target_platforms=list(PlatformType),
                frequency=SyncFrequency.EVERY_MINUTE,
                security_level=SecurityLevel.INTERNAL
            )
        ]
        
        for rule in default_rules:
            self._sync_rules_cache[rule.id] = rule
        
        await self._save_sync_rules()

    async def _save_sync_rules(self) -> None:
        """同期ルールを保存"""
        data = []
        for rule in self._sync_rules_cache.values():
            rule_data = {
                "id": rule.id,
                "name": rule.name,
                "data_type": rule.data_type.value,
                "source_platforms": [
                    p.value for p in rule.source_platforms
                ],
                "target_platforms": [
                    p.value for p in rule.target_platforms
                ],
                "frequency": rule.frequency.value,
                "security_level": rule.security_level.value,
                "filters": rule.filters,
                "transformations": rule.transformations,
                "enabled": rule.enabled,
                "created_at": rule.created_at.isoformat(),
                "updated_at": rule.updated_at.isoformat()
            }
            data.append(rule_data)
        
        async with aiofiles.open(
            self.sync_rules_file, 'w', encoding='utf-8'
        ) as f:
            await f.write(
                json.dumps(data, ensure_ascii=False, indent=2)
            )

    async def _load_credentials(self) -> None:
        """認証情報を読み込み"""
        if self.credentials_file.exists():
            try:
                async with aiofiles.open(
                    self.credentials_file, 'r', encoding='utf-8'
                ) as f:
                    content = await f.read()
                    data = json.loads(content)
                    
                    for cred_data in data:
                        # Enum型に変換
                        cred_data["platform_type"] = PlatformType(
                            cred_data["platform_type"]
                        )
                        
                        # 認証情報を復号化
                        if self._fernet and cred_data.get("credentials"):
                            encrypted_creds = cred_data["credentials"]
                            decrypted_creds = {}
                            for key, encrypted_value in encrypted_creds.items():
                                try:
                                    decrypted_value = (
                                        self._fernet.decrypt(
                                            encrypted_value.encode()
                                        ).decode()
                                    )
                                    decrypted_creds[key] = decrypted_value
                                except Exception:
                                    # 復号化に失敗した場合はスキップ
                                    continue
                            cred_data["credentials"] = decrypted_creds
                        
                        cred = PlatformCredentials(**cred_data)
                        key = f"{cred.platform_type.value}_{cred.platform_id}"
                        self._credentials_cache[key] = cred
                        
            except Exception:
                # 認証情報の読み込みに失敗した場合は空のキャッシュを使用
                self._credentials_cache = {}

    async def _save_credentials(self) -> None:
        """認証情報を保存"""
        data = []
        for cred in self._credentials_cache.values():
            # 認証情報を暗号化
            encrypted_creds = {}
            if self._fernet and cred.credentials:
                for key, value in cred.credentials.items():
                    try:
                        encrypted_value = (
                            self._fernet.encrypt(value.encode()).decode()
                        )
                        encrypted_creds[key] = encrypted_value
                    except Exception:
                        # 暗号化に失敗した場合はスキップ
                        continue
            
            cred_data = {
                "platform_type": cred.platform_type.value,
                "platform_id": cred.platform_id,
                "auth_type": cred.auth_type,
                "credentials": encrypted_creds,
                "expires_at": (
                    cred.expires_at.isoformat() if cred.expires_at else None
                ),
                "created_at": cred.created_at.isoformat(),
                "last_used": (
                    cred.last_used.isoformat() if cred.last_used else None
                )
            }
            data.append(cred_data)
        
        async with aiofiles.open(
            self.credentials_file, 'w', encoding='utf-8'
        ) as f:
            await f.write(
                json.dumps(data, ensure_ascii=False, indent=2)
            )

    # 公開メソッド
    
    async def get_settings(self) -> IntegrationSettings:
        """統合設定を取得"""
        if not self._settings_cache:
            await self._load_settings()
        return self._settings_cache
    
    async def get_config(self) -> IntegrationSettings:
        """設定を取得（get_settingsのエイリアス）"""
        return await self.get_settings()
    
    async def save_config(self, config: IntegrationSettings) -> None:
        """設定を保存"""
        self._settings_cache = config
        await self._save_settings()

    async def update_settings(self, **kwargs) -> None:
        """統合設定を更新"""
        if not self._settings_cache:
            await self._load_settings()
        
        for key, value in kwargs.items():
            if hasattr(self._settings_cache, key):
                setattr(self._settings_cache, key, value)
        
        self._settings_cache.updated_at = datetime.now()
        await self._save_settings()

    async def get_sync_rules(
        self, 
        data_type: Optional[DataType] = None,
        enabled_only: bool = True
    ) -> List[SyncRule]:
        """同期ルールを取得"""
        rules = list(self._sync_rules_cache.values())
        
        if data_type:
            rules = [r for r in rules if r.data_type == data_type]
        
        if enabled_only:
            rules = [r for r in rules if r.enabled]
        
        return rules

    async def add_sync_rule(self, rule: SyncRule) -> None:
        """同期ルールを追加"""
        self._sync_rules_cache[rule.id] = rule
        await self._save_sync_rules()

    async def update_sync_rule(self, rule_id: str, **kwargs) -> bool:
        """同期ルールを更新"""
        if rule_id not in self._sync_rules_cache:
            return False
        
        rule = self._sync_rules_cache[rule_id]
        for key, value in kwargs.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        
        rule.updated_at = datetime.now()
        await self._save_sync_rules()
        return True

    async def remove_sync_rule(self, rule_id: str) -> bool:
        """同期ルールを削除"""
        if rule_id in self._sync_rules_cache:
            del self._sync_rules_cache[rule_id]
            await self._save_sync_rules()
            return True
        return False

    async def get_credentials(
        self, 
        platform_type: PlatformType, 
        platform_id: str
    ) -> Optional[PlatformCredentials]:
        """認証情報を取得"""
        key = f"{platform_type.value}_{platform_id}"
        return self._credentials_cache.get(key)

    async def store_credentials(self, credentials: PlatformCredentials) -> None:
        """認証情報を保存"""
        key = f"{credentials.platform_type.value}_{credentials.platform_id}"
        self._credentials_cache[key] = credentials
        await self._save_credentials()

    async def remove_credentials(
        self, 
        platform_type: PlatformType, 
        platform_id: str
    ) -> bool:
        """認証情報を削除"""
        key = f"{platform_type.value}_{platform_id}"
        if key in self._credentials_cache:
            del self._credentials_cache[key]
            await self._save_credentials()
            return True
        return False

    async def cleanup_expired_credentials(self) -> int:
        """期限切れの認証情報をクリーンアップ"""
        now = datetime.now()
        expired_keys = []
        
        for key, cred in self._credentials_cache.items():
            if cred.expires_at and cred.expires_at < now:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._credentials_cache[key]
        
        if expired_keys:
            await self._save_credentials()
        
        return len(expired_keys)

    async def get_platform_config(
        self, 
        platform_type: PlatformType
    ) -> Dict[str, Any]:
        """プラットフォーム固有の設定を取得"""
        settings = await self.get_settings()
        platform_key = f"platform_{platform_type.value}"
        return settings.custom_settings.get(platform_key, {})

    async def update_platform_config(
        self,
        platform_type: PlatformType,
        config: Dict[str, Any]
    ) -> None:
        """プラットフォーム固有の設定を更新"""
        settings = await self.get_settings()
        platform_key = f"platform_{platform_type.value}"
        settings.custom_settings[platform_key] = config
        settings.updated_at = datetime.now()
        await self._save_settings()

    def encrypt_data(self, data: str) -> str:
        """データを暗号化"""
        if not self._fernet:
            raise ValueError("暗号化キーが初期化されていません")
        return self._fernet.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data: str) -> str:
        """データを復号化"""
        if not self._fernet:
            raise ValueError("暗号化キーが初期化されていません")
        return self._fernet.decrypt(encrypted_data.encode()).decode()

    async def export_config(
        self, include_credentials: bool = False
    ) -> Dict[str, Any]:
        """設定をエクスポート"""
        settings = await self.get_settings()
        sync_rules = await self.get_sync_rules(enabled_only=False)
        
        export_data = {
            "settings": {
                "user_id": settings.user_id,
                "encryption_enabled": settings.encryption_enabled,
                "auto_sync_enabled": settings.auto_sync_enabled,
                "conflict_resolution": settings.conflict_resolution,
                "max_sync_retries": settings.max_sync_retries,
                "sync_timeout": settings.sync_timeout,
                "data_retention_days": settings.data_retention_days,
                "allowed_platforms": [
                    p.value for p in settings.allowed_platforms
                ],
                "blocked_data_types": [
                    d.value for d in settings.blocked_data_types
                ],
                "custom_settings": settings.custom_settings,
                "created_at": settings.created_at.isoformat(),
                "updated_at": settings.updated_at.isoformat()
            },
            "sync_rules": [
                {
                    "id": rule.id,
                    "name": rule.name,
                    "data_type": rule.data_type.value,
                    "source_platforms": [
                        p.value for p in rule.source_platforms
                    ],
                    "target_platforms": [
                        p.value for p in rule.target_platforms
                    ],
                    "frequency": rule.frequency.value,
                    "security_level": rule.security_level.value,
                    "filters": rule.filters,
                    "transformations": rule.transformations,
                    "enabled": rule.enabled,
                    "created_at": rule.created_at.isoformat(),
                    "updated_at": rule.updated_at.isoformat()
                }
                for rule in sync_rules
            ]
        }
        
        if include_credentials:
            export_data["credentials"] = [
                {
                    "platform_type": cred.platform_type.value,
                    "platform_id": cred.platform_id,
                    "auth_type": cred.auth_type,
                    "expires_at": (
                        cred.expires_at.isoformat() 
                        if cred.expires_at else None
                    ),
                    "created_at": cred.created_at.isoformat(),
                    "last_used": (
                        cred.last_used.isoformat() 
                        if cred.last_used else None
                    )
                    # 認証情報自体は含めない（セキュリティ上の理由）
                }
                for cred in self._credentials_cache.values()
            ]
        
        return export_data

    async def import_config(self, config_data: Dict[str, Any]) -> bool:
        """設定をインポート"""
        try:
            # 設定をインポート
            if "settings" in config_data:
                settings_data = config_data["settings"]
                # Enum型に変換
                if "allowed_platforms" in settings_data:
                    settings_data["allowed_platforms"] = [
                        PlatformType(p) for p in settings_data["allowed_platforms"]
                    ]
                if "blocked_data_types" in settings_data:
                    settings_data["blocked_data_types"] = [
                        DataType(d) for d in settings_data["blocked_data_types"]
                    ]
                
                self._settings_cache = IntegrationSettings(**settings_data)
                await self._save_settings()
            
            # 同期ルールをインポート
            if "sync_rules" in config_data:
                self._sync_rules_cache = {}
                for rule_data in config_data["sync_rules"]:
                    # Enum型に変換
                    rule_data["data_type"] = DataType(rule_data["data_type"])
                    rule_data["source_platforms"] = [
                        PlatformType(p) for p in rule_data["source_platforms"]
                    ]
                    rule_data["target_platforms"] = [
                        PlatformType(p) 
                        for p in rule_data["target_platforms"]
                    ]
                    rule_data["frequency"] = SyncFrequency(rule_data["frequency"])
                    rule_data["security_level"] = SecurityLevel(
                        rule_data["security_level"]
                    )
                    
                    rule = SyncRule(**rule_data)
                    self._sync_rules_cache[rule.id] = rule
                
                await self._save_sync_rules()
            
            return True
            
        except Exception:
            return False

    async def load_config(self) -> IntegrationConfig:
        """統合設定を読み込んでIntegrationConfigオブジェクトを返す"""
        await self.initialize()
        
        settings = await self.get_settings()
        sync_rules = await self.get_sync_rules(enabled_only=False)
        credentials = list(self._credentials_cache.values())
        
        return IntegrationConfig(
            settings=settings,
            sync_rules=sync_rules,
            credentials=credentials
        )

    async def get_status(self) -> Dict[str, Any]:
        """設定管理システムのステータスを取得"""
        settings = await self.get_settings()
        sync_rules = await self.get_sync_rules(enabled_only=False)
        
        return {
            "user_id": settings.user_id,
            "encryption_enabled": settings.encryption_enabled,
            "auto_sync_enabled": settings.auto_sync_enabled,
            "total_sync_rules": len(sync_rules),
            "enabled_sync_rules": len([r for r in sync_rules if r.enabled]),
            "total_credentials": len(self._credentials_cache),
            "allowed_platforms": [
                p.value for p in settings.allowed_platforms
            ],
            "blocked_data_types": [
                d.value for d in settings.blocked_data_types
            ],
            "config_files": {
                "settings": self.settings_file.exists(),
                "sync_rules": self.sync_rules_file.exists(),
                "credentials": self.credentials_file.exists(),
                "encryption_key": self.encryption_key_file.exists()
            }
        }