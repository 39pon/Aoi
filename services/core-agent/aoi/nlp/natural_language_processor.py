from typing import Dict, Optional
import re
from dataclasses import dataclass
from enum import Enum


class IntentType(Enum):
    """意図の種類"""
    WEB_SEARCH = "web_search"
    REF_SEARCH = "ref_search"
    SEQUENTIAL_THINKING = "sequential_thinking"
    FILE_CREATE = "file_create"
    FILE_EDIT = "file_edit"
    FILE_VIEW = "file_view"
    RUN_SERVER = "run_server"
    INSTALL_DEPS = "install_deps"
    RUN_TESTS = "run_tests"
    GENERAL_HELP = "general_help"
    UNKNOWN = "unknown"


@dataclass
class ParsedIntent:
    """解析された意図"""
    intent_type: IntentType
    confidence: float
    parameters: Dict[str, str]
    original_text: str
    suggested_action: str


class NaturalLanguageProcessor:
    """
    口語での機能呼び出しを理解するシステム
    
    ユーザーの自然な日本語入力から意図を解析し、
    適切なMCPサーバーや機能を呼び出すための情報を抽出する。
    """
    
    def __init__(self):
        self.command_patterns = {
            IntentType.WEB_SEARCH: [
                r'(.+?)について?調べて',
                r'(.+?)をググって',
                r'(.+?)を検索して',
                r'(.+?)を探して',
                r'(.+?)の情報が欲しい',
                r'(.+?)って何？?',
                r'(.+?)について教えて'
            ],
            IntentType.REF_SEARCH: [
                r'(.+?)のドキュメント(を)?見て',
                r'(.+?)の技術資料(を)?調べて',
                r'(.+?)のリファレンス(を)?確認',
                r'(.+?)のAPI(を)?確認',
                r'(.+?)の使い方(を)?教えて'
            ],
            IntentType.SEQUENTIAL_THINKING: [
                r'(.+?)について考えて',
                r'(.+?)を分析して',
                r'(.+?)を整理して',
                r'(.+?)の問題を解決して',
                r'(.+?)を検討して'
            ],
            IntentType.FILE_CREATE: [
                r'(.+?)ファイル(を)?作って',
                r'新しい(.+?)ファイル',
                r'(.+?)を作成して',
                r'(.+?)ファイル作成'
            ],
            IntentType.FILE_EDIT: [
                r'(.+?)(を)?修正して',
                r'(.+?)(を)?変更して',
                r'(.+?)(を)?編集して',
                r'(.+?)(を)?直して',
                r'(.+?)(を)?更新して'
            ],
            IntentType.FILE_VIEW: [
                r'(.+?)(を)?見せて',
                r'(.+?)(を)?確認して',
                r'(.+?)(を)?表示して',
                r'(.+?)(を)?開いて'
            ],
            IntentType.RUN_SERVER: [
                r'サーバー(を)?起動',
                r'(.+?)(を)?実行して',
                r'(.+?)(を)?動かして',
                r'(.+?)(を)?起動して'
            ],
            IntentType.INSTALL_DEPS: [
                r'(.+?)(を)?インストールして',
                r'(.+?)パッケージ(を)?入れて',
                r'依存関係(を)?インストール'
            ],
            IntentType.RUN_TESTS: [
                r'テスト(を)?実行',
                r'テストして',
                r'(.+?)テスト(を)?動かして'
            ]
        }
        
        # コンテキストキーワード
        self.context_keywords = {
            'coding': ['コード', 'プログラム', '実装', '開発', 'バグ', 'エラー'],
            'research': ['調査', '研究', '情報', '資料', '文献'],
            'design': ['設計', 'アーキテクチャ', '構造', '仕様'],
            'testing': ['テスト', '検証', 'デバッグ', '確認']
        }
    
    def parse_intent(self, user_input: str) -> ParsedIntent:
        """
        ユーザーの口語入力から意図を解析
        
        Args:
            user_input: ユーザーの入力テキスト
            
        Returns:
            ParsedIntent: 解析された意図情報
            
        Examples:
            "GitHubのAPIについて調べて" → 
            ParsedIntent(
                intent_type=IntentType.WEB_SEARCH,
                confidence=0.9,
                parameters={'query': 'GitHub API'},
                original_text="GitHubのAPIについて調べて",
                suggested_action="Brave Searchを使用してGitHub APIについて検索します"
            )
        """
        user_input = user_input.strip()
        
        # 各パターンとマッチングを試行
        for intent_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    # マッチした場合の処理
                    extracted_param = match.group(1) if match.groups() else ""
                    confidence = self._calculate_confidence(
                        user_input, pattern)
                    
                    parameters = self._extract_parameters(
                        intent_type, extracted_param, user_input)
                    
                    suggested_action = self._generate_suggested_action(
                        intent_type, parameters)
                    
                    return ParsedIntent(
                        intent_type=intent_type,
                        confidence=confidence,
                        parameters=parameters,
                        original_text=user_input,
                        suggested_action=suggested_action
                    )
        
        # マッチしなかった場合は一般的なヘルプとして処理
        return ParsedIntent(
            intent_type=IntentType.GENERAL_HELP,
            confidence=0.3,
            parameters={'query': user_input},
            original_text=user_input,
            suggested_action="お手伝いできることを確認します"
        )
    
    def _calculate_confidence(self, user_input: str, pattern: str) -> float:
        """
        マッチングの信頼度を計算
        
        Args:
            user_input: ユーザー入力
            pattern: マッチしたパターン
            
        Returns:
            float: 信頼度 (0.0-1.0)
        """
        # 基本信頼度
        base_confidence = 0.7
        
        # 入力の長さによる調整
        length_factor = min(len(user_input) / 20, 1.0)
        
        # キーワードの存在による調整
        keyword_bonus = 0.0
        for context, keywords in self.context_keywords.items():
            for keyword in keywords:
                if keyword in user_input:
                    keyword_bonus += 0.1
                    break
        
        return min(base_confidence + length_factor * 0.2 + keyword_bonus, 1.0)
    
    def _extract_parameters(self, intent_type: IntentType,
                            extracted_param: str,
                            full_input: str) -> Dict[str, str]:
        """
        意図タイプに応じてパラメータを抽出
        
        Args:
            intent_type: 意図タイプ
            extracted_param: 正規表現で抽出されたパラメータ
            full_input: 完全な入力テキスト
            
        Returns:
            Dict[str, str]: 抽出されたパラメータ
        """
        parameters = {}
        
        if intent_type in [IntentType.WEB_SEARCH, IntentType.REF_SEARCH]:
            parameters['query'] = extracted_param or full_input
        elif intent_type == IntentType.SEQUENTIAL_THINKING:
            parameters['topic'] = extracted_param or full_input
        elif intent_type in [IntentType.FILE_CREATE, IntentType.FILE_EDIT,
                             IntentType.FILE_VIEW]:
            parameters['target'] = extracted_param or 'current_file'
        elif intent_type == IntentType.RUN_SERVER:
            parameters['server_type'] = extracted_param or 'development'
        elif intent_type == IntentType.INSTALL_DEPS:
            parameters['package'] = extracted_param or 'requirements'
        elif intent_type == IntentType.RUN_TESTS:
            parameters['test_type'] = extracted_param or 'all'
        else:
            parameters['query'] = full_input
        
        return parameters
    
    def _generate_suggested_action(self, intent_type: IntentType,
                                   parameters: Dict[str, str]) -> str:
        """
        意図に基づいて推奨アクションを生成
        
        Args:
            intent_type: 意図タイプ
            parameters: パラメータ
            
        Returns:
            str: 推奨アクション文
        """
        action_templates = {
            IntentType.WEB_SEARCH: (
                "Brave Searchを使用して'{query}'について検索します"),
            IntentType.REF_SEARCH: (
                "Refを使用して'{query}'のドキュメントを検索します"),
            IntentType.SEQUENTIAL_THINKING: (
                "Sequential Thinkingを使用して'{topic}'について分析します"),
            IntentType.FILE_CREATE: "'{target}'ファイルを作成します",
            IntentType.FILE_EDIT: "'{target}'を編集します",
            IntentType.FILE_VIEW: "'{target}'を表示します",
            IntentType.RUN_SERVER: "'{server_type}'サーバーを起動します",
            IntentType.INSTALL_DEPS: "'{package}'をインストールします",
            IntentType.RUN_TESTS: "'{test_type}'テストを実行します",
            IntentType.GENERAL_HELP: "お手伝いできることを確認します"
        }
        
        template = action_templates.get(intent_type, "処理を実行します")
        return template.format(**parameters)
    
    def get_mcp_server_mapping(self, intent_type: IntentType) -> Optional[str]:
        """
        意図タイプに対応するMCPサーバー名を取得
        
        Args:
            intent_type: 意図タイプ
            
        Returns:
            Optional[str]: MCPサーバー名
        """
        mcp_mapping = {
            IntentType.WEB_SEARCH: (
                "mcp.config.usrlocalmcp.Brave Search"),
            IntentType.REF_SEARCH: "mcp.config.usrlocalmcp.Ref",
            IntentType.SEQUENTIAL_THINKING: (
                "mcp.config.usrlocalmcp.Sequential Thinking")
        }
        
        return mcp_mapping.get(intent_type)
    
    def get_tool_mapping(self, intent_type: IntentType) -> Optional[str]:
        """
        意図タイプに対応するツール名を取得
        
        Args:
            intent_type: 意図タイプ
            
        Returns:
            Optional[str]: ツール名
        """
        tool_mapping = {
            IntentType.WEB_SEARCH: "brave_web_search",
            IntentType.REF_SEARCH: "ref_search_documentation",
            IntentType.SEQUENTIAL_THINKING: "sequentialthinking",
            IntentType.FILE_CREATE: "write_to_file",
            IntentType.FILE_EDIT: "update_file",
            IntentType.FILE_VIEW: "view_files",
            IntentType.RUN_SERVER: "run_command",
            IntentType.INSTALL_DEPS: "run_command",
            IntentType.RUN_TESTS: "run_command"
        }
        
        return tool_mapping.get(intent_type)