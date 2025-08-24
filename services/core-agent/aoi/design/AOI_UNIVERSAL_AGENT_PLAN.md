# 汎用AIエージェント「葵」実装計画

## 概要
本計画は、ブラウザ、Obsidian、Raycastで同一人格を持つ汎用AIエージェント「葵」の実装を目的とします。

## ユーザー要件
- **人格**: 世話焼きで優しいおっとりお姉さん
- **話し方**: 理論的で説得力のある話し方
- **エビデンス提示**: 質問に対して根拠・出典を提示
- **作業継続**: エラーハンドリングと「継続」コマンドによる作業再開
- **クロスプラットフォーム**: 同一人格での一貫した対話

## 1. 人格システム設計

### 1.1 コア人格特性
```python
class AoiCorePersonality:
    """
    葵の基本人格定義
    """
    PERSONALITY_TRAITS = {
        'caring': 0.9,          # 世話焼き度
        'gentle': 0.8,          # 優しさ
        'calm': 0.7,            # おっとり度
        'logical': 0.9,         # 論理性
        'persuasive': 0.8,      # 説得力
        'supportive': 0.9       # 支援性
    }
    
    SPEECH_PATTERNS = {
        'polite_level': 'medium',   # 丁寧語レベル（親近感重視）
        'explanation_style': 'step_by_step',  # 段階的説明
        'evidence_requirement': 'always',     # 常にエビデンス提示
        'tone': 'warm_casual'               # 温かみのあるカジュアル口調
    }
```

### 1.2 応答生成パターン
```python
class AoiResponseGenerator:
    """
    葵の応答生成システム
    """
    
    def generate_response(self, query: str, context: dict) -> str:
        """
        1. 質問理解・分析
        2. エビデンス収集
        3. 論理的構成
        4. 人格フィルター適用
        5. 最終応答生成
        """
        pass
    
    def add_evidence(self, response: str, sources: List[str]) -> str:
        """
        応答にエビデンス・出典を自動付与
        """
        pass
```

## 2. 自然言語理解システム

### 2.1 口語コマンド解析
```python
class NaturalLanguageProcessor:
    """
    口語での機能呼び出しを理解するシステム
    """
    
    def __init__(self):
        self.command_patterns = {
            # MCP関連
            'web_search': ['調べて', 'ググって', '検索して', '探して'],
            'ref_search': ['ドキュメント見て', '技術資料調べて', 'リファレンス確認'],
            'sequential_thinking': ['考えて', '分析して', '整理して'],
            
            # ファイル操作
            'file_create': ['ファイル作って', '新しいファイル', 'ファイル作成'],
            'file_edit': ['修正して', '変更して', '編集して', '直して'],
            'file_view': ['見せて', '確認して', '表示して'],
            
            # 開発関連
            'run_server': ['サーバー起動', '実行して', '動かして'],
            'install_deps': ['インストールして', 'パッケージ入れて'],
            'run_tests': ['テスト実行', 'テストして']
        }
    
    def parse_intent(self, user_input: str) -> dict:
        """
        ユーザーの口語入力から意図を解析
        
        例:
        "GitHubのAPIについて調べて" → {'action': 'web_search', 'query': 'GitHub API'}
        "このファイル修正して" → {'action': 'file_edit', 'target': 'current_file'}
        """
        pass
    
    def execute_natural_command(self, intent: dict) -> str:
        """
        解析した意図に基づいて適切なMCP/機能を実行
        """
        pass
```

### 2.2 コンテキスト理解
```python
class ContextualUnderstanding:
    """
    会話の文脈を理解して適切な機能を選択
    """
    
    def understand_context(self, conversation_history: List[str]) -> dict:
        """
        会話履歴から現在のコンテキストを理解
        
        例:
        - コーディング中 → ファイル操作、検索機能を優先
        - 調査中 → Web検索、文献検索を優先
        - 設計中 → 思考整理、分析機能を優先
        """
        pass
```

## 3. エビデンス提示システム

### 3.1 情報源統合
```python
class EvidenceSystem:
    """
    エビデンス収集・提示システム
    """
    
    def __init__(self):
        self.web_search = BraveSearchMCP()      # Web検索
        self.ref_search = RefMCP()              # 技術文献
        self.knowledge_base = LocalKnowledge()  # ローカル知識
    
    async def gather_evidence(self, query: str) -> List[Evidence]:
        """
        複数ソースからエビデンス収集
        """
        evidence_list = []
        
        # Web検索
        web_results = await self.web_search.search(query)
        evidence_list.extend(self._process_web_results(web_results))
        
        # 技術文献検索
        ref_results = await self.ref_search.search_documentation(query)
        evidence_list.extend(self._process_ref_results(ref_results))
        
        # 信頼性スコアリング
        return self._rank_by_reliability(evidence_list)
```

### 2.2 出典フォーマット
```python
class CitationFormatter:
    """
    出典・引用フォーマッター
    """
    
    def format_citation(self, evidence: Evidence) -> str:
        """
        エビデンスを適切な引用形式でフォーマット
        
        例:
        「この手法は効果的です。[1] 実際に、○○の研究では××という結果が報告されています。[2]
        
        [1] MDN Web Docs - JavaScript Best Practices
        [2] Stack Overflow Developer Survey 2023
        """
        pass
```

## 3. 作業継続システム

### 3.1 状態管理
```python
class TaskStateManager:
    """
    作業状態管理システム
    """
    
    def __init__(self):
        self.current_task = None
        self.task_history = []
        self.error_context = None
    
    def save_task_state(self, task: Task, progress: dict):
        """
        作業状態を保存
        """
        state = {
            'task_id': task.id,
            'progress': progress,
            'timestamp': datetime.now(),
            'context': task.context,
            'next_steps': task.get_next_steps()
        }
        self._persist_state(state)
    
    def handle_continuation(self, user_input: str) -> bool:
        """
        「継続」コマンドの処理
        """
        if user_input.strip() in ['継続', 'continue', '続き']:
            return self._resume_last_task()
        return False
```

### 3.2 エラーハンドリング
```python
class AoiErrorHandler:
    """
    葵のエラーハンドリングシステム
    """
    
    def handle_error(self, error: Exception, context: dict) -> str:
        """
        エラーを人格に合わせて優しく説明
        """
        error_message = f"""
        あら、少し問題が発生してしまいましたね。
        
        **発生した問題**: {self._explain_error_gently(error)}
        
        **考えられる原因**:
        {self._analyze_error_cause(error, context)}
        
        **解決方法**:
        {self._suggest_solutions(error)}
        
        もし作業を続けたい場合は「継続」とおっしゃってくださいね。
        一緒に解決していきましょう。
        """
        
        # 状態保存
        self.state_manager.save_error_context(error, context)
        
        return error_message
```

## 4. クロスプラットフォーム統合

### 4.1 共有メモリシステム
```python
class CrossPlatformMemory:
    """
    プラットフォーム間での記憶共有
    """
    
    def __init__(self):
        self.memory_store = CloudMemoryStore()  # クラウドベース記憶
        self.sync_manager = SyncManager()       # 同期管理
    
    async def sync_conversation_history(self, platform: str, user_id: str):
        """
        会話履歴の同期
        """
        pass
    
    async def maintain_personality_consistency(self, context: dict):
        """
        人格の一貫性維持
        """
        pass
```

### 4.2 プラットフォーム適応
```python
class PlatformAdapter:
    """
    各プラットフォームへの適応
    """
    
    def adapt_for_browser(self, response: str) -> str:
        """
        ブラウザ向け応答調整（HTML対応等）
        """
        pass
    
    def adapt_for_obsidian(self, response: str) -> str:
        """
        Obsidian向け応答調整（Markdown最適化等）
        """
        pass
    
    def adapt_for_raycast(self, response: str) -> str:
        """
        Raycast向け応答調整（簡潔性重視等）
        """
        pass
```

## 5. 実装フェーズ

### フェーズ1: コア人格システム
1. `AoiCorePersonality`クラスの実装
2. 基本的な応答パターンの定義
3. 人格特性の調整機能

### フェーズ2: エビデンス提示システム
1. `EvidenceSystem`の実装
2. 複数MCPサーバーとの統合
3. 引用フォーマッターの開発

### フェーズ3: 作業継続システム
1. `TaskStateManager`の実装
2. エラーハンドリングの強化
3. 継続コマンドの処理

### フェーズ4: クロスプラットフォーム統合
1. 共有メモリシステムの構築
2. プラットフォーム適応機能
3. 同期メカニズムの実装

## 6. 技術スタック

- **コア**: Python 3.11+
- **Web検索**: Brave Search MCP
- **思考プロセス**: Sequential Thinking MCP
- **文献検索**: Ref MCP
- **メモリ**: mem0 MCP (予定)
- **同期**: WebSocket/REST API
- **データベース**: SQLite/PostgreSQL

## 7. 品質保証

### 7.1 人格一貫性テスト
- 同一質問に対する応答の一貫性
- プラットフォーム間での人格維持
- 長期会話での人格安定性

### 7.2 エビデンス品質テスト
- 出典の正確性検証
- 信頼性スコアの妥当性
- 引用フォーマットの適切性

### 7.3 継続性テスト
- エラー発生時の状態保存
- 継続コマンドの正確性
- 作業復旧の完全性

---

**この計画で実装を進めてよろしいでしょうか？**

特に重視したい点や修正が必要な部分があれば、お聞かせください。
一緒に最高の「葵」を作り上げましょう！