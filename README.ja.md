# 葵（Aoi）- 万能型AIエージェントエコシステム

![Aoi Logo](https://img.shields.io/badge/Aoi-万能型AIエージェント-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-green?style=flat-square)
![Agno](https://img.shields.io/badge/Agno-Framework-orange?style=flat-square)
![Gemini](https://img.shields.io/badge/Gemini-LLM-purple?style=flat-square)

## 📖 概要

**葵（Aoi）** は、最新のAI技術を統合した万能型AIエージェントエコシステムです。Agnoフレームワークをベースに、Gemini LLM、Weaviate、Jina、Redis、Obsidianを組み合わせて、高性能で拡張性の高いAIエージェントを実現します。

### 🎯 主な特徴

- **🤖 万能型エージェント**: あらゆるタスクに対応可能な汎用AIエージェント
- **🧠 高度な推論**: Agnoフレームワークによる高性能な推論機能
- **📚 知識ベース**: Obsidianで管理された.mdファイルからの知識抽出
- **🔍 ベクトル検索**: Weaviate + Jinaによる高精度な意味検索
- **💾 セッション管理**: Redisによる永続的な会話履歴管理
- **🌐 Web UI**: 直感的で美しいユーザーインターフェース

## ⚡ 機能

### 🔧 コア機能

- **マルチモーダル対応**: テキスト、画像、音声、動画の処理
- **リアルタイム推論**: 高速な応答生成と意思決定
- **知識統合**: Obsidianボルトからの自動知識抽出
- **セッション永続化**: 長期記憶による文脈理解
- **カスタムツール**: 拡張可能なツールシステム

### 🛠️ 技術スタック

| コンポーネント | 技術 | 用途 |
|---------------|------|------|
| **AIフレームワーク** | Agno | エージェント基盤 |
| **LLM** | Google Gemini | 言語モデル |
| **ベクトルDB** | Weaviate | 意味検索 |
| **エンベッディング** | Jina | ベクトル化 |
| **データベース** | Redis | セッション管理 |
| **知識管理** | Obsidian | .mdファイル管理 |
| **UI** | Next.js | Webインターフェース |
| **インフラ** | Docker | コンテナ化 |

## 🏗️ アーキテクチャ

```
葵（Aoi）エコシステム
┌─────────────────────────────────────────────────────────┐
│                    Web UI (Next.js)                    │
├─────────────────────────────────────────────────────────┤
│                  API Gateway (FastAPI)                 │
├─────────────────────────────────────────────────────────┤
│                 Aoi Agent (Agno Core)                  │
├─────────────────┬─────────────────┬─────────────────────┤
│   Gemini LLM    │  Vector Search  │   Session Store     │
│   (Reasoning)   │  (Weaviate+Jina)│     (Redis)        │
├─────────────────┴─────────────────┴─────────────────────┤
│              Knowledge Base (Obsidian)                 │
└─────────────────────────────────────────────────────────┘
```

### 📁 ディレクトリ構造

```
Aoi/
├── agent-ui/                 # Next.js Webインターフェース
│   ├── src/
│   │   ├── components/        # UIコンポーネント
│   │   ├── pages/            # ページ定義
│   │   └── store/            # 状態管理
│   └── package.json
├── services/
│   └── aoi-agent/            # Python Agnoサービス
│       ├── src/
│       │   ├── agent/        # エージェント実装
│       │   ├── knowledge/    # 知識ベース管理
│       │   ├── tools/        # カスタムツール
│       │   └── api/          # FastAPI routes
│       ├── requirements.txt
│       ├── Dockerfile
│       └── .env.example
├── obsidian-data/            # 知識ベース（.mdファイル）
├── docker-compose.yml        # インフラ設定
├── README.md                 # 英語版ドキュメント
├── README.ja.md             # 日本語版ドキュメント
└── .env.example             # 環境変数テンプレート
```

## 🚀 クイックスタート

### 📋 前提条件

- **Python 3.11+**
- **Node.js 18+**
- **Docker & Docker Compose**
- **Git**

### 🔑 必要なAPIキー

以下のAPIキーを事前に取得してください：

1. **Google AI Studio**: [Gemini API Key](https://makersuite.google.com/app/apikey)
2. **Jina AI**: [Jina Embeddings API Key](https://jina.ai/)
3. **Weaviate Cloud**: [Weaviate API Key](https://console.weaviate.cloud/) (オプション)
4. **Agno**: [Agno API Key](https://app.agno.com/) (オプション)

### ⚙️ インストール手順

#### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd Aoi
```

#### 2. 環境変数の設定

```bash
# .envファイルを作成
cp .env.example .env

# 必要なAPIキーを設定
vim .env
```

#### 3. Dockerでインフラを起動

```bash
# Redis、Weaviateなどを起動
docker-compose up -d
```

#### 4. Agnoエージェントサービスの起動

```bash
cd services/aoi-agent

# 仮想環境の作成
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt

# エージェントサービスの起動
python src/main.py
```

#### 5. Web UIの起動

```bash
cd agent-ui

# 依存関係のインストール
pnpm install

# 開発サーバーの起動
pnpm dev
```

#### 6. アクセス

- **Web UI**: http://localhost:3000
- **API**: http://localhost:7777
- **Weaviate**: http://localhost:8080
- **Redis**: localhost:6379

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

### 💬 基本的な対話

1. Web UI（http://localhost:3000）にアクセス
2. チャット画面で質問を入力
3. 葵が知識ベースを検索して回答

### 🔍 知識ベース検索

```python
# Python APIでの直接利用例
from aoi_agent import AoiAgent

agent = AoiAgent()
response = agent.search_knowledge("機械学習について教えて")
print(response)
```

### 🛠️ カスタムツールの追加

```python
# services/aoi-agent/src/tools/custom_tool.py
from agno.tools import Tool

class CustomTool(Tool):
    def __init__(self):
        super().__init__(name="custom_tool", description="カスタムツール")
    
    def execute(self, query: str) -> str:
        # カスタム処理
        return f"処理結果: {query}"
```

## 🔧 開発・カスタマイズ

### 🧪 テスト実行

```bash
# Agnoエージェントのテスト
cd services/aoi-agent
pytest tests/

# Web UIのテスト
cd agent-ui
pnpm test
```

### 📊 監視・ログ

- **Agno Dashboard**: https://app.agno.com/
- **ログファイル**: `services/aoi-agent/logs/`
- **メトリクス**: Prometheus + Grafana（オプション）

## 🤝 コントリビューション

1. フォークしてブランチを作成
2. 変更を実装
3. テストを実行
4. プルリクエストを作成

## 📄 ライセンス

MIT License - 詳細は[LICENSE](LICENSE)ファイルを参照

## 🆘 サポート

- **Issues**: [GitHub Issues](https://github.com/your-repo/aoi/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/aoi/discussions)
- **Documentation**: [Wiki](https://github.com/your-repo/aoi/wiki)

---

**葵（Aoi）で、AIエージェントの新しい可能性を探求しましょう！** 🚀✨