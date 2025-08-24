#!/usr/bin/env python3
"""記憶同期システムのテスト"""

import asyncio
import json
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
                    {"role": "assistant", "content": "こんにちは！何かお手伝いできることはありますか？"}
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


class MockCrossPlatformSystem:
    """テスト用クロスプラットフォームシステム"""
    
    def __init__(self):
        self.platforms = {
            "browser": {"status": "connected"},
            "obsidian": {"status": "connected"},
            "raycast": {"status": "connected"}
        }
        self.sync_data_calls = []
        self.event_handlers = {}
    
    def add_event_handler(self, event_type, handler):
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def sync_data(self, data_id, data_type, content, source_platform, target_platforms):
        self.sync_data_calls.append({
            "data_id": data_id,
            "data_type": data_type,
            "content": content,
            "source_platform": source_platform,
            "target_platforms": target_platforms
        })
        return True


async def test_memory_sync_system():
    """記憶同期システムのテスト"""
    print("=== 記憶同期システムテスト開始 ===")
    
    try:
        # モジュールのインポートテスト
        print("1. モジュールインポートテスト...")
        from aoi.integration.memory_sync import MemorySyncManager, MemorySnapshot
        from aoi.integration.cross_platform_system import DataType
        print("✓ インポート成功")
        
        # モックシステムの初期化
        print("\n2. システム初期化テスト...")
        mock_cross_platform = MockCrossPlatformSystem()
        mock_memory_manager = MockMemoryManager()
        
        memory_sync = MemorySyncManager(
            cross_platform_system=mock_cross_platform,
            memory_manager=mock_memory_manager
        )
        print("✓ システム初期化成功")
        
        # メモリスナップショット作成テスト
        print("\n3. メモリスナップショット作成テスト...")
        snapshot = await memory_sync.create_memory_snapshot("browser")
        
        assert snapshot.platform_id == "browser"
        assert isinstance(snapshot.conversation_history, list)
        assert isinstance(snapshot.knowledge_base, list)
        assert isinstance(snapshot.context_data, dict)
        assert isinstance(snapshot.personality_state, dict)
        print(f"✓ スナップショット作成成功 (ID: {snapshot.snapshot_id})")
        
        # プラットフォーム同期テスト
        print("\n4. プラットフォーム同期テスト...")
        sync_result = await memory_sync.sync_platform_memory("browser")
        
        assert sync_result == True
        assert len(mock_cross_platform.sync_data_calls) > 0
        print(f"✓ 同期成功 ({len(mock_cross_platform.sync_data_calls)} 件のデータ同期)")
        
        # 同期ステータス確認テスト
        print("\n5. 同期ステータス確認テスト...")
        status = await memory_sync.get_sync_status("browser")
        
        assert status["platform_id"] == "browser"
        assert status["last_sync"] is not None
        assert isinstance(status["is_syncing"], bool)
        assert isinstance(status["auto_sync_enabled"], bool)
        print("✓ ステータス確認成功")
        
        # 全プラットフォーム同期テスト
        print("\n6. 全プラットフォーム同期テスト...")
        full_sync_results = await memory_sync.force_full_sync()
        
        assert len(full_sync_results) == 3  # browser, obsidian, raycast
        assert all(result for result in full_sync_results.values())
        print("✓ 全プラットフォーム同期成功")
        
        # スナップショットエクスポート/インポートテスト
        print("\n7. スナップショットエクスポート/インポートテスト...")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            export_path = tmp_file.name
        
        export_result = await memory_sync.export_memory_snapshot("browser", export_path)
        assert export_result == True
        
        # ファイルが作成されたか確認
        assert Path(export_path).exists()
        
        # インポートテスト
        import_result = await memory_sync.import_memory_snapshot("obsidian", export_path)
        assert import_result == True
        
        # クリーンアップ
        Path(export_path).unlink()
        print("✓ エクスポート/インポート成功")
        
        # 古い競合クリーンアップテスト
        print("\n8. 競合クリーンアップテスト...")
        cleaned_count = await memory_sync.cleanup_old_conflicts(max_age_hours=0)
        print(f"✓ クリーンアップ完了 ({cleaned_count} 件の古い競合を削除)")
        
        print("\n=== 全テスト成功！ ===")
        
        # 詳細情報の表示
        print("\n=== テスト結果詳細 ===")
        print(f"作成されたスナップショット: {snapshot.snapshot_id}")
        print(f"同期されたデータ件数: {len(mock_cross_platform.sync_data_calls)}")
        print(f"最終同期時刻: {status['last_sync']}")
        print(f"自動同期設定: {status['auto_sync_enabled']}")
        print(f"同期間隔: {status['sync_interval']} 秒")
        
        # 同期されたデータの詳細
        print("\n=== 同期データ詳細 ===")
        for i, call in enumerate(mock_cross_platform.sync_data_calls[:5]):  # 最初の5件のみ表示
            print(f"{i+1}. {call['data_type']} - {call['data_id']}")
            print(f"   ソース: {call['source_platform']}")
            print(f"   ターゲット: {call['target_platforms']}")
        
        if len(mock_cross_platform.sync_data_calls) > 5:
            print(f"   ... 他 {len(mock_cross_platform.sync_data_calls) - 5} 件")
        
        return True
        
    except Exception as e:
        print(f"\n❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_memory_sync_system())
    if result:
        print("\n🎉 記憶同期システムテスト完了！")
    else:
        print("\n💥 テスト失敗")
        exit(1)