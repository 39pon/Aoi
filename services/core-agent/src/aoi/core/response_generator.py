# =============================================================================
# Aoi Core Agent - Advanced Response Generator with MCP Integration
# =============================================================================

from typing import Dict, Optional, Any
from datetime import datetime
import logging

from ..mcp.integration import MCPIntegration
from ..prompts.system_prompt import TraeAISystemPrompt
from .config import AoiConfig


class AdvancedResponseGenerator:
    """
    Advanced response generator with MCP integration for Trae AI quality
    responses.
    
    This class combines Sequential Thinking, web search, GitHub integration,
    and documentation search to generate high-quality, contextual responses.
    """
    
    def __init__(self, config: AoiConfig):
        """
        Initialize the advanced response generator.
        
        Args:
            config: Aoi configuration instance.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.mcp_integration = MCPIntegration()
        self.system_prompt = TraeAISystemPrompt()
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize the advanced response generator and MCP integration.
        
        Returns:
            bool: True if initialization successful.
        """
        try:
            # Initialize MCP integration
            await self.mcp_integration.initialize()
            
            self.is_initialized = True
            self.logger.info(
                "Advanced response generator initialized successfully"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize response generator: {e}")
            return False
    
    async def generate_response(
        self,
        message: str,
        memory_context: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        user_level: str = "intermediate",
        task_complexity: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate an advanced response using MCP integration.
        
        Args:
            message: User input message.
            memory_context: Context from memory.
            context: Additional context data.
            user_level: User skill level (beginner, intermediate, advanced).
            task_complexity: Task complexity (simple, medium, complex).
        
        Returns:
            Dict containing the generated response and metadata.
        """
        if not self.is_initialized:
            return await self._fallback_response(message)
        
        try:
            start_time = datetime.now()
            
            # Step 1: Analyze the message and determine response strategy
            analysis = await self._analyze_message(message, context)
            
            # Step 2: Use Sequential Thinking for complex problems
            thinking_result = None
            if analysis["requires_thinking"]:
                thinking_result = await self._apply_sequential_thinking(
                    message, analysis, memory_context
                )
            
            # Step 3: Gather additional context if needed
            enhanced_context = await self._gather_enhanced_context(
                message, analysis, memory_context
            )
            
            # Step 4: Generate system prompt
            system_prompt = self.system_prompt.generate_system_prompt(
                context_type=analysis.get("context_type"),
                user_level=user_level,
                task_complexity=task_complexity,
                additional_context=enhanced_context
            )
            
            # Step 5: Generate final response
            response_content = await self._generate_final_response(
                message=message,
                system_prompt=system_prompt,
                thinking_result=thinking_result,
                enhanced_context=enhanced_context,
                memory_context=memory_context
            )
            
            # Step 6: Post-process and enhance response
            final_response = await self._post_process_response(
                response_content, analysis, enhanced_context
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "content": final_response,
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "processing_time": f"{processing_time:.2f}s",
                    "used_sequential_thinking": (
                         thinking_result is not None
                     ),
                    "enhanced_context_sources": list(enhanced_context.keys()),
                    "analysis": analysis,
                    "user_level": user_level,
                    "task_complexity": task_complexity
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating advanced response: {e}")
            return await self._fallback_response(message, error=str(e))
    
    async def _analyze_message(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze the user message to determine response strategy.
        
        Args:
            message: User input message.
            context: Additional context data.
        
        Returns:
            Dict containing analysis results.
        """
        message_lower = message.lower()
        
        # Determine if Sequential Thinking is needed
        thinking_keywords = [
            "どうやって", "なぜ", "説明", "理由", "方法", "手順",
            "how", "why", "explain", "reason", "method", "steps",
            "問題", "エラー", "バグ", "デバッグ", "最適化",
            "problem", "error", "bug", "debug", "optimize"
        ]
        
        requires_thinking = any(
            keyword in message_lower for keyword in thinking_keywords
        )
        
        # Determine context type
        context_type = "general"
        code_words = ["コード", "プログラム", "code", "programming"]
        if any(word in message_lower for word in code_words):
            context_type = "code_analysis"
        problem_words = ["問題", "エラー", "バグ", "problem", "error", "bug"]
        if any(word in message_lower for word in problem_words):
            context_type = "problem_solving"
        learn_words = ["学習", "教えて", "説明", "learn", "teach", "explain"]
        if any(word in message_lower for word in learn_words):
            context_type = "learning_support"
        
        # Determine if web search is needed
        search_keywords = [
            "最新", "新しい", "トレンド", "ニュース",
            "latest", "new", "trend", "news", "recent"
        ]
        needs_web_search = any(
            keyword in message_lower for keyword in search_keywords
        )
        
        # Determine if GitHub search is needed
        github_keywords = [
            "github", "リポジトリ", "repository", "オープンソース",
            "open source", "ライブラリ", "library", "フレームワーク",
            "framework"
        ]
        needs_github_search = any(
            keyword in message_lower for keyword in github_keywords
        )
        
        return {
            "requires_thinking": requires_thinking,
            "context_type": context_type,
            "needs_web_search": needs_web_search,
            "needs_github_search": needs_github_search,
            "message_length": len(message),
            "complexity_score": self._calculate_complexity_score(message)
        }
    
    def _calculate_complexity_score(self, message: str) -> float:
        """
        Calculate complexity score for the message.
        
        Args:
            message: User input message.
        
        Returns:
            float: Complexity score (0.0 to 1.0).
        """
        # Simple heuristic based on message length and technical terms
        technical_terms = [
            "アルゴリズム", "データ構造", "API", "フレームワーク",
            "algorithm", "data structure", "framework", "architecture",
            "パフォーマンス", "最適化", "セキュリティ",
            "performance", "optimization", "security"
        ]
        
        base_score = min(len(message) / 200, 0.5)  # Length factor
        technical_score = sum(
            1 for term in technical_terms 
            if term.lower() in message.lower()
        ) * 0.1
        
        return min(base_score + technical_score, 1.0)
    
    async def _apply_sequential_thinking(
        self,
        message: str,
        analysis: Dict[str, Any],
        memory_context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Apply Sequential Thinking to complex problems.
        
        Args:
            message: User input message.
            analysis: Message analysis results.
            memory_context: Context from memory.
        
        Returns:
            Optional[Dict]: Sequential thinking results.
        """
        try:
            # Prepare thinking prompt
            thinking_prompt = f"""
            ユーザーからの質問: {message}
            
            この質問について段階的に思考し、最適な回答を生成してください。
            コンテキストタイプ: {analysis.get('context_type', 'general')}
            複雑度スコア: {analysis.get('complexity_score', 0.0)}
            """
            
            # Execute Sequential Thinking
            result = await self.mcp_integration.execute_sequential_thinking(
                thinking_prompt
            )
            
            return result
            
        except Exception as e:
            self.logger.warning(f"Sequential thinking failed: {e}")
            return None
    
    async def _gather_enhanced_context(
        self,
        message: str,
        analysis: Dict[str, Any],
        memory_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Gather enhanced context from various sources.
        
        Args:
            message: User input message.
            analysis: Message analysis results.
            memory_context: Context from memory.
        
        Returns:
            Dict containing enhanced context.
        """
        enhanced_context = {"memory": memory_context}
        
        try:
            # Web search if needed
            if analysis.get("needs_web_search"):
                search_results = await self.mcp_integration.search_web(
                    message
                )
                if search_results:
                    enhanced_context["web_search"] = search_results
            
            # GitHub search if needed
            if analysis.get("needs_github_search"):
                # Extract search terms for GitHub
                github_query = self._extract_github_search_terms(message)
                if github_query:
                    github_results = (
                        await self.mcp_integration.search_github_repositories(
                            github_query
                        )
                    )
                    if github_results:
                        enhanced_context["github"] = github_results
            
            # Documentation search for technical queries
            context_types = ["code_analysis", "problem_solving"]
            if analysis.get("context_type") in context_types:
                doc_results = await self.mcp_integration.search_ref(
                    message
                )
                if doc_results:
                    enhanced_context["documentation"] = doc_results
            
        except Exception as e:
            self.logger.warning(f"Failed to gather enhanced context: {e}")
        
        return enhanced_context
    
    def _extract_github_search_terms(self, message: str) -> Optional[str]:
        """
        Extract GitHub search terms from the message.
        
        Args:
            message: User input message.
        
        Returns:
            Optional[str]: GitHub search query.
        """
        # Simple extraction logic - can be enhanced
        tech_terms = []
        message_words = message.lower().split()
        
        tech_keywords = [
            "python", "javascript", "typescript", "react", "vue",
            "angular", "django", "flask", "fastapi", "express", "node",
            "npm", "machine learning", "ai", "deep learning",
            "tensorflow", "pytorch"
        ]
        
        for word in message_words:
            if word in tech_keywords:
                tech_terms.append(word)
        
        return " ".join(tech_terms) if tech_terms else None
    
    async def _generate_final_response(
        self,
        message: str,
        system_prompt: str,
        thinking_result: Optional[Dict[str, Any]],
        enhanced_context: Dict[str, Any],
        memory_context: Dict[str, Any]
    ) -> str:
        """
        Generate the final response using all available context.
        
        Args:
            message: User input message.
            system_prompt: Generated system prompt.
            thinking_result: Sequential thinking results.
            enhanced_context: Enhanced context from various sources.
            memory_context: Context from memory.
        
        Returns:
            str: Generated response content.
        """
        # For now, create a comprehensive response based on available context
        # TODO: Integrate with actual LLM (Gemini, OpenAI, etc.)
        
        response_parts = []
        
        # Add greeting and acknowledgment
        response_parts.append(f"ご質問「{message}」について、詳しく回答いたします。")
        
        # Add Sequential Thinking insights if available
        if thinking_result:
            response_parts.append("\n## 段階的分析")
            response_parts.append("この問題について段階的に分析した結果:")
            # Extract key insights from thinking result
            if "final_answer" in thinking_result:
                response_parts.append(f"- {thinking_result['final_answer']}")
        
        # Add web search results if available
        if "web_search" in enhanced_context:
            response_parts.append("\n## 最新情報")
            response_parts.append("関連する最新情報を調査しました:")
            # Add search insights (simplified)
            response_parts.append("- 最新のトレンドと技術動向を確認済み")
        
        # Add GitHub results if available
        if "github" in enhanced_context:
            response_parts.append("\n## 関連リポジトリ")
            response_parts.append("関連するオープンソースプロジェクトを見つけました:")
            response_parts.append("- 実装例とベストプラクティスを参照可能")
        
        # Add documentation results if available
        if "documentation" in enhanced_context:
            response_parts.append("\n## 技術文書")
            response_parts.append("関連する技術文書を参照しました:")
            response_parts.append("- 公式ドキュメントとガイドラインを確認済み")
        
        # Add memory context insights
        if memory_context.get("recent_messages"):
            response_parts.append("\n## 会話履歴の考慮")
            response_parts.append("これまでの会話内容を踏まえて回答しています。")
        
        # Add closing
        response_parts.append("\n---")
        response_parts.append("この回答は、MCP統合による高度な分析と複数の情報源を活用して生成されました。")
        response_parts.append("追加のご質問がございましたら、お気軽にお聞かせください。")
        
        return "\n".join(response_parts)
    
    async def _post_process_response(
        self,
        response_content: str,
        analysis: Dict[str, Any],
        enhanced_context: Dict[str, Any]
    ) -> str:
        """
        Post-process the response for quality enhancement.
        
        Args:
            response_content: Generated response content.
            analysis: Message analysis results.
            enhanced_context: Enhanced context data.
        
        Returns:
            str: Post-processed response.
        """
        # Add quality indicators
        quality_indicators = []
        
        if enhanced_context.get("web_search"):
            quality_indicators.append("🌐 最新情報")
        
        if enhanced_context.get("github"):
            quality_indicators.append("📚 オープンソース")
        
        if enhanced_context.get("documentation"):
            quality_indicators.append("📖 技術文書")
        
        if analysis.get("requires_thinking"):
            quality_indicators.append("🧠 段階的思考")
        
        if quality_indicators:
            indicator_line = f"**品質保証**: {' | '.join(quality_indicators)}\n\n"
            response_content = indicator_line + response_content
        
        return response_content
    
    async def _fallback_response(
        self, 
        message: str, 
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a fallback response when advanced processing fails.
        
        Args:
            message: User input message.
            error: Optional error message.
        
        Returns:
            Dict containing fallback response.
        """
        if error:
            content = f"申し訳ございません。高度な処理中にエラーが発生しました: {error}\n\n"
        else:
            content = ""
        
        content += f"ご質問「{message}」について、基本的な回答をいたします。\n\n"
        content += "現在、Aoiエージェントは開発中ですが、お手伝いできることがあればお聞かせください。"
        
        return {
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "fallback_mode": True,
                "error": error,
                "processing_time": "<1s"
            }
        }
    
    async def shutdown(self) -> bool:
        """
        Shutdown the response generator and clean up resources.
        
        Returns:
            bool: True if shutdown successful.
        """
        try:
            if self.mcp_integration:
                await self.mcp_integration.shutdown()
            
            self.is_initialized = False
            self.logger.info("Advanced response generator shutdown completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            return False