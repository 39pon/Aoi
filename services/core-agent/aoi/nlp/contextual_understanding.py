from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import re
from datetime import datetime


class ContextType(Enum):
    """コンテキストの種類"""
    CODING = "coding"
    RESEARCH = "research"
    DESIGN = "design"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    DEBUGGING = "debugging"
    GENERAL = "general"


@dataclass
class ConversationContext:
    """会話のコンテキスト情報"""
    context_type: ContextType
    confidence: float
    active_files: List[str]
    current_task: Optional[str]
    recent_actions: List[str]
    keywords: List[str]
    timestamp: datetime


class ContextualUnderstanding:
    """
    会話の文脈を理解して適切な機能を選択するシステム
    
    会話履歴、現在のファイル状態、最近の操作から
    ユーザーの現在のコンテキストを理解し、
    最適な機能やMCPサーバーを推奨する。
    """
    
    def __init__(self):
        # コンテキスト判定用のキーワード
        self.context_keywords = {
            ContextType.CODING: [
                'コード', 'プログラム', '実装', '開発', 'バグ', 'エラー',
                'function', 'class', 'method', 'variable', 'import',
                'def', 'return', 'if', 'for', 'while', 'try', 'except'
            ],
            ContextType.RESEARCH: [
                '調査', '研究', '情報', '資料', '文献', '論文', '記事',
                'について', '調べ', '検索', '探し', '情報収集'
            ],
            ContextType.DESIGN: [
                '設計', 'アーキテクチャ', '構造', '仕様', 'デザイン',
                'パターン', 'モデル', '図', 'UML', 'ER図'
            ],
            ContextType.TESTING: [
                'テスト', '検証', 'デバッグ', '確認', 'チェック',
                'test', 'assert', 'mock', 'unittest', 'pytest'
            ],
            ContextType.DOCUMENTATION: [
                'ドキュメント', '文書', 'README', 'マニュアル',
                '説明', '解説', 'コメント', 'docstring'
            ],
            ContextType.DEBUGGING: [
                'デバッグ', 'エラー', 'バグ', '問題', '修正',
                'error', 'exception', 'traceback', 'log'
            ]
        }
        
        # ファイル拡張子によるコンテキスト推定
        self.file_context_mapping = {
            '.py': ContextType.CODING,
            '.js': ContextType.CODING,
            '.ts': ContextType.CODING,
            '.java': ContextType.CODING,
            '.cpp': ContextType.CODING,
            '.c': ContextType.CODING,
            '.md': ContextType.DOCUMENTATION,
            '.txt': ContextType.DOCUMENTATION,
            '.json': ContextType.CODING,
            '.yaml': ContextType.CODING,
            '.yml': ContextType.CODING,
            '.test.py': ContextType.TESTING,
            '.spec.js': ContextType.TESTING
        }
        
        # コンテキストに応じた推奨機能
        self.context_recommendations = {
            ContextType.CODING: {
                'primary_tools': ['view_files', 'update_file', 'run_command'],
                'mcp_servers': [
                    'mcp.config.usrlocalmcp.Ref'
                ],
                'search_priority': 'tech_docs'
            },
            ContextType.RESEARCH: {
                'primary_tools': ['web_search'],
                'mcp_servers': [
                    'mcp.config.usrlocalmcp.Brave Search',
                    'mcp.config.usrlocalmcp.Ref'
                ],
                'search_priority': 'papers'
            },
            ContextType.DESIGN: {
                'primary_tools': ['write_to_file', 'view_files'],
                'mcp_servers': ['mcp.config.usrlocalmcp.Sequential Thinking'],
                'search_priority': 'design'
            },
            ContextType.TESTING: {
                'primary_tools': ['run_command', 'view_files'],
                'mcp_servers': ['mcp.config.usrlocalmcp.Ref'],
                'search_priority': 'testing_docs'
            },
            ContextType.DEBUGGING: {
                'primary_tools': ['view_files', 'search_codebase', 'run_command'],
                'mcp_servers': [
                    'mcp.config.usrlocalmcp.Sequential Thinking',
                    'mcp.config.usrlocalmcp.Brave Search'
                ],
                'search_priority': 'error_analysis'
            }
        }
    
    def understand_context(self,
                           conversation_history: List[str],
                           current_files: Optional[List[str]] = None,
                           recent_actions: Optional[List[str]] = None
                           ) -> ConversationContext:
        """
        会話履歴から現在のコンテキストを理解
        
        Args:
            conversation_history: 会話履歴のリスト
            current_files: 現在開いているファイルのリスト
            recent_actions: 最近の操作履歴
            
        Returns:
            ConversationContext: 理解されたコンテキスト情報
            
        Examples:
            conversation_history = [
                "Pythonのファイルを作成して",
                "エラーが出ているので修正したい"
            ]
            → ContextType.DEBUGGING (エラー修正のコンテキスト)
        """
        current_files = current_files or []
        recent_actions = recent_actions or []
        
        # 全テキストを結合して分析
        all_text = ' '.join(conversation_history + recent_actions)
        
        # キーワードベースでコンテキストスコアを計算
        context_scores = self._calculate_context_scores(all_text)
        
        # ファイル情報からコンテキストを推定
        file_context_scores = self._analyze_file_context(current_files)
        
        # スコアを統合
        combined_scores = self._combine_scores(
            context_scores, file_context_scores)
        
        # 最高スコアのコンテキストを選択
        best_context = max(
            combined_scores.items(), key=lambda x: x[1])
        context_type, confidence = best_context
        
        # キーワードを抽出
        keywords = self._extract_keywords(all_text, context_type)
        
        # 現在のタスクを推定
        current_task = self._estimate_current_task(
            conversation_history, context_type)
        
        return ConversationContext(
            context_type=context_type,
            confidence=confidence,
            active_files=current_files,
            current_task=current_task,
            recent_actions=recent_actions,
            keywords=keywords,
            timestamp=datetime.now()
        )
    
    def _calculate_context_scores(self, text: str) -> Dict[ContextType, float]:
        """
        テキストからコンテキストスコアを計算
        
        Args:
            text: 分析対象のテキスト
            
        Returns:
            Dict[ContextType, float]: コンテキストタイプ別スコア
        """
        scores = {context: 0.0 for context in ContextType}
        text_lower = text.lower()
        
        for context_type, keywords in self.context_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    # キーワードの出現回数に基づいてスコア加算
                    count = text_lower.count(keyword.lower())
                    scores[context_type] += count * 0.1
        
        # スコアを正規化
        max_score = max(scores.values()) if scores.values() else 1.0
        if max_score > 0:
            scores = {k: v / max_score for k, v in scores.items()}
        
        return scores
    
    def _analyze_file_context(self, files: List[str]) -> Dict[ContextType, float]:
        """
        ファイル情報からコンテキストを分析
        
        Args:
            files: ファイルパスのリスト
            
        Returns:
            Dict[ContextType, float]: ファイルベースのコンテキストスコア
        """
        scores = {context: 0.0 for context in ContextType}
        
        for file_path in files:
            # ファイル拡張子を取得
            for ext, context_type in self.file_context_mapping.items():
                if file_path.endswith(ext):
                    scores[context_type] += 0.3
                    break
            
            # ファイル名からコンテキストを推定
            file_lower = file_path.lower()
            if 'test' in file_lower:
                scores[ContextType.TESTING] += 0.2
            elif 'doc' in file_lower or 'readme' in file_lower:
                scores[ContextType.DOCUMENTATION] += 0.2
            elif 'design' in file_lower or 'spec' in file_lower:
                scores[ContextType.DESIGN] += 0.2
        
        return scores
    
    def _combine_scores(self,
                        text_scores: Dict[ContextType, float],
                        file_scores: Dict[ContextType, float]
                        ) -> Dict[ContextType, float]:
        """
        テキストスコアとファイルスコアを統合
        
        Args:
            text_scores: テキストベースのスコア
            file_scores: ファイルベースのスコア
            
        Returns:
            Dict[ContextType, float]: 統合されたスコア
        """
        combined = {}
        
        for context_type in ContextType:
            # 重み付き平均（テキスト70%、ファイル30%）
            combined[context_type] = (
                text_scores.get(context_type, 0.0) * 0.7 +
                file_scores.get(context_type, 0.0) * 0.3
            )
        
        return combined
    
    def _extract_keywords(self, text: str,
                          context_type: ContextType) -> List[str]:
        """
        コンテキストに関連するキーワードを抽出
        
        Args:
            text: 分析対象のテキスト
            context_type: コンテキストタイプ
            
        Returns:
            List[str]: 抽出されたキーワード
        """
        keywords = []
        text_lower = text.lower()
        
        # コンテキストに関連するキーワードを検索
        context_keywords = self.context_keywords.get(context_type, [])
        for keyword in context_keywords:
            if keyword.lower() in text_lower:
                keywords.append(keyword)
        
        # 重複を除去して返す
        return list(set(keywords))
    
    def _estimate_current_task(self,
                               conversation_history: List[str],
                               context_type: ContextType
                               ) -> Optional[str]:
        """
        現在のタスクを推定
        
        Args:
            conversation_history: 会話履歴
            context_type: コンテキストタイプ
            
        Returns:
            Optional[str]: 推定されたタスク
        """
        if not conversation_history:
            return None
        
        # 最新の発言からタスクを推定
        latest_message = conversation_history[-1]
        
        # タスク推定パターン
        task_patterns = {
            r'(.+?)を作成': 'creating',
            r'(.+?)を修正': 'fixing',
            r'(.+?)を調べ': 'researching',
            r'(.+?)を実装': 'implementing',
            r'(.+?)をテスト': 'testing',
            r'(.+?)を設計': 'designing'
        }
        
        for pattern, task_type in task_patterns.items():
            match = re.search(pattern, latest_message)
            if match:
                target = match.group(1)
                return f"{task_type}: {target}"
        
        return f"working on {context_type.value} task"
    
    def get_recommendations(self,
                            context: ConversationContext
                            ) -> Dict[str, List[str]]:
        """
        コンテキストに基づいて推奨機能を取得
        
        Args:
            context: コンテキスト情報
            
        Returns:
            Dict[str, List[str]]: 推奨機能の辞書
        """
        recommendations = self.context_recommendations.get(
            context.context_type,
            self.context_recommendations[
                ContextType.GENERAL])
        
        return {
            'primary_tools': recommendations.get('primary_tools', []),
            'mcp_servers': recommendations.get('mcp_servers', []),
            'search_priority': [
                recommendations.get('search_priority', 'general')
            ]
        }