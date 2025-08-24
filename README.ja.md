# 葵（Aoi）- クロスプラットフォームAIエージェントエコシステム

**[English](README.md) | 日本語**

![Aoi Logo](https://img.shields.io/badge/Aoi-クロスプラットフォームAI-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-実装完了-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-green?style=flat-square)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue?style=flat-square)
![Obsidian](https://img.shields.io/badge/Obsidian-Plugin-purple?style=flat-square)
![Browser](https://img.shields.io/badge/Browser-Extension-orange?style=flat-square)

## 📖 概要

**葵（Aoi）** は、複数のプラットフォームで一貫したAI体験を提供するクロスプラットフォームAIエージェントエコシステムです。Obsidianプラグイン、ブラウザ拡張機能、Core Agentを通じて、どこからでもアクセス可能な統合されたAIアシスタントを実現します。

### 🎯 主な特徴

- **🔗 クロスプラットフォーム統合**: Obsidian、ブラウザ、APIで一貫したAI体験
- **🧠 インテリジェントメモリシステム**: プラットフォーム間で共有される永続的なメモリ
- **🎭 適応型パーソナリティ**: ユーザーの操作スタイルに適応する一貫したAIペルソナ
- **📚 知識ベース統合**: Obsidianノートとの深い統合による文脈理解
- **🔍 エビデンスベースAI**: すべての回答が知識ベースに基づく信頼性の高いAI
- **⚡ リアルタイム同期**: プラットフォーム間での瞬時の情報同期

## ⚡ 機能

### 🔧 コア機能

- **クロスプラットフォーム統合**: Obsidian、ブラウザ、APIでの統一されたAI体験
- **インテリジェントメモリシステム**: プラットフォーム間で共有される永続的なコンテキスト
- **適応型パーソナリティ**: ユーザーの操作パターンに学習・適応するAIペルソナ
- **知識ベース統合**: Obsidianノートからの自動知識抽出と活用
- **エビデンスベースAI**: 知識ベースに基づく信頼性の高い回答生成
- **リアルタイム同期**: プラットフォーム間での瞬時の情報同期

### 🌐 プラットフォーム統合

- **📝 Obsidianプラグイン**: ノート作成・分析・要約機能
- **🌐 ブラウザ拡張機能**: Webページの文脈理解とインサイト生成
- **🔗 Webインターフェース**: 統合ダッシュボードとAPI管理
- **💾 クロスプラットフォームメモリ**: 全プラットフォーム間での記憶共有
- **📊 統合ダッシュボード**: 全体的な使用状況とインサイトの可視化

### 🛠️ 技術スタック

| コンポーネント | 技術 | 用途 |
|---------------|------|------|
| **Obsidianプラグイン** | TypeScript | ノート統合・メモリ管理 |
| **ブラウザ拡張** | JavaScript/TypeScript | Web統合・コンテキスト抽出 |
| **Core Agent** | Python/Agno | AI推論・API提供 |
| **LLM** | Google Gemini | 言語理解・生成 |
| **ベクトルDB** | Weaviate | 意味検索・知識管理 |
| **エンベッディング** | Jina | テキストベクトル化 |
| **データベース** | Redis | セッション・メモリ管理 |
| **インフラ** | Docker | コンテナ化・デプロイ |

## 🏗️ アーキテクチャ

```
葵（Aoi）クロスプラットフォームエコシステム
┌─────────────────────────────────────────────────────────────────┐
│                    クロスプラットフォームレイヤー                      │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  Obsidianプラグイン │   ブラウザ拡張機能   │      Webインターフェース      │
│   (TypeScript)  │  (JavaScript)   │       (Next.js)           │
├─────────────────┴─────────────────┴─────────────────────────────┤
│                      統合メモリシステム                           │
│              (クロスプラットフォーム同期・永続化)                    │
├─────────────────────────────────────────────────────────────────┤
│                     Core Agent (Python)                       │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   Gemini LLM    │  Vector Search  │      Session Store          │
│   (推論・生成)    │ (Weaviate+Jina) │       (Redis)              │
├─────────────────┴─────────────────┴─────────────────────────────┤
│                   Knowledge Base (Obsidian)                   │
└─────────────────────────────────────────────────────────────────┘
```

### 📁 ディレクトリ構造

```
Aoi/
├── obsidian-plugin/          # Obsidianプラグイン (TypeScript)
│   ├── main.ts              # プラグインメイン
│   ├── memory-client.ts     # メモリシステム統合
│   ├── personality.ts       # パーソナリティシステム
│   └── manifest.json        # プラグイン設定
├── browser-extension/        # ブラウザ拡張機能
│   ├── manifest.json        # 拡張機能設定
│   ├── content-script.js    # コンテンツスクリプト
│   ├── background.js        # バックグラウンドスクリプト
│   └── popup/              # ポップアップUI
├── services/
│   └── core-agent/          # Core Agent (Python)
│       ├── src/
│       │   ├── agent/       # エージェント実装
│       │   ├── memory/      # メモリシステム
│       │   ├── adapters/    # プラットフォームアダプター
│       │   └── api/         # FastAPI routes
│       ├── requirements.txt
│       └── config.py        # 設定管理
├── agent-ui/                # Webインターフェース (Next.js)
│   ├── src/
│   │   ├── components/      # UIコンポーネント
│   │   ├── pages/          # ページ定義
│   │   └── store/          # 状態管理
│   └── package.json
├── docker-compose.yml       # インフラ設定
├── README.md               # 英語版ドキュメント
├── README.ja.md           # 日本語版ドキュメント
└── .env.example           # 環境変数テンプレート
```

## 🚀 クイックスタート

### 📋 前提条件

- **Python 3.8+** (Core Agent用)
- **Node.js 16+** (Web UI用)
- **Obsidian** (プラグイン使用時)
- **モダンブラウザ** (Chrome, Firefox, Safari)
- **OpenAI API キー**

### 🚧 現在の実装状況

✅ **Obsidian Plugin** - TypeScriptで実装済み  
✅ **Browser Extension** - 基本機能実装済み  
✅ **Core Agent** - Python FastAPIで実装済み  
🚧 **Web Interface** - Next.js開発中  
✅ **Cross-Platform Memory** - 統合メモリシステム実装済み

### ⚙️ インストール手順

#### 1. リポジトリのクローン

```bash
git clone https://github.com/39pon/Aoi.git
cd Aoi
```

#### 2. Obsidianプラグインのインストール

```bash
# Obsidianのプラグインフォルダにコピー
cp -r obsidian-plugin ~/.obsidian/plugins/aoi-agent/
```

#### 3. ブラウザ拡張機能のインストール

- **Chrome**: `chrome://extensions/` で開発者モードを有効にし、`browser-extension`フォルダを読み込み
- **Firefox**: `about:debugging` で一時的なアドオンとして読み込み

#### 4. Core Agentサービスの起動

```bash
cd services/core-agent
pip install -r requirements.txt
python simple_server.py
```

#### 5. アクセス

- **Obsidianプラグイン**: Obsidian内でAoiコマンドを実行
- **ブラウザ拡張機能**: ブラウザのツールバーアイコンをクリック
- **Core Agent API**: http://localhost:8002

## ⚙️ 詳細設定

### 🔐 環境変数

`.env`ファイルで以下の環境変数を設定してください：

```bash
# Gemini API
GOOGLE_API_KEY=your_gemini_api_key

# Jina Embeddings
JINA_API_KEY=your_jina_api_key

# Weaviate
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=your_weaviate_api_key  # クラウド使用時のみ

# Redis
REDIS_URL=redis://localhost:6379

# Obsidian
OBSIDIAN_VAULT_PATH=./obsidian-data

# Agno (オプション)
AGNO_API_KEY=your_agno_api_key

# サービス設定
AOI_AGENT_PORT=7777
AOI_AGENT_HOST=0.0.0.0
```

### 📚 Obsidian連携設定

1. **ボルトの配置**:
   ```bash
   # Obsidianボルトを配置
   cp -r /path/to/your/obsidian/vault ./obsidian-data
   ```

2. **自動同期の設定**:
   ```bash
   # 定期的な知識ベース更新
   # crontabまたはGitHub Actionsで自動化可能
   ```

### 🐳 Docker設定

`docker-compose.yml`でインフラサービスを管理：

```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  weaviate:
    image: semitechnologies/weaviate:latest
    ports:
      - "8080:8080"
    environment:
      QUERY_DEFAULTS_LIMIT: 25
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'true'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
    volumes:
      - weaviate_data:/var/lib/weaviate

volumes:
  redis_data:
  weaviate_data:
```

## 📖 使用方法

### Obsidianプラグインでの使用

1. **プラグインの有効化**
   - Obsidianの設定 > コミュニティプラグイン > Aoi Agentを有効化

2. **基本的な使い方**
   - コマンドパレット（Ctrl/Cmd + P）で「Aoi」と入力
   - ノート内でAoiコマンドを実行
   - 選択したテキストに対してAIアシスタンスを受ける

3. **メモリ機能**
   - 会話履歴が自動的に保存される
   - 過去の文脈を考慮した応答を受ける

### ブラウザ拡張機能での使用

1. **拡張機能の起動**
   - ブラウザのツールバーでAoiアイコンをクリック
   - ポップアップウィンドウが開く

2. **Webページとの連携**
   - 現在のページ内容を自動的に認識
   - ページに関する質問や要約を依頼
   - 選択したテキストに対する詳細な説明を取得

### Core Agent APIの直接利用

```bash
# チャット API
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, Aoi!", "platform": "api"}'

# メモリ検索 API
curl -X GET http://localhost:8002/memory/search?query=検索語

# パーソナリティ設定 API
curl -X POST http://localhost:8002/personality \
  -H "Content-Type: application/json" \
  -d '{"traits": ["helpful", "analytical"]}'
```

### 高度な機能

#### クロスプラットフォームメモリ
- Obsidian、ブラウザ、APIでの会話が統合される
- 一つのプラットフォームでの学習が他でも活用される
- 文脈の継続性が保たれる

#### 適応型パーソナリティ
- ユーザーの使用パターンに応じてAIの応答スタイルが調整される
- プラットフォーム固有の最適化が行われる
- 個人の好みに合わせたカスタマイズが可能

#### エビデンスベースの応答
- 回答に使用した情報源が明示される
- 信頼性の高い情報に基づく応答
- 知識ベースとの連携による正確性の向上

#### リアルタイム同期
- 複数デバイス間での即座の同期
- 会話状態の一貫性維持
- オフライン時の変更も自動同期

## 🔧 開発・カスタマイズ

### 🏗️ アーキテクチャの拡張

#### Obsidianプラグインの拡張

```typescript
// obsidian-plugin/custom-feature.ts
import { Plugin } from 'obsidian';
import { MemoryClient } from './memory-client';

export class CustomFeature {
    constructor(private plugin: Plugin, private memory: MemoryClient) {}
    
    async executeCustomLogic(input: string): Promise<string> {
        // カスタム機能の実装
        return await this.memory.processWithContext(input);
    }
}
```

#### ブラウザ拡張機能の拡張

```javascript
// browser-extension/custom-content-script.js
class CustomContentScript {
    constructor() {
        this.initializeCustomFeatures();
    }
    
    initializeCustomFeatures() {
        // ページ固有の機能を追加
        this.addCustomUI();
        this.setupEventListeners();
    }
}
```

#### Core Agentの拡張

```python
# services/core-agent/src/adapters/custom_adapter.py
from .base_adapter import BaseAdapter

class CustomAdapter(BaseAdapter):
    def __init__(self):
        super().__init__(platform="custom")
    
    async def process_message(self, message: str) -> str:
        # カスタムプラットフォーム用の処理
        return await self.agent.process_with_memory(message)
```

### 🎨 UI のカスタマイズ

```typescript
// agent-ui/src/components/CustomComponent.tsx
import React from 'react';
import { useMemoryStore } from '../store/memory';

const CustomComponent: React.FC = () => {
  const { memories, addMemory } = useMemoryStore();
  
  return (
    <div className="custom-component">
      {/* カスタムUI */}
    </div>
  );
};

export default CustomComponent;
```

### 🧪 テスト実行

```bash
# Core Agentのテスト
cd services/core-agent
pytest tests/

# Web UIのテスト
cd agent-ui
npm test

# Obsidianプラグインのテスト
cd obsidian-plugin
npm test
```

### 📊 監視・ログ

- **ログファイル**: `services/core-agent/logs/`
- **メトリクス**: Prometheus + Grafana（オプション）
- **デバッグ**: ブラウザ開発者ツール

## 🤝 コントリビューション

### 🐛 バグ報告

1. [Issues](https://github.com/39pon/Aoi/issues) で既存の報告を確認
2. 新しいIssueを作成
3. 再現手順、期待される動作、実際の動作を記載
4. 使用しているプラットフォーム（Obsidian/Browser/API）を明記

### ✨ 機能提案

1. [Discussions](https://github.com/39pon/Aoi/discussions) で議論
2. 機能の詳細、用途、実装案を提案
3. どのプラットフォームに影響するかを明記
4. コミュニティからのフィードバックを収集

### 🔧 プルリクエスト

1. フォークしてブランチを作成
2. 変更を実装（適切なプラットフォームで）
3. テストを追加・実行
4. プルリクエストを作成
5. 変更内容とテスト結果を詳細に記載

## 📄 ライセンス

MIT License - 詳細は[LICENSE](LICENSE)ファイルを参照

## 🙏 謝辞

- [Obsidian](https://obsidian.md/) - 知識管理プラットフォーム
- [TypeScript](https://www.typescriptlang.org/) - 型安全なJavaScript
- [FastAPI](https://fastapi.tiangolo.com/) - 高性能Webフレームワーク
- [Next.js](https://nextjs.org/) - Reactフレームワーク
- [Google Gemini](https://ai.google.dev/) - AI技術プラットフォーム

## 🆘 サポート

- **Issues**: [GitHub Issues](https://github.com/39pon/Aoi/issues)
- **Discussions**: [GitHub Discussions](https://github.com/39pon/Aoi/discussions)
- **Documentation**: [Wiki](https://github.com/39pon/Aoi/wiki)

---

**葵（Aoi）で、AIエージェントの新しい可能性を探求しましょう！** 🚀✨

> 「知識は力なり。しかし、知識を活用する知恵こそが真の力である。」
> 
> Aoiは、あなたの知識を単に保存するだけでなく、それを活用し、成長させ、あなたの思考を拡張するパートナーです。