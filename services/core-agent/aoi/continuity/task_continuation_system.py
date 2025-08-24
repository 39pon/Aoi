from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import asyncio
from pathlib import Path


class TaskStatus(Enum):
    """タスクステータス"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class ErrorType(Enum):
    """エラータイプ"""
    NETWORK_ERROR = "network_error"
    FILE_ERROR = "file_error"
    PERMISSION_ERROR = "permission_error"
    TIMEOUT_ERROR = "timeout_error"
    VALIDATION_ERROR = "validation_error"
    SYSTEM_ERROR = "system_error"
    USER_INTERRUPTION = "user_interruption"


@dataclass
class TaskStep:
    """タスクステップ"""
    step_id: str
    description: str
    status: TaskStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    error_type: Optional[ErrorType] = None
    retry_count: int = 0
    max_retries: int = 3
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskState:
    """タスク状態"""
    task_id: str
    title: str
    description: str
    status: TaskStatus
    steps: List[TaskStep] = field(default_factory=list)
    current_step_index: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    error_history: List[Dict[str, Any]] = field(default_factory=list)
    recovery_suggestions: List[str] = field(default_factory=list)


class TaskContinuationSystem:
    """作業継続システム"""
    
    def __init__(self, state_dir: str = "./task_states"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)
        self.active_tasks: Dict[str, TaskState] = {}
        self.error_handlers: Dict[ErrorType, callable] = {
            ErrorType.NETWORK_ERROR: self._handle_network_error,
            ErrorType.FILE_ERROR: self._handle_file_error,
            ErrorType.PERMISSION_ERROR: self._handle_permission_error,
            ErrorType.TIMEOUT_ERROR: self._handle_timeout_error,
            ErrorType.VALIDATION_ERROR: self._handle_validation_error,
            ErrorType.SYSTEM_ERROR: self._handle_system_error,
            ErrorType.USER_INTERRUPTION: self._handle_user_interruption,
        }
    
    async def create_task(
            self,
            task_id: str,
            title: str,
            description: str,
            steps: List[Dict[str, Any]]
    ) -> TaskState:
        """新しいタスクを作成"""
        task_steps = [
            TaskStep(
                step_id=step['id'],
                description=step['description'],
                status=TaskStatus.PENDING,
                max_retries=step.get('max_retries', 3),
                context=step.get('context', {})
            )
            for step in steps
        ]
        
        task_state = TaskState(
            task_id=task_id,
            title=title,
            description=description,
            status=TaskStatus.PENDING,
            steps=task_steps
        )
        
        self.active_tasks[task_id] = task_state
        await self._save_task_state(task_state)
        return task_state
    
    async def execute_task(self, task_id: str) -> TaskState:
        """タスクを実行"""
        task_state = self.active_tasks.get(task_id)
        if not task_state:
            task_state = await self._load_task_state(task_id)
            if not task_state:
                raise ValueError(f"Task {task_id} not found")
        
        task_state.status = TaskStatus.IN_PROGRESS
        task_state.updated_at = datetime.now()
        
        try:
            while task_state.current_step_index < len(task_state.steps):
                current_step = task_state.steps[task_state.current_step_index]
                
                if current_step.status == TaskStatus.COMPLETED:
                    task_state.current_step_index += 1
                    continue
                
                await self._execute_step(task_state, current_step)
                
                if current_step.status == TaskStatus.COMPLETED:
                    task_state.current_step_index += 1
                elif current_step.status == TaskStatus.FAILED:
                    if current_step.retry_count >= current_step.max_retries:
                        task_state.status = TaskStatus.FAILED
                        break
                    else:
                        await self._retry_step(task_state, current_step)
                elif current_step.status == TaskStatus.PAUSED:
                    task_state.status = TaskStatus.PAUSED
                    break
            
            if task_state.current_step_index >= len(task_state.steps):
                task_state.status = TaskStatus.COMPLETED
        
        except Exception as e:
            await self._handle_task_error(task_state, e)
        
        finally:
            task_state.updated_at = datetime.now()
            await self._save_task_state(task_state)
        
        return task_state
    
    async def continue_task(self, task_id: str) -> TaskState:
        """タスクを継続"""
        task_state = await self._load_task_state(task_id)
        if not task_state:
            raise ValueError(f"Task {task_id} not found")
        
        if task_state.status in [TaskStatus.PAUSED, TaskStatus.FAILED]:
            # 失敗したステップをリセット
            if task_state.status == TaskStatus.FAILED:
                current_step = task_state.steps[task_state.current_step_index]
                current_step.status = TaskStatus.PENDING
                current_step.error_message = None
                current_step.error_type = None
            
            task_state.status = TaskStatus.PENDING
            self.active_tasks[task_id] = task_state
            return await self.execute_task(task_id)
        
        return task_state
    
    async def pause_task(self, task_id: str) -> TaskState:
        """タスクを一時停止"""
        task_state = self.active_tasks.get(task_id)
        if task_state and task_state.status == TaskStatus.IN_PROGRESS:
            task_state.status = TaskStatus.PAUSED
            task_state.updated_at = datetime.now()
            await self._save_task_state(task_state)
        return task_state
    
    async def cancel_task(self, task_id: str) -> TaskState:
        """タスクをキャンセル"""
        task_state = self.active_tasks.get(task_id)
        if not task_state:
            task_state = await self._load_task_state(task_id)
        
        if task_state:
            task_state.status = TaskStatus.CANCELLED
            task_state.updated_at = datetime.now()
            await self._save_task_state(task_state)
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
        
        return task_state
    
    async def get_task_status(self, task_id: str) -> Optional[TaskState]:
        """タスクステータスを取得"""
        task_state = self.active_tasks.get(task_id)
        if not task_state:
            task_state = await self._load_task_state(task_id)
        return task_state
    
    async def list_tasks(
            self,
            status_filter: Optional[TaskStatus] = None
    ) -> List[TaskState]:
        """タスク一覧を取得"""
        tasks = []
        
        # アクティブなタスク
        for task_state in self.active_tasks.values():
            if not status_filter or task_state.status == status_filter:
                tasks.append(task_state)
        
        # 保存されたタスク
        for state_file in self.state_dir.glob("*.json"):
            task_id = state_file.stem
            if task_id not in self.active_tasks:
                task_state = await self._load_task_state(task_id)
                if task_state and (
                        not status_filter or 
                        task_state.status == status_filter
                ):
                    tasks.append(task_state)
        
        return sorted(tasks, key=lambda t: t.updated_at, reverse=True)
    
    async def _execute_step(
            self,
            task_state: TaskState,
            step: TaskStep
    ) -> None:
        """ステップを実行"""
        step.status = TaskStatus.IN_PROGRESS
        step.started_at = datetime.now()
        
        try:
            # 実際のステップ実行ロジック
            # ここでは模擬的な実装
            await asyncio.sleep(0.1)  # 実際の処理をシミュレート
            
            # ステップの種類に応じた処理
            step_type = step.context.get('type', 'default')
            if step_type == 'file_operation':
                await self._execute_file_operation(step)
            elif step_type == 'api_call':
                await self._execute_api_call(step)
            elif step_type == 'validation':
                await self._execute_validation(step)
            else:
                await self._execute_default_step(step)
            
            step.status = TaskStatus.COMPLETED
            step.completed_at = datetime.now()
        
        except Exception as e:
            await self._handle_step_error(task_state, step, e)
    
    async def _execute_file_operation(self, step: TaskStep) -> None:
        """ファイル操作を実行"""
        operation = step.context.get('operation')
        _ = step.context.get('file_path')  # 未使用変数を明示的に無視
        
        if operation == 'read':
            # ファイル読み取り処理
            pass
        elif operation == 'write':
            # ファイル書き込み処理
            pass
        elif operation == 'delete':
            # ファイル削除処理
            pass
    
    async def _execute_api_call(self, step: TaskStep) -> None:
        """API呼び出しを実行"""
        _ = step.context.get('url')  # 未使用変数を明示的に無視
        _ = step.context.get('method', 'GET')  # 未使用変数を明示的に無視
        # API呼び出し処理
        pass
    
    async def _execute_validation(self, step: TaskStep) -> None:
        """バリデーションを実行"""
        _ = step.context.get('validation_type')  # 未使用変数を明示的に無視
        # バリデーション処理
        pass
    
    async def _execute_default_step(self, step: TaskStep) -> None:
        """デフォルトステップを実行"""
        # デフォルト処理
        pass
    
    async def _retry_step(
            self,
            task_state: TaskState,
            step: TaskStep
    ) -> None:
        """ステップをリトライ"""
        step.retry_count += 1
        step.status = TaskStatus.PENDING
        step.error_message = None
        step.error_type = None
        
        # リトライ前の待機時間
        wait_time = min(2 ** step.retry_count, 30)  # 指数バックオフ
        await asyncio.sleep(wait_time)
        
        await self._execute_step(task_state, step)
    
    async def _handle_step_error(
            self,
            task_state: TaskState,
            step: TaskStep,
            error: Exception
    ) -> None:
        """ステップエラーを処理"""
        error_type = self._classify_error(error)
        step.error_type = error_type
        step.error_message = str(error)
        
        # エラー履歴に追加
        error_record = {
            'timestamp': datetime.now().isoformat(),
            'step_id': step.step_id,
            'error_type': error_type.value,
            'error_message': str(error),
            'retry_count': step.retry_count
        }
        task_state.error_history.append(error_record)
        
        # エラーハンドラーを実行
        handler = self.error_handlers.get(error_type)
        if handler:
            recovery_suggestion = await handler(task_state, step, error)
            if recovery_suggestion:
                task_state.recovery_suggestions.append(recovery_suggestion)
        
        # リトライ可能かチェック
        if step.retry_count < step.max_retries:
            step.status = TaskStatus.PENDING
        else:
            step.status = TaskStatus.FAILED
    
    async def _handle_task_error(
            self,
            task_state: TaskState,
            error: Exception
    ) -> None:
        """タスクレベルのエラーを処理"""
        task_state.status = TaskStatus.FAILED
        error_record = {
            'timestamp': datetime.now().isoformat(),
            'error_type': 'task_error',
            'error_message': str(error)
        }
        task_state.error_history.append(error_record)
    
    def _classify_error(self, error: Exception) -> ErrorType:
        """エラーを分類"""
        error_str = str(error).lower()
        
        if 'network' in error_str or 'connection' in error_str:
            return ErrorType.NETWORK_ERROR
        elif 'file' in error_str or 'directory' in error_str:
            return ErrorType.FILE_ERROR
        elif 'permission' in error_str or 'access' in error_str:
            return ErrorType.PERMISSION_ERROR
        elif 'timeout' in error_str:
            return ErrorType.TIMEOUT_ERROR
        elif 'validation' in error_str or 'invalid' in error_str:
            return ErrorType.VALIDATION_ERROR
        elif 'interrupt' in error_str or 'cancelled' in error_str:
            return ErrorType.USER_INTERRUPTION
        else:
            return ErrorType.SYSTEM_ERROR
    
    # エラーハンドラー
    async def _handle_network_error(
            self,
            task_state: TaskState,
            step: TaskStep,
            error: Exception
    ) -> str:
        """ネットワークエラーを処理"""
        return (
            "ネットワーク接続を確認してください。"
            "VPNやプロキシ設定も確認してください。"
        )
    
    async def _handle_file_error(
            self,
            task_state: TaskState,
            step: TaskStep,
            error: Exception
    ) -> str:
        """ファイルエラーを処理"""
        return (
            "ファイルパスとファイルの存在を確認してください。"
            "ディスク容量も確認してください。"
        )
    
    async def _handle_permission_error(
            self,
            task_state: TaskState,
            step: TaskStep,
            error: Exception
    ) -> str:
        """権限エラーを処理"""
        return (
            "ファイルやディレクトリの権限を確認してください。"
            "管理者権限が必要な場合があります。"
        )
    
    async def _handle_timeout_error(
            self,
            task_state: TaskState,
            step: TaskStep,
            error: Exception
    ) -> str:
        """タイムアウトエラーを処理"""
        return (
            "処理時間が長すぎます。タイムアウト設定を調整するか、"
            "処理を分割してください。"
        )
    
    async def _handle_validation_error(
            self,
            task_state: TaskState,
            step: TaskStep,
            error: Exception
    ) -> str:
        """バリデーションエラーを処理"""
        return (
            "入力データの形式や値を確認してください。"
            "必須フィールドが不足している可能性があります。"
        )
    
    async def _handle_system_error(
            self,
            task_state: TaskState,
            step: TaskStep,
            error: Exception
    ) -> str:
        """システムエラーを処理"""
        return (
            "システムエラーが発生しました。ログを確認し、"
            "必要に応じてシステムを再起動してください。"
        )
    
    async def _handle_user_interruption(
            self,
            task_state: TaskState,
            step: TaskStep,
            error: Exception
    ) -> str:
        """ユーザー中断を処理"""
        return (
            "ユーザーによって処理が中断されました。"
            "'継続'コマンドで作業を再開できます。"
        )
    
    async def _save_task_state(self, task_state: TaskState) -> None:
        """タスク状態を保存"""
        state_file = self.state_dir / f"{task_state.task_id}.json"
        
        # dataclassをJSONシリアライズ可能な形式に変換
        state_dict = {
            'task_id': task_state.task_id,
            'title': task_state.title,
            'description': task_state.description,
            'status': task_state.status.value,
            'current_step_index': task_state.current_step_index,
            'created_at': task_state.created_at.isoformat(),
            'updated_at': task_state.updated_at.isoformat(),
            'context': task_state.context,
            'error_history': task_state.error_history,
            'recovery_suggestions': (
                task_state.recovery_suggestions
            ),
            'steps': [
                {
                    'step_id': step.step_id,
                    'description': step.description,
                    'status': step.status.value,
                    'started_at': (
                        step.started_at.isoformat() 
                        if step.started_at else None
                    ),
                    'completed_at': (
                        step.completed_at.isoformat() 
                        if step.completed_at else None
                    ),
                    'error_message': step.error_message,
                    'error_type': (
                        step.error_type.value 
                        if step.error_type else None
                    ),
                    'retry_count': step.retry_count,
                    'max_retries': step.max_retries,
                    'context': step.context
                }
                for step in task_state.steps
            ]
        }
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state_dict, f, ensure_ascii=False, indent=2)
    
    async def _load_task_state(self, task_id: str) -> Optional[TaskState]:
        """タスク状態を読み込み"""
        state_file = self.state_dir / f"{task_id}.json"
        
        if not state_file.exists():
            return None
        
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state_dict = json.load(f)
            
            # JSONからdataclassに変換
            steps = [
                TaskStep(
                    step_id=step_data['step_id'],
                    description=step_data['description'],
                    status=TaskStatus(step_data['status']),
                    started_at=(
                        datetime.fromisoformat(step_data['started_at']) 
                        if step_data['started_at'] else None
                    ),
                    completed_at=(
                        datetime.fromisoformat(step_data['completed_at']) 
                        if step_data['completed_at'] else None
                    ),
                    error_message=step_data['error_message'],
                    error_type=(
                        ErrorType(step_data['error_type']) 
                        if step_data['error_type'] else None
                    ),
                    retry_count=step_data['retry_count'],
                    max_retries=step_data['max_retries'],
                    context=step_data['context']
                )
                for step_data in state_dict['steps']
            ]
            
            task_state = TaskState(
                task_id=state_dict['task_id'],
                title=state_dict['title'],
                description=state_dict['description'],
                status=TaskStatus(state_dict['status']),
                steps=steps,
                current_step_index=state_dict['current_step_index'],
                created_at=datetime.fromisoformat(state_dict['created_at']),
                updated_at=datetime.fromisoformat(state_dict['updated_at']),
                context=state_dict['context'],
                error_history=state_dict['error_history'],
                recovery_suggestions=state_dict['recovery_suggestions']
            )
            
            return task_state
        
        except Exception as e:
            print(f"Failed to load task state {task_id}: {e}")
            return None
    
    def format_task_status(self, task_state: TaskState) -> str:
        """タスクステータスをフォーマット"""
        status_icons = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.FAILED: "❌",
            TaskStatus.PAUSED: "⏸️",
            TaskStatus.CANCELLED: "🚫"
        }
        
        icon = status_icons.get(task_state.status, "❓")
        progress = f"{task_state.current_step_index}/{len(task_state.steps)}"
        
        status_text = f"{icon} **{task_state.title}** ({progress})\n"
        status_text += f"📝 {task_state.description}\n"
        status_text += (
            f"🕒 更新: "
            f"{task_state.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        
        if task_state.status == TaskStatus.FAILED and task_state.recovery_suggestions:
            status_text += "\n💡 **復旧提案:**\n"
            for suggestion in task_state.recovery_suggestions[-3:]:  # 最新3件
                status_text += f"• {suggestion}\n"
        
        if task_state.current_step_index < len(task_state.steps):
            current_step = task_state.steps[task_state.current_step_index]
            status_text += f"\n🎯 **現在のステップ:** {current_step.description}\n"
            
            if current_step.error_message:
                status_text += f"⚠️ **エラー:** {current_step.error_message}\n"
        
        return status_text