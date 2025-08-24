from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


class EvidenceType(Enum):
    """エビデンスの種類"""
    WEB_SEARCH = "web_search"  # Web検索結果
    DOCUMENTATION = "documentation"  # 技術文書
    CODE_REFERENCE = "code_reference"  # コード参照
    ACADEMIC_PAPER = "academic_paper"  # 学術論文
    OFFICIAL_DOCS = "official_docs"  # 公式ドキュメント
    STACK_OVERFLOW = "stack_overflow"  # Stack Overflow
    GITHUB_ISSUE = "github_issue"  # GitHub Issue
    BLOG_POST = "blog_post"  # ブログ記事
    TUTORIAL = "tutorial"  # チュートリアル
    API_DOCS = "api_docs"  # API文書


class CredibilityLevel(Enum):
    """信頼性レベル"""
    HIGH = "high"  # 高信頼性（公式文書、学術論文等）
    MEDIUM = "medium"  # 中信頼性（技術ブログ、Stack Overflow等）
    LOW = "low"  # 低信頼性（個人ブログ、未検証情報等）


@dataclass
class Evidence:
    """エビデンス情報"""
    title: str
    url: str
    content: str
    evidence_type: EvidenceType
    credibility: CredibilityLevel
    timestamp: datetime
    relevance_score: float  # 関連性スコア（0.0-1.0）
    source_domain: str
    tags: List[str]
    summary: Optional[str] = None


@dataclass
class EvidenceCollection:
    """エビデンスコレクション"""
    query: str
    evidences: List[Evidence]
    total_sources: int
    search_timestamp: datetime
    confidence_score: float  # 全体の信頼性スコア


class EvidenceSystem:
    """エビデンス提示システム - 根拠となる情報を収集・提示"""
    
    def __init__(self):
        self.credibility_weights = {
            CredibilityLevel.HIGH: 1.0,
            CredibilityLevel.MEDIUM: 0.7,
            CredibilityLevel.LOW: 0.4
        }
        
        self.domain_credibility = {
            # 高信頼性ドメイン
            "docs.python.org": CredibilityLevel.HIGH,
            "developer.mozilla.org": CredibilityLevel.HIGH,
            "docs.microsoft.com": CredibilityLevel.HIGH,
            "kubernetes.io": CredibilityLevel.HIGH,
            "reactjs.org": CredibilityLevel.HIGH,
            "nodejs.org": CredibilityLevel.HIGH,
            "github.com": CredibilityLevel.HIGH,
            
            # 中信頼性ドメイン
            "stackoverflow.com": CredibilityLevel.MEDIUM,
            "medium.com": CredibilityLevel.MEDIUM,
            "dev.to": CredibilityLevel.MEDIUM,
            "qiita.com": CredibilityLevel.MEDIUM,
            "zenn.dev": CredibilityLevel.MEDIUM,
            
            # 学術系
            "arxiv.org": CredibilityLevel.HIGH,
            "ieee.org": CredibilityLevel.HIGH,
            "acm.org": CredibilityLevel.HIGH
        }
        
        self.evidence_templates = {
            "web_search": "🔍 Web検索結果",
            "documentation": "📚 技術文書",
            "code_reference": "💻 コード参照",
            "academic_paper": "🎓 学術論文",
            "official_docs": "📋 公式文書",
            "stack_overflow": "❓ Stack Overflow",
            "github_issue": "🐛 GitHub Issue",
            "blog_post": "✍️ ブログ記事",
            "tutorial": "🎯 チュートリアル",
            "api_docs": "⚙️ API文書"
        }
    
    async def gather_evidence(
            self,
            query: str,
            evidence_types: Optional[List[EvidenceType]] = None,
            max_results: int = 5
    ) -> EvidenceCollection:
        """指定されたクエリに対してエビデンスを収集"""
        if evidence_types is None:
            evidence_types = [
                EvidenceType.WEB_SEARCH,
                EvidenceType.DOCUMENTATION,
                EvidenceType.STACK_OVERFLOW
            ]
        
        evidences = []
        
        for evidence_type in evidence_types:
            type_evidences = await self._search_by_type(
                query, evidence_type, max_results // len(evidence_types))
            evidences.extend(type_evidences)
        
        # 関連性でソート
        evidences.sort(key=lambda x: x.relevance_score, reverse=True)
        evidences = evidences[:max_results]
        
        # 信頼性スコアを計算
        confidence_score = self._calculate_confidence_score(evidences)
        
        return EvidenceCollection(
            query=query,
            evidences=evidences,
            total_sources=len(evidences),
            search_timestamp=datetime.now(),
            confidence_score=confidence_score
        )
    
    async def _search_by_type(self,
                              query: str,
                              evidence_type: EvidenceType,
                              max_results: int) -> List[Evidence]:
        """タイプ別エビデンス検索"""
        evidences = []
        
        if evidence_type == EvidenceType.WEB_SEARCH:
            evidences = await self._web_search(query, max_results)
        elif evidence_type == EvidenceType.DOCUMENTATION:
            evidences = await self._search_documentation(query, max_results)
        elif evidence_type == EvidenceType.STACK_OVERFLOW:
            evidences = await self._search_stackoverflow(query, max_results)
        elif evidence_type == EvidenceType.GITHUB_ISSUE:
            evidences = await self._search_github_issues(query, max_results)
        
        return evidences
    
    async def _web_search(self,
                          query: str,
                          max_results: int) -> List[Evidence]:
        """Web検索を実行"""
        # Brave Search MCPを使用
        try:
            # 実際の実装では run_mcp を使用
            search_results = await self._mock_brave_search(query, max_results)
            evidences = []
            
            for result in search_results:
                credibility = self._determine_credibility(result['url'])
                relevance = self._calculate_relevance(query, result['content'])
                
                evidence = Evidence(
                    title=result['title'],
                    url=result['url'],
                    content=result['content'],
                    evidence_type=EvidenceType.WEB_SEARCH,
                    credibility=credibility,
                    timestamp=datetime.now(),
                    relevance_score=relevance,
                    source_domain=self._extract_domain(
                        result['url']),
                    tags=self._extract_tags(result['content']),
                    summary=result.get('summary')
                )
                evidences.append(evidence)
            
            return evidences
        except Exception as e:
            print(f"Web検索エラー: {e}")
            return []
    
    async def _search_documentation(self,
                                    query: str,
                                    max_results: int
                                    ) -> List[Evidence]:
        """技術文書を検索"""
        # Ref MCPを使用
        try:
            # 実際の実装では run_mcp を使用
            doc_results = await self._mock_ref_search(query, max_results)
            evidences = []
            
            for result in doc_results:
                evidence = Evidence(
                    title=result['title'],
                    url=result['url'],
                    content=result['content'],
                    evidence_type=EvidenceType.DOCUMENTATION,
                    credibility=CredibilityLevel.HIGH,
                    timestamp=datetime.now(),
                    relevance_score=self._calculate_relevance(
                        query, result['content']),
                    source_domain=self._extract_domain(result['url']),
                    tags=self._extract_tags(result['content'])
                )
                evidences.append(evidence)
            
            return evidences
        except Exception as e:
            print(f"文書検索エラー: {e}")
            return []
    
    async def _search_stackoverflow(self,
                                    query: str,
                                    max_results: int
                                    ) -> List[Evidence]:
        """Stack Overflow検索"""
        # Stack Overflow APIまたはWeb検索を使用
        try:
            # site:stackoverflow.com でWeb検索
            so_query = f"site:stackoverflow.com {query}"
            search_results = await self._mock_brave_search(
                so_query, max_results)
            evidences = []
            
            for result in search_results:
                evidence = Evidence(
                    title=result['title'],
                    url=result['url'],
                    content=result['content'],
                    evidence_type=EvidenceType.STACK_OVERFLOW,
                    credibility=CredibilityLevel.MEDIUM,
                    timestamp=datetime.now(),
                    relevance_score=self._calculate_relevance(
                        query, result['content']),
                    source_domain="stackoverflow.com",
                    tags=self._extract_tags(result['content'])
                )
                evidences.append(evidence)
            
            return evidences
        except Exception as e:
            print(f"Stack Overflow検索エラー: {e}")
            return []
    
    async def _search_github_issues(self,
                                    query: str,
                                    max_results: int
                                    ) -> List[Evidence]:
        """GitHub Issues検索"""
        # GitHub MCPを使用
        try:
            # 実際の実装では run_mcp を使用
            github_results = await self._mock_github_search(
                query, max_results)
            evidences = []
            
            for result in github_results:
                evidence = Evidence(
                    title=result['title'],
                    url=result['url'],
                    content=result['content'],
                    evidence_type=EvidenceType.GITHUB_ISSUE,
                    credibility=CredibilityLevel.MEDIUM,
                    timestamp=datetime.now(),
                    relevance_score=self._calculate_relevance(
                        query, result['content']),
                    source_domain="github.com",
                    tags=self._extract_tags(result['content'])
                )
                evidences.append(evidence)
            
            return evidences
        except Exception as e:
            print(f"GitHub検索エラー: {e}")
            return []
    
    def _determine_credibility(self, url: str) -> CredibilityLevel:
        """URLから信頼性を判定"""
        domain = self._extract_domain(url)
        return self.domain_credibility.get(domain, CredibilityLevel.LOW)
    
    def _extract_domain(self, url: str) -> str:
        """URLからドメインを抽出"""
        import re
        match = re.search(r'https?://([^/]+)', url)
        if match:
            domain = match.group(1)
            # www. を除去
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        return ""
    
    def _calculate_relevance(self, query: str, content: str) -> float:
        """関連性スコアを計算"""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        if not query_words:
            return 0.0
        
        # 単純な単語マッチング（実際の実装ではより高度な手法を使用）
        matches = len(query_words.intersection(content_words))
        return min(matches / len(query_words), 1.0)
    
    def _extract_tags(self, content: str) -> List[str]:
        """コンテンツからタグを抽出"""
        # 技術用語やプログラミング言語を検出
        tech_terms = [
            'python', 'javascript', 'react', 'node.js', 'docker',
            'kubernetes', 'aws', 'azure', 'gcp', 'api', 'rest',
            'graphql', 'database', 'sql', 'nosql', 'mongodb',
            'postgresql', 'mysql', 'redis', 'nginx', 'apache'
        ]
        
        content_lower = content.lower()
        found_tags = []
        
        for term in tech_terms:
            if term in content_lower:
                found_tags.append(term)
        
        return found_tags[:5]  # 最大5個のタグ
    
    def _calculate_confidence_score(self,
                                    evidences: List[Evidence]) -> float:
        """全体の信頼性スコアを計算"""
        if not evidences:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        for evidence in evidences:
            weight = self.credibility_weights[evidence.credibility]
            score = evidence.relevance_score * weight
            total_score += score
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def format_evidence_section(self,
                                collection: EvidenceCollection) -> str:
        """エビデンスセクションをフォーマット"""
        if not collection.evidences:
            return ("\n\n📋 **参考情報**\n"
                    "関連する情報が見つかりませんでした。")
        
        section = (f"\n\n📋 **参考情報** "
                   f"(信頼性: {collection.confidence_score:.1%})\n")
        
        for i, evidence in enumerate(collection.evidences, 1):
            icon = self.evidence_templates.get(
                evidence.evidence_type.value, "📄")
            credibility_indicator = self._get_credibility_indicator(
                evidence.credibility)
            
            section += (f"{i}. {icon} **{evidence.title}** "
                        f"{credibility_indicator}\n")
            section += f"   🔗 {evidence.url}\n"
            
            if evidence.summary:
                section += f"   💡 {evidence.summary}\n"
            
            if evidence.tags:
                tags_str = ", ".join(evidence.tags[:3])
                section += f"   🏷️ {tags_str}\n"
            
            section += "\n"
        
        return section
    
    def _get_credibility_indicator(self,
                                   credibility: CredibilityLevel) -> str:
        """信頼性インジケーターを取得"""
        indicators = {
            CredibilityLevel.HIGH: "🟢",
            CredibilityLevel.MEDIUM: "🟡",
            CredibilityLevel.LOW: "🔴"
        }
        return indicators.get(credibility, "⚪")
    
    # モック関数（実際の実装では削除）
    async def _mock_brave_search(self,
                                 query: str,
                                 max_results: int) -> List[Dict[str, str]]:
        """Brave Search のモック"""
        return [
            {
                "title": f"検索結果 1: {query}",
                "url": "https://example.com/result1",
                "content": f"これは{query}に関する情報です。",
                "summary": f"{query}の概要説明"
            }
        ]
    
    async def _mock_ref_search(self,
                               query: str,
                               max_results: int) -> List[Dict[str, str]]:
        """Ref Search のモック"""
        return [
            {
                "title": f"技術文書: {query}",
                "url": "https://docs.example.com/guide",
                "content": f"{query}の技術的な説明です。"
            }
        ]
    
    async def _mock_github_search(self,
                                  query: str,
                                  max_results: int) -> List[Dict[str, str]]:
        """GitHub Search のモック"""
        return [
            {
                "title": f"GitHub Issue: {query}",
                "url": "https://github.com/example/repo/issues/123",
                "content": f"{query}に関するIssueの内容です。"
            }
        ]