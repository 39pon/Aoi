"""プラットフォーム適応システム

各プラットフォーム（ブラウザ、Obsidian、Raycast）に最適化された
応答フォーマットと機能を提供する
"""

import re
import json
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass

from .cross_platform_system import PlatformType


class ResponseFormat(Enum):
    """応答フォーマット種別"""
    PLAIN_TEXT = "plain_text"
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    RICH_TEXT = "rich_text"


@dataclass
class PlatformCapabilities:
    """プラットフォーム機能情報"""
    supports_html: bool
    supports_markdown: bool
    supports_images: bool
    supports_links: bool
    supports_code_blocks: bool
    max_response_length: int
    preferred_format: ResponseFormat
    ui_constraints: Dict[str, Any]


class PlatformAdapter:
    """プラットフォーム適応システム"""

    def __init__(self):
        self.platform_capabilities = {
            PlatformType.BROWSER: PlatformCapabilities(
                supports_html=True,
                supports_markdown=True,
                supports_images=True,
                supports_links=True,
                supports_code_blocks=True,
                max_response_length=10000,
                preferred_format=ResponseFormat.HTML,
                ui_constraints={
                    "max_width": "800px",
                    "responsive": True,
                    "dark_mode_support": True
                }
            ),
            PlatformType.OBSIDIAN: PlatformCapabilities(
                supports_html=False,
                supports_markdown=True,
                supports_images=True,
                supports_links=True,
                supports_code_blocks=True,
                max_response_length=50000,
                preferred_format=ResponseFormat.MARKDOWN,
                ui_constraints={
                    "vault_integration": True,
                    "wikilink_support": True,
                    "tag_support": True
                }
            ),
            PlatformType.RAYCAST: PlatformCapabilities(
                supports_html=False,
                supports_markdown=True,
                supports_images=False,
                supports_links=True,
                supports_code_blocks=True,
                max_response_length=2000,
                preferred_format=ResponseFormat.PLAIN_TEXT,
                ui_constraints={
                    "compact_mode": True,
                    "quick_actions": True,
                    "search_optimization": True
                }
            )
        }

    def adapt_response(
        self, 
        response: str, 
        platform: PlatformType,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """プラットフォームに応じて応答を適応"""
        capabilities = self.platform_capabilities.get(platform)
        if not capabilities:
            return response

        # 長さ制限の適用
        if len(response) > capabilities.max_response_length:
            response = self._truncate_response(
                response, 
                capabilities.max_response_length
            )

        # フォーマット変換
        if platform == PlatformType.BROWSER:
            return self._adapt_for_browser(response, capabilities, context)
        elif platform == PlatformType.OBSIDIAN:
            return self._adapt_for_obsidian(response, capabilities, context)
        elif platform == PlatformType.RAYCAST:
            return self._adapt_for_raycast(response, capabilities, context)
        
        return response

    def _adapt_for_browser(self, response: str, capabilities: PlatformCapabilities, context: Optional[Dict[str, Any]]) -> str:
        """ブラウザ向け応答調整"""
        # Markdownを基本HTMLに変換
        html_response = self._markdown_to_html(response)
        
        # CSSスタイリングの追加
        styled_response = f"""
        <div class="aoi-response" style="
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        ">
            {html_response}
        </div>
        """
        
        # ダークモード対応
        if context and context.get("dark_mode", False):
            styled_response = styled_response.replace(
                "color: #333;", 
                "color: #e0e0e0; background-color: #1a1a1a;"
            )
        
        return styled_response

    def _adapt_for_obsidian(self, response: str, capabilities: PlatformCapabilities, context: Optional[Dict[str, Any]]) -> str:
        """Obsidian向け応答調整"""
        # Wikilink形式の変換
        response = self._convert_to_wikilinks(response)
        
        # タグの追加
        if context and context.get("add_tags", True):
            tags = self._generate_relevant_tags(response)
            if tags:
                response += f"\n\n---\n\n{' '.join(tags)}"
        
        # コードブロックの最適化
        response = self._optimize_code_blocks_for_obsidian(response)
        
        # メタデータの追加
        if context and context.get("add_metadata", True):
            metadata = self._generate_obsidian_metadata(context)
            response = f"{metadata}\n\n{response}"
        
        return response

    def _adapt_for_raycast(self, response: str, capabilities: PlatformCapabilities, context: Optional[Dict[str, Any]]) -> str:
        """Raycast向け応答調整"""
        # 簡潔性を重視した調整
        response = self._make_concise(response)
        
        # アクション可能な要素の抽出
        actions = self._extract_actionable_items(response)
        
        # Raycast形式のフォーマット
        formatted_response = response
        
        if actions:
            formatted_response += "\n\n🔧 **クイックアクション:**\n"
            for action in actions[:3]:  # 最大3つまで
                formatted_response += f"• {action}\n"
        
        return formatted_response

    def _markdown_to_html(self, markdown: str) -> str:
        """基本的なMarkdown→HTML変換"""
        # 見出し
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', markdown, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # 強調
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # コードブロック
        html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
        html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
        
        # リンク
        html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)
        
        # 改行
        html = html.replace('\n', '<br>\n')
        
        return html

    def _convert_to_wikilinks(self, text: str) -> str:
        """通常のリンクをWikilink形式に変換"""
        # [テキスト](URL) → [[テキスト]]
        return re.sub(r'\[(.*?)\]\(.*?\)', r'[[\1]]', text)

    def _generate_relevant_tags(self, content: str) -> List[str]:
        """コンテンツから関連タグを生成"""
        tags = []
        
        # キーワードベースのタグ生成
        if 'python' in content.lower():
            tags.append('#python')
        if 'javascript' in content.lower():
            tags.append('#javascript')
        if 'api' in content.lower():
            tags.append('#api')
        if 'データベース' in content or 'database' in content.lower():
            tags.append('#database')
        if '設計' in content or 'design' in content.lower():
            tags.append('#design')
        
        return tags

    def _optimize_code_blocks_for_obsidian(self, text: str) -> str:
        """Obsidian用のコードブロック最適化"""
        # 言語指定の追加
        text = re.sub(r'```\n', '```python\n', text)
        return text

    def _generate_obsidian_metadata(self, context: Dict[str, Any]) -> str:
        """Obsidianメタデータの生成"""
        from datetime import datetime
        
        metadata = "---\n"
        metadata += f"created: {datetime.now().isoformat()}\n"
        metadata += "type: aoi-response\n"
        
        if context.get("topic"):
            metadata += f"topic: {context['topic']}\n"
        
        metadata += "---"
        return metadata

    def _make_concise(self, text: str) -> str:
        """テキストを簡潔にする"""
        # 長い文章を短縮
        sentences = text.split('。')
        if len(sentences) > 5:
            text = '。'.join(sentences[:5]) + '。'
        
        # 冗長な表現を削除
        text = re.sub(r'ということです', '', text)
        text = re.sub(r'と思われます', '', text)
        text = re.sub(r'について説明します', '', text)
        
        return text

    def _extract_actionable_items(self, text: str) -> List[str]:
        """実行可能なアクションを抽出"""
        actions = []
        
        # 動詞で始まる文を抽出
        action_patterns = [
            r'(実行|作成|削除|更新|確認|検索|インストール|設定).*?[。\n]',
            r'(Run|Create|Delete|Update|Check|Search|Install|Configure).*?[.\n]'
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            actions.extend(matches)
        
        return actions[:5]  # 最大5つまで

    def _truncate_response(self, response: str, max_length: int) -> str:
        """応答を適切に切り詰める"""
        if len(response) <= max_length:
            return response
        
        # 文の境界で切り詰める
        truncated = response[:max_length]
        last_sentence_end = max(
            truncated.rfind('。'),
            truncated.rfind('.'),
            truncated.rfind('\n')
        )
        
        if last_sentence_end > max_length * 0.8:  # 80%以上なら文境界で切る
            truncated = truncated[:last_sentence_end + 1]
        
        return truncated + "\n\n[応答が長いため省略されました]"

    def get_platform_capabilities(self, platform: PlatformType) -> Optional[PlatformCapabilities]:
        """プラットフォーム機能情報を取得"""
        return self.platform_capabilities.get(platform)

    def is_feature_supported(self, platform: PlatformType, feature: str) -> bool:
        """機能がサポートされているかチェック"""
        capabilities = self.get_platform_capabilities(platform)
        if not capabilities:
            return False
        
        return getattr(capabilities, f"supports_{feature}", False)