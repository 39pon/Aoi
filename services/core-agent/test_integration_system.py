#!/usr/bin/env python3
"""統合システムのテストスクリプト

クロスプラットフォーム統合システムの動作確認と
スケーラビリティテストを実行
"""

import asyncio
import json
import time
from datetime import datetime

try:
    import psutil
except ImportError:
    psutil = None

# 統合システムをインポート
from aoi.integration import (
    initialize_integration_system,
    get_system_info,
    EventType,
    EventPriority,
    publish_event,
    subscribe_to_event,
    PlatformType,
    DataType
)


class IntegrationSystemTester:
    """統合システムのテスター"""
    
    def __init__(self):
        self.system = None
        self.test_results = []
        self.performance_metrics = {}
    
    async def run_all_tests(self):
        """全テストを実行"""
        print("=" * 60)
        print("Aoi統合システム テスト開始")
        print("=" * 60)
        
        # システム情報を表示
        await self.test_system_info()
        
        # 基本機能テスト
        await self.test_system_initialization()
        await self.test_event_system()
        await self.test_platform_adapters()
        await self.test_data_sync()
        await self.test_configuration_management()
        
        # スケーラビリティテスト
        await self.test_scalability()
        
        # パフォーマンステスト
        await self.test_performance()
        
        # 結果を表示
        await self.display_results()
        
        # クリーンアップ
        await self.cleanup()
    
    async def test_system_info(self):
        """システム情報テスト"""
        print("\n📋 システム情報テスト")
        print("-" * 40)
        
        try:
            info = get_system_info()
            print(f"システム名: {info['name']}")
            print(f"バージョン: {info['version']}")
            print(f"作成者: {info['author']}")
            print(f"説明: {info['description']}")
            
            print("\n対応プラットフォーム:")
            for platform in info['supported_platforms']:
                print(f"  - {platform}")
            
            print("\n機能:")
            for feature in info['features']:
                print(f"  - {feature}")
            
            self.test_results.append({
                "test": "system_info",
                "status": "PASS",
                "message": "システム情報の取得に成功"
            })
            
        except Exception as e:
            self.test_results.append({
                "test": "system_info",
                "status": "FAIL",
                "message": f"エラー: {str(e)}"
            })
    
    async def test_system_initialization(self):
        """システム初期化テスト"""
        print("\n🚀 システム初期化テスト")
        print("-" * 40)
        
        try:
            start_time = time.time()
            
            # システムを初期化
            self.system = await initialize_integration_system(
                "test_config.json"
            )
            
            init_time = time.time() - start_time
            self.performance_metrics["initialization_time"] = init_time
            
            print(f"✅ システム初期化完了 ({init_time:.2f}秒)")
            print(f"プラットフォーム数: {len(self.system.platforms)}")
            
            # システム状態を確認
            status = await self.system.get_sync_status()
            print(f"同期ステータス: {status}")
            
            self.test_results.append({
                "test": "system_initialization",
                "status": "PASS",
                "message": f"初期化時間: {init_time:.2f}秒"
            })
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"❌ システム初期化エラー: {str(e)}")
            print(f"詳細: {error_details}")
            self.test_results.append({
                "test": "system_initialization",
                "status": "FAIL",
                "message": f"エラー: {str(e)}"
            })
    
    async def test_event_system(self):
        """イベントシステムテスト"""
        print("\n📡 イベントシステムテスト")
        print("-" * 40)
        
        try:
            event_received = False
            received_data = None
            
            # イベントハンドラーを登録
            def test_handler(event):
                nonlocal event_received, received_data
                event_received = True
                received_data = event.data
                print(f"📨 イベント受信: {event.type.value}")
                return True
            
            subscribe_to_event(
                EventType.DATA_CREATED, 
                test_handler
            )
            
            # テストイベントを発行
            test_data = {
                "test_key": "test_value", 
                "timestamp": datetime.now().isoformat()
            }
            
            await publish_event(
                EventType.DATA_CREATED,
                "test_source",
                data=test_data,
                priority=EventPriority.HIGH
            )
            
            # イベント処理を待機
            await asyncio.sleep(0.5)
            
            if event_received and received_data == test_data:
                print("✅ イベント送受信成功")
                self.test_results.append({
                    "test": "event_system",
                    "status": "PASS",
                    "message": "イベントシステム正常動作"
                })
            else:
                raise Exception("イベントが正しく処理されませんでした")
            
        except Exception as e:
            self.test_results.append({
                "test": "event_system",
                "status": "FAIL",
                "message": f"エラー: {str(e)}"
            })
    
    async def test_platform_adapters(self):
        """プラットフォームアダプターテスト"""
        print("\n🔌 プラットフォームアダプターテスト")
        print("-" * 40)
        
        try:
            if not self.system:
                raise Exception("システムが初期化されていません")
            
            # テストプラットフォームを登録
            test_platform = {
                "id": "test_platform",
                "type": PlatformType.BROWSER,
                "name": "Test Platform",
                "config": {"test": True}
            }
            
            platform_id = await self.system.register_platform(
                test_platform["type"],
                "1.0.0",
                ["test", "sync"]
            )
            
            print(f"✅ プラットフォーム登録成功: {platform_id}")
            
            # プラットフォーム一覧を確認
            platforms = list(self.system.platforms.keys())
            print(f"登録済みプラットフォーム: {platforms}")
            
            # プラットフォームを解除
            await self.system.unregister_platform(platform_id)
            print(f"✅ プラットフォーム解除成功: {platform_id}")
            
            self.test_results.append({
                "test": "platform_adapters",
                "status": "PASS",
                "message": "プラットフォームアダプター正常動作"
            })
            
        except Exception as e:
            self.test_results.append({
                "test": "platform_adapters",
                "status": "FAIL",
                "message": f"エラー: {str(e)}"
            })
    
    async def test_data_sync(self):
        """データ同期テスト"""
        print("\n🔄 データ同期テスト")
        print("-" * 40)
        
        try:
            if not self.system:
                raise Exception("システムが初期化されていません")
            
            # テストデータを作成
            test_data = {
                "id": "test_data_001",
                "content": "これはテストデータです",
                "created_at": datetime.now().isoformat(),
                "tags": ["test", "integration"]
            }
            
            # データを同期
            sync_result = await self.system.sync_data(
                DataType.NOTE,
                test_data,
                "test_platform"
            )
            
            print(f"✅ データ同期実行: {sync_result}")
            
            # 同期ステータスを確認
            status = await self.system.get_sync_status()
            print(f"同期ステータス: {status}")
            
            self.test_results.append({
                "test": "data_sync",
                "status": "PASS",
                "message": "データ同期機能正常動作"
            })
            
        except Exception as e:
            self.test_results.append({
                "test": "data_sync",
                "status": "FAIL",
                "message": f"エラー: {str(e)}"
            })
    
    async def test_configuration_management(self):
        """設定管理テスト"""
        print("\n⚙️ 設定管理テスト")
        print("-" * 40)
        
        try:
            if not self.system:
                raise Exception("システムが初期化されていません")
            
            # 設定を取得
            config = await self.system.config_manager.get_config()
            print(f"✅ 設定取得成功: {len(config.__dict__)} 項目")
            print(f"🔍 デバッグ: config型 = {type(config)}")
            print(f"🔍 デバッグ: config内容 = {config}")
            sync_interval_type = type(getattr(config, 'sync_interval', 'NOT_FOUND'))
            sync_interval_value = getattr(config, 'sync_interval', 'NOT_FOUND')
            print(f"🔍 デバッグ: sync_interval型 = {sync_interval_type}")
            print(f"🔍 デバッグ: sync_interval値 = {sync_interval_value}")
            
            # 設定を更新
            original_interval = config.sync_interval
            config.sync_interval = 30
            
            await self.system.config_manager.save_config(config)
            print(f"✅ 設定更新成功: sync_interval {original_interval} -> 30")
            
            # 設定を復元
            config.sync_interval = original_interval
            await self.system.config_manager.save_config(config)
            print(f"✅ 設定復元成功: sync_interval -> {original_interval}")
            
            self.test_results.append({
                "test": "configuration_management",
                "status": "PASS",
                "message": "設定管理機能正常動作"
            })
            
        except Exception as e:
            self.test_results.append({
                "test": "configuration_management",
                "status": "FAIL",
                "message": f"エラー: {str(e)}"
            })
    
    async def test_scalability(self):
        """スケーラビリティテスト"""
        print("\n📈 スケーラビリティテスト")
        print("-" * 40)
        
        try:
            # 大量イベント処理テスト
            event_count = 1000
            start_time = time.time()
            
            print(f"大量イベント処理テスト開始 ({event_count}件)...")
            
            # 並行してイベントを発行
            tasks = []
            for i in range(event_count):
                task = publish_event(
                    EventType.DATA_UPDATED,
                    f"test_source_{i % 10}",
                    data={"index": i, "batch": "scalability_test"},
                    priority=EventPriority.NORMAL
                )
                tasks.append(task)
            
            # 全イベントの発行を待機
            await asyncio.gather(*tasks)
            
            # 処理完了を待機
            await asyncio.sleep(2.0)
            
            processing_time = time.time() - start_time
            events_per_second = event_count / processing_time
            
            metrics = self.performance_metrics
            metrics["scalability_events_count"] = event_count
            metrics["scalability_processing_time"] = processing_time
            metrics["scalability_events_per_second"] = events_per_second
            
            print("✅ 大量イベント処理完了")
            print(f"   処理時間: {processing_time:.2f}秒")
            print(f"   処理速度: {events_per_second:.0f}件/秒")
            
            # 複数プラットフォーム同時接続テスト
            platform_count = 50
            print(f"\n複数プラットフォーム接続テスト ({platform_count}件)...")
            
            start_time = time.time()
            
            # 複数のプラットフォームを並行登録
            registration_tasks = []
            for i in range(platform_count):
                task = self.system.register_platform(
                    f"scale_test_platform_{i}",
                    PlatformType.BROWSER,
                    {"test_id": i, "batch": "scalability"}
                )
                registration_tasks.append(task)
            
            await asyncio.gather(*registration_tasks, return_exceptions=True)
            
            registration_time = time.time() - start_time
            platforms_per_second = platform_count / registration_time
            
            metrics["scalability_platforms_count"] = platform_count
            metrics["scalability_registration_time"] = registration_time
            metrics["scalability_platforms_per_second"] = platforms_per_second
            
            print("✅ 複数プラットフォーム登録完了")
            print(f"   登録時間: {registration_time:.2f}秒")
            print(f"   登録速度: {platforms_per_second:.0f}件/秒")
            total_platforms = len(self.system.platforms)
            print(f"   総プラットフォーム数: {total_platforms}")
            
            # クリーンアップ
            cleanup_tasks = []
            for i in range(platform_count):
                task = self.system.unregister_platform(
                    f"scale_test_platform_{i}"
                )
                cleanup_tasks.append(task)
            
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
            print("✅ テストプラットフォームクリーンアップ完了")
            
            success_msg = (
                f"スケーラビリティテスト成功 "
                f"({events_per_second:.0f}件/秒, "
                f"{platforms_per_second:.0f}プラットフォーム/秒)"
            )
            self.test_results.append({
                "test": "scalability",
                "status": "PASS",
                "message": success_msg
            })
            
        except Exception as e:
            self.test_results.append({
                "test": "scalability",
                "status": "FAIL",
                "message": f"エラー: {str(e)}"
            })
    
    async def test_performance(self):
        """パフォーマンステスト"""
        print("\n⚡ パフォーマンステスト")
        print("-" * 40)
        
        try:
            # メモリ使用量テスト
            if psutil:
                process = psutil.Process()
                memory_before = process.memory_info().rss / 1024 / 1024
            else:
                memory_before = 0
            
            # 大量データ処理
            data_count = 5000
            print(f"大量データ処理テスト ({data_count}件)...")
            
            start_time = time.time()
            
            # 大量のデータを作成・処理
            for i in range(data_count):
                test_data = {
                    "id": f"perf_test_{i}",
                    "content": f"パフォーマンステストデータ {i}" * 10,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {"index": i, "batch": "performance"}
                }
                
                # データ処理をシミュレート
                await self.system._process_data(test_data)
            
            processing_time = time.time() - start_time
            data_per_second = data_count / processing_time
            
            if psutil:
                process = psutil.Process()
                memory_after = process.memory_info().rss / 1024 / 1024
            else:
                memory_after = 0
            memory_usage = memory_after - memory_before
            
            metrics = self.performance_metrics
            metrics["performance_data_count"] = data_count
            metrics["performance_processing_time"] = processing_time
            metrics["performance_data_per_second"] = data_per_second
            metrics["performance_memory_usage"] = memory_usage
            
            print("✅ 大量データ処理完了")
            print(f"   処理時間: {processing_time:.2f}秒")
            print(f"   処理速度: {data_per_second:.0f}件/秒")
            print(f"   メモリ使用量: {memory_usage:.1f}MB")
            
            perf_msg = (
                f"パフォーマンステスト成功 "
                f"({data_per_second:.0f}件/秒, "
                f"{memory_usage:.1f}MB)"
            )
            self.test_results.append({
                "test": "performance",
                "status": "PASS",
                "message": perf_msg
            })
            
        except Exception as e:
            self.test_results.append({
                "test": "performance",
                "status": "FAIL",
                "message": f"エラー: {str(e)}"
            })
    
    async def display_results(self):
        """テスト結果を表示"""
        print("\n" + "=" * 60)
        print("テスト結果サマリー")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["status"] == "PASS")
        failed = sum(1 for result in self.test_results if result["status"] == "FAIL")
        total = len(self.test_results)
        
        print(f"\n📊 総合結果: {passed}/{total} テスト成功")
        print(f"✅ 成功: {passed}")
        print(f"❌ 失敗: {failed}")
        
        print("\n📋 詳細結果:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            print(f"  {status_icon} {result['test']}: {result['message']}")
        
        if self.performance_metrics:
            print("\n⚡ パフォーマンス指標:")
            for metric, value in self.performance_metrics.items():
                if isinstance(value, float):
                    print(f"  - {metric}: {value:.2f}")
                else:
                    print(f"  - {metric}: {value}")
        
        # 結果をJSONファイルに保存
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "success_rate": (
                    (passed / total * 100) if total > 0 else 0
                )
            },
            "test_results": self.test_results,
            "performance_metrics": self.performance_metrics
        }
        
        filename = "integration_test_results.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 テスト結果を保存: {filename}")
    
    async def cleanup(self):
        """クリーンアップ"""
        print("\n🧹 クリーンアップ中...")
        
        try:
            if self.system:
                await self.system.stop_sync_service()
                print("✅ システム停止完了")
        except Exception as e:
            print(f"⚠️ クリーンアップエラー: {e}")


async def main():
    """メイン関数"""
    tester = IntegrationSystemTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())