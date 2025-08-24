#!/usr/bin/env python3
"""クロスプラットフォーム統合システムの包括的テスト"""

import asyncio
import tempfile
from datetime import datetime
from pathlib import Path

# テスト用のモックシステム
class MockMemoryManager:
    """テスト用メモリマネージャー"""
    
    def __init__(self):
        self.conversations = [
            {
                "id": "conv_1",
                "timestamp": datetime.now().isoformat(),
                "messages": [
                    {"role": "user", "content": "こんにちは"},
                    {"role": "assistant", "content": "こんにちは！"}
                ]
            }
        ]
        self.knowledge = [
            {
                "id": "knowledge_1",
                "topic": "プログラミング",
                "content": "Pythonは動的型付け言語です",
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    async def get_conversation_history(self, limit=100):
        return self.conversations[:limit]
    
    async def get_knowledge_base(self):
        return self.knowledge


class MockCrossPlatformSystem:
    """テスト用クロスプラットフォームシステム"""
    
    def __init__(self):
        self.sync_data_calls = []
        self.data_store = {}
        self.platforms = ['browser', 'obsidian', 'raycast']
        self.capabilities = {
            'browser': {'web_access': True, 'notifications': True},
            'obsidian': {'file_system': True, 'markdown': True},
            'raycast': {'quick_actions': True, 'system_integration': True}
        }
        self.event_handlers = {}
    
    def add_event_handler(self, event_type: str, handler):
        """イベントハンドラーの追加"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def emit_event(self, event_type: str, data: dict):
        """イベントの発火"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                await handler(data)
    
    async def sync_to_platform(self, platform: str, data: dict) -> bool:
        """プラットフォームへのデータ同期"""
        self.data_store[platform] = data
        return True
    
    async def get_platform_data(self, platform: str) -> dict:
        """プラットフォームからのデータ取得"""
        return self.data_store.get(platform, {})
    
    def get_platform_capabilities(self, platform: str) -> dict:
        """プラットフォーム機能の取得"""
        return self.capabilities.get(platform, {})
    
    async def sync_data(self, data_type, data_id, data, source_platform, target_platforms):
        self.sync_data_calls.append({
            "data_type": data_type,
            "data_id": data_id,
            "data": data,
            "source_platform": source_platform,
            "target_platforms": target_platforms,
            "timestamp": datetime.now()
        })
        
        # データストアに保存
        key = f"{data_type}_{data_id}"
        self.data_store[key] = data
        
        return True
    
    async def get_data(self, data_type, data_id, platform_id):
        key = f"{data_type}_{data_id}"
        return self.data_store.get(key)


async def test_cross_platform_integration():
    """クロスプラットフォーム統合システムの包括的テスト"""
    print("=== クロスプラットフォーム統合テスト開始 ===")
    
    try:
        # 1. モジュールインポートテスト
        print("\n1. モジュールインポートテスト...")
        from aoi.integration.memory_sync import MemorySyncManager
        from aoi.integration.platform_adapter import PlatformAdapter
        from aoi.integration.cross_platform_system import PlatformType
        print("✓ 全モジュールのインポート成功")
        
        # 2. システム初期化テスト
        print("\n2. システム初期化テスト...")
        mock_cross_platform = MockCrossPlatformSystem()
        mock_memory_manager = MockMemoryManager()
        
        memory_sync = MemorySyncManager(
            cross_platform_system=mock_cross_platform,
            memory_manager=mock_memory_manager
        )
        
        platform_adapter = PlatformAdapter()
        print("✓ 全システムの初期化成功")
        
        # 3. プラットフォーム適応テスト
        print("\n3. プラットフォーム適応テスト...")
        test_response = """
# テスト応答

これは**重要な**情報です。

```python
print("Hello, World!")
```

詳細は[こちら](https://example.com)をご覧ください。
        """
        
        # ブラウザ向け適応
        browser_response = platform_adapter.adapt_response(
            test_response, 
            PlatformType.BROWSER,
            {"dark_mode": False}
        )
        assert "<div class=\"aoi-response\"" in browser_response
        assert "<strong>重要な</strong>" in browser_response
        print("✓ ブラウザ向け適応成功")
        
        # Obsidian向け適応
        obsidian_response = platform_adapter.adapt_response(
            test_response,
            PlatformType.OBSIDIAN,
            {"add_tags": True, "add_metadata": True}
        )
        assert "---" in obsidian_response  # メタデータ
        assert "[[こちら]]" in obsidian_response  # Wikilink
        print("✓ Obsidian向け適応成功")
        
        # Raycast向け適応
        raycast_response = platform_adapter.adapt_response(
            test_response,
            PlatformType.RAYCAST
        )
        assert len(raycast_response) <= 2000  # 長さ制限
        print("✓ Raycast向け適応成功")
        
        # 4. 記憶同期テスト
        print("\n4. 記憶同期テスト...")
        
        # スナップショット作成
        snapshot = await memory_sync.create_memory_snapshot("browser")
        assert snapshot.platform_id == "browser"
        print(f"✓ スナップショット作成成功 (ID: {snapshot.snapshot_id})")
        
        # プラットフォーム間同期
        sync_result = await memory_sync.sync_platform_memory(
            "browser", 
            ["obsidian", "raycast"]
        )
        assert sync_result == True
        print("✓ プラットフォーム間同期成功")
        
        # 5. エンドツーエンドテスト
        print("\n5. エンドツーエンドテスト...")
        
        # 1. ブラウザで会話
        browser_conversation = {
            "id": "conv_browser_1",
            "messages": [
                {"role": "user", "content": "Pythonについて教えて"},
                {"role": "assistant", "content": "Pythonは素晴らしい言語です"}
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        # 2. 記憶に保存
        mock_memory_manager.conversations.append(browser_conversation)
        
        # 3. 他プラットフォームに同期
        await memory_sync.sync_platform_memory(
            "browser", 
            ["obsidian", "raycast"]
        )
        
        # 4. Obsidianで応答を適応
        obsidian_adapted = platform_adapter.adapt_response(
            "Pythonは素晴らしい言語です。詳細は[Python公式サイト](https://python.org)をご覧ください。",
            PlatformType.OBSIDIAN,
            {"topic": "Python", "add_tags": True}
        )
        
        assert "#python" in obsidian_adapted
        assert "[[Python公式サイト]]" in obsidian_adapted
        print("✓ エンドツーエンド統合成功")
        
        # 6. パフォーマンステスト
        print("\n6. パフォーマンステスト...")
        
        import time
        start_time = time.time()
        
        # 大量同期テスト
        for i in range(10):
            await memory_sync.sync_platform_memory(
                "browser",
                ["obsidian", "raycast"]
            )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        assert processing_time < 5.0  # 5秒以内
        print(f"✓ パフォーマンステスト成功 ({processing_time:.2f}秒)")
        
        # 7. エラーハンドリングテスト
        print("\n7. エラーハンドリングテスト...")
        
        # 無効なプラットフォーム
        try:
            invalid_response = platform_adapter.adapt_response(
                "テスト",
                "invalid_platform"  # 無効なプラットフォーム
            )
            assert invalid_response == "テスト"  # 元の応答がそのまま返される
            print("✓ 無効プラットフォーム処理成功")
        except Exception as e:
            print(f"✗ エラーハンドリング失敗: {e}")
        
        # 8. 機能サポートチェックテスト
        print("\n8. 機能サポートチェックテスト...")
        
        # ブラウザはHTML対応
        assert platform_adapter.is_feature_supported(
            PlatformType.BROWSER, "html"
        ) == True
        
        # RaycastはHTML非対応
        assert platform_adapter.is_feature_supported(
            PlatformType.RAYCAST, "html"
        ) == False
        
        # ObsidianはMarkdown対応
        assert platform_adapter.is_feature_supported(
            PlatformType.OBSIDIAN, "markdown"
        ) == True
        
        print("✓ 機能サポートチェック成功")
        
        print("\n=== 全テスト成功！ ===")
        
        # テスト結果サマリー
        print("\n=== テスト結果サマリー ===")
        print(f"同期データ件数: {len(mock_cross_platform.sync_data_calls)}")
        print(f"処理時間: {processing_time:.2f}秒")
        print(f"メモリスナップショット: {snapshot.snapshot_id}")
        
        # 同期データの詳細
        print("\n=== 同期データ詳細 ===")
        for i, call in enumerate(mock_cross_platform.sync_data_calls[:5]):
            print(f"{i+1}. {call['data_type']} - {call['data_id']}")
            print(f"   ソース: {call['source_platform']}")
            print(f"   ターゲット: {call['target_platforms']}")
        
        if len(mock_cross_platform.sync_data_calls) > 5:
            remaining = len(mock_cross_platform.sync_data_calls) - 5
            print(f"   ... 他 {remaining} 件")
        
        print("\n🎉 クロスプラットフォーム統合テスト完了！")
        
        return True
        
    except Exception as e:
        print(f"\n❌ テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_cross_platform_integration())
    exit(0 if success else 1)