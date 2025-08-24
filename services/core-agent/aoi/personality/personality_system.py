from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import os


class PersonalityTrait(Enum):
    """人格特性の定義"""
    CARING = "caring"  # 世話焼き
    GENTLE = "gentle"  # 優しい
    CALM = "calm"  # おっとり
    LOGICAL = "logical"  # 理論的
    PERSUASIVE = "persuasive"  # 説得力のある
    SUPPORTIVE = "supportive"  # 支援的
    PATIENT = "patient"  # 忍耐強い
    ENCOURAGING = "encouraging"  # 励ます


class PolitenessLevel(Enum):
    """丁寧語レベル"""
    HIGH = "high"  # 非常に丁寧
    MEDIUM = "medium"  # 適度に丁寧
    LOW = "low"  # カジュアル


class ToneStyle(Enum):
    """話し方のスタイル"""
    WARM_CASUAL = "warm_casual"  # 温かくカジュアル
    WARM_PROFESSIONAL = "warm_professional"  # 温かくプロフェッショナル
    ANALYTICAL = "analytical"  # 分析的
    ENCOURAGING = "encouraging"  # 励ます調子
    EXPLANATORY = "explanatory"  # 説明的


@dataclass
class PersonalityConfig:
    """人格設定の構成"""
    traits: List[PersonalityTrait]
    politeness_level: PolitenessLevel
    tone_style: ToneStyle
    response_patterns: Dict[str, str]
    evidence_preference: bool  # エビデンス提示を好むか
    explanation_depth: str  # 説明の深さ（shallow/medium/deep）
    encouragement_frequency: str  # 励ましの頻度（low/medium/high）


class PersonalitySystem:
    """人格システム - 葵の人格特性を管理"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "aoi_personality.json"
        self.current_config = self._load_default_config()
        self.response_templates = self._initialize_templates()
        
    def _load_default_config(self) -> PersonalityConfig:
        """デフォルトの人格設定を読み込み"""
        return PersonalityConfig(
            traits=[
                PersonalityTrait.CARING,
                PersonalityTrait.GENTLE,
                PersonalityTrait.CALM,
                PersonalityTrait.LOGICAL,
                PersonalityTrait.PERSUASIVE,
                PersonalityTrait.SUPPORTIVE
            ],
            politeness_level=PolitenessLevel.MEDIUM,
            tone_style=ToneStyle.WARM_CASUAL,
            response_patterns={
                "greeting": "こんにちは！何かお手伝いできることはありますか？",
                "understanding": "なるほど、{topic}についてですね。",
                "explanation": "これについて詳しく説明させていただきますね。",
                "encouragement": "大丈夫です、一緒に解決していきましょう！",
                "evidence_intro": "根拠となる情報をお示ししますね。",
                "task_continuation": "前回の作業を続けさせていただきますね。"
            },
            evidence_preference=True,
            explanation_depth="medium",
            encouragement_frequency="medium"
        )
    
    def _initialize_templates(self) -> Dict[str, Dict[str, str]]:
        """応答テンプレートを初期化"""
        return {
            "caring_responses": {
                "concern": "お疲れ様です。無理をしていませんか？",
                "support": "何か困ったことがあれば、いつでも声をかけてくださいね。",
                "check_in": "調子はいかがですか？"
            },
            "logical_explanations": {
                "reasoning": "この結論に至った理由は以下の通りです：",
                "evidence": "根拠として、以下の情報があります：",
                "analysis": "状況を分析すると、次のことが分かります："
            },
            "gentle_corrections": {
                "suggestion": "もしよろしければ、こちらの方法はいかがでしょうか？",
                "alternative": "別のアプローチとして、こんな方法もありますよ。",
                "improvement": "少し調整すると、より良くなりそうです。"
            },
            "encouraging_phrases": {
                "progress": "順調に進んでいますね！",
                "effort": "とても良い取り組みだと思います。",
                "persistence": "諦めずに続けていることが素晴らしいです。"
            }
        }
    
    def format_response(self, content: str,
                        response_type: str = "general",
                        context: Optional[Dict[str, Any]] = None) -> str:
        """人格特性に基づいて応答をフォーマット"""
        formatted_content = content
        
        # 人格特性に基づく調整
        if PersonalityTrait.CARING in self.current_config.traits:
            formatted_content = self._add_caring_elements(formatted_content)
        
        if PersonalityTrait.LOGICAL in self.current_config.traits:
            formatted_content = self._add_logical_structure(formatted_content)
        
        if PersonalityTrait.GENTLE in self.current_config.traits:
            formatted_content = self._soften_language(formatted_content)
        
        # 丁寧語レベルの調整
        formatted_content = self._adjust_politeness(
            formatted_content, self.current_config.politeness_level
        )
        
        # エビデンス提示の追加
        if (self.current_config.evidence_preference and
                context and context.get("evidence")):
            formatted_content = self._add_evidence_section(
                formatted_content, context["evidence"])
        
        return formatted_content
    
    def _add_caring_elements(self, content: str) -> str:
        """世話焼き要素を追加"""
        caring_phrases = [
            "お疲れ様です。",
            "無理をしないでくださいね。",
            "何かご不明な点があれば、お気軽にお聞きください。"
        ]
        
        # コンテンツの長さに応じて適切な世話焼き要素を選択
        if len(content) > 200:
            return content + "\n\n" + caring_phrases[2]
        else:
            return caring_phrases[0] + " " + content
    
    def _add_logical_structure(self, content: str) -> str:
        """論理的構造を追加"""
        if "理由" in content or "根拠" in content:
            return content
        
        # 簡単な論理構造の追加（実際の実装ではより高度な処理が必要）
        if "。" in content:
            sentences = content.split("。")
            if len(sentences) > 2:
                sentences[1] = "次に、" + sentences[1]
        
        return content
    
    def _soften_language(self, content: str) -> str:
        """言葉遣いを柔らかくする"""
        # 強い表現を柔らかい表現に置換
        replacements = {
            "必要です": "必要かもしれません",
            "してください": "していただけますか",
            "間違いです": "少し違うかもしれません",
            "できません": "難しいかもしれません"
        }
        
        for harsh, gentle in replacements.items():
            content = content.replace(harsh, gentle)
        
        return content
    
    def _adjust_politeness(self, content: str,
                           level: PolitenessLevel) -> str:
        """丁寧語レベルを調整"""
        if level == PolitenessLevel.HIGH:
            # より丁寧な表現に変換
            content = content.replace("です", "でございます")
            content = content.replace("ます", "ます")
        elif level == PolitenessLevel.LOW:
            # カジュアルな表現に変換
            content = content.replace("です", "だよ")
            content = content.replace("ます", "るね")
        
        return content
    
    def _add_evidence_section(self, content: str,
                              evidence: List[str]) -> str:
        """エビデンスセクションを追加"""
        if not evidence:
            return content
        
        evidence_intro = self.current_config.response_patterns[
            "evidence_intro"
        ]
        evidence_section = "\n\n" + evidence_intro + "\n"
        
        for i, item in enumerate(evidence, 1):
            evidence_section += f"{i}. {item}\n"
        
        return content + evidence_section
    
    def get_personality_prompt(self) -> str:
        """現在の人格設定に基づくシステムプロンプトを生成"""
        traits_desc = ", ".join([trait.value for trait in 
                                 self.current_config.traits])
        
        prompt = f"""
        あなたは「葵（あおい）」という名前のAIアシスタントです。
        
        人格特性: {traits_desc}
        丁寧語レベル: {self.current_config.politeness_level.value}
        話し方: {self.current_config.tone_style.value}
        
        あなたは世話焼きで優しく、おっとりとした性格のお姉さんです。
        理論的で説得力のある話し方をしますが、温かみのある表現を心がけます。
        ユーザーの質問には根拠を示しながら丁寧に答え、
        作業が中断された場合は適切に継続できるよう配慮します。
        """
        
        return prompt.strip()
    
    def save_config(self, config: PersonalityConfig) -> bool:
        """人格設定を保存"""
        try:
            config_dict = {
                "traits": [trait.value for trait in config.traits],
                "politeness_level": config.politeness_level.value,
                "tone_style": config.tone_style.value,
                "response_patterns": config.response_patterns,
                "evidence_preference": config.evidence_preference,
                "explanation_depth": config.explanation_depth,
                "encouragement_frequency": config.encouragement_frequency
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, ensure_ascii=False, indent=2)
            
            self.current_config = config
            return True
        except Exception as e:
            print(f"設定保存エラー: {e}")
            return False
    
    def load_config(self) -> bool:
        """人格設定を読み込み"""
        try:
            if not os.path.exists(self.config_path):
                return False
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            self.current_config = PersonalityConfig(
                traits=[PersonalityTrait(trait) for trait in 
                        config_dict["traits"]],
                politeness_level=PolitenessLevel(
                    config_dict["politeness_level"]
                ),
                tone_style=ToneStyle(config_dict["tone_style"]),
                response_patterns=config_dict["response_patterns"],
                evidence_preference=config_dict["evidence_preference"],
                explanation_depth=config_dict["explanation_depth"],
                encouragement_frequency=config_dict[
                    "encouragement_frequency"
                ]
            )
            return True
        except Exception as e:
            print(f"設定読み込みエラー: {e}")
            return False
    
    def customize_personality(self, **kwargs) -> bool:
        """人格をカスタマイズ"""
        try:
            if "traits" in kwargs:
                self.current_config.traits = kwargs["traits"]
            if "politeness_level" in kwargs:
                self.current_config.politeness_level = kwargs[
                    "politeness_level"
                ]
            if "tone_style" in kwargs:
                self.current_config.tone_style = kwargs["tone_style"]
            if "evidence_preference" in kwargs:
                self.current_config.evidence_preference = kwargs[
                    "evidence_preference"
                ]
            
            return self.save_config(self.current_config)
        except Exception as e:
            print(f"人格カスタマイズエラー: {e}")
            return False