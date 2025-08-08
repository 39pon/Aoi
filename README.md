# Aoi - Universal AI Agent Ecosystem

![Aoi Logo](https://img.shields.io/badge/Aoi-Universal_AI_Agent-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-green?style=flat-square)
![Agno](https://img.shields.io/badge/Agno-Framework-orange?style=flat-square)
![Gemini](https://img.shields.io/badge/Gemini-LLM-purple?style=flat-square)

## 📖 Overview

**Aoi** is a universal AI agent ecosystem that integrates cutting-edge AI technologies. Built on the Agno framework and combining Gemini LLM, Weaviate, Jina, Redis, and Obsidian, it delivers high-performance and highly scalable AI agents.

### 🎯 Key Features

- **🤖 Universal Agent**: Versatile AI agent capable of handling any task
- **🧠 Advanced Reasoning**: High-performance reasoning powered by Agno framework
- **📚 Knowledge Base**: Knowledge extraction from Obsidian-managed .md files
- **🔍 Vector Search**: High-precision semantic search with Weaviate + Jina
- **💾 Session Management**: Persistent conversation history with Redis
- **🌐 Web UI**: Intuitive and beautiful user interface

## ⚡ Features

### 🔧 Core Capabilities

- **Multimodal Support**: Processing text, images, audio, and video
- **Real-time Reasoning**: Fast response generation and decision making
- **Knowledge Integration**: Automatic knowledge extraction from Obsidian vaults
- **Session Persistence**: Long-term memory for contextual understanding
- **Custom Tools**: Extensible tool system

### 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|----------|
| **AI Framework** | Agno | Agent foundation |
| **LLM** | Google Gemini | Language model |
| **Vector DB** | Weaviate | Semantic search |
| **Embeddings** | Jina | Vectorization |
| **Database** | Redis | Session management |
| **Knowledge Management** | Obsidian | .md file management |
| **UI** | Next.js | Web interface |
| **Infrastructure** | Docker | Containerization |

## 🏗️ Architecture

```
Aoi Ecosystem
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

### 📁 Directory Structure

```
Aoi/
├── agent-ui/                 # Next.js Web Interface
│   ├── src/
│   │   ├── components/        # UI Components
│   │   ├── pages/            # Page Definitions
│   │   └── store/            # State Management
│   └── package.json
├── services/
│   └── aoi-agent/            # Python Agno Service
│       ├── src/
│       │   ├── agent/        # Agent Implementation
│       │   ├── knowledge/    # Knowledge Base Management
│       │   ├── tools/        # Custom Tools
│       │   └── api/          # FastAPI Routes
│       ├── requirements.txt
│       ├── Dockerfile
│       └── .env.example
├── obsidian-data/            # Knowledge Base (.md files)
├── docker-compose.yml        # Infrastructure Configuration
├── README.md                 # English Documentation
├── README.ja.md             # Japanese Documentation
└── .env.example             # Environment Variables Template
```

## 🚀 Quick Start

### 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Docker & Docker Compose**
- **Git**

### 🔑 Required API Keys

Obtain the following API keys in advance:

1. **Google AI Studio**: [Gemini API Key](https://makersuite.google.com/app/apikey)
2. **Jina AI**: [Jina Embeddings API Key](https://jina.ai/)
3. **Weaviate Cloud**: [Weaviate API Key](https://console.weaviate.cloud/) (Optional)
4. **Agno**: [Agno API Key](https://app.agno.com/) (Optional)

### ⚙️ Installation Steps

#### 1. Clone Repository

```bash
git clone <repository-url>
cd Aoi
```

#### 2. Configure Environment Variables

```bash
# Create .env file
cp .env.example .env

# Set required API keys
vim .env
```

#### 3. Start Infrastructure with Docker

```bash
# Start Redis, Weaviate, etc.
docker-compose up -d
```

#### 4. Start Agno Agent Service

```bash
cd services/aoi-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start agent service
python src/main.py
```

#### 5. Start Web UI

```bash
cd agent-ui

# Install dependencies
pnpm install

# Start development server
pnpm dev
```

#### 6. Access

- **Web UI**: http://localhost:3000
- **API**: http://localhost:7777
- **Weaviate**: http://localhost:8080
- **Redis**: localhost:6379

## ⚙️ Configuration

### 🔐 Environment Variables

Configure the following environment variables in the `.env` file:

```bash
# Gemini API
GOOGLE_API_KEY=your_gemini_api_key

# Jina Embeddings
JINA_API_KEY=your_jina_api_key

# Weaviate
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=your_weaviate_api_key  # Only for cloud usage

# Redis
REDIS_URL=redis://localhost:6379

# Obsidian
OBSIDIAN_VAULT_PATH=./obsidian-data

# Agno (Optional)
AGNO_API_KEY=your_agno_api_key

# Service Configuration
AOI_AGENT_PORT=7777
AOI_AGENT_HOST=0.0.0.0
```

### 📚 Obsidian Integration Setup

1. **Place Vault**:
   ```bash
   # Place your Obsidian vault
   cp -r /path/to/your/obsidian/vault ./obsidian-data
   ```

2. **Auto-sync Configuration**:
   ```bash
   # Periodic knowledge base updates
   # Can be automated with crontab or GitHub Actions
   ```

### 🐳 Docker Configuration

Manage infrastructure services with `docker-compose.yml`:

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

## 📖 Usage

### 💬 Basic Interaction

1. Access Web UI (http://localhost:3000)
2. Enter questions in the chat interface
3. Aoi searches the knowledge base and provides answers

### 🔍 Knowledge Base Search

```python
# Direct usage example with Python API
from aoi_agent import AoiAgent

agent = AoiAgent()
response = agent.search_knowledge("Tell me about machine learning")
print(response)
```

### 🛠️ Adding Custom Tools

```python
# services/aoi-agent/src/tools/custom_tool.py
from agno.tools import Tool

class CustomTool(Tool):
    def __init__(self):
        super().__init__(name="custom_tool", description="Custom tool")
    
    def execute(self, query: str) -> str:
        # Custom processing
        return f"Processing result: {query}"
```

## 🔧 Development & Customization

### 🧪 Running Tests

```bash
# Test Agno agent
cd services/aoi-agent
pytest tests/

# Test Web UI
cd agent-ui
pnpm test
```

### 📊 Monitoring & Logging

- **Agno Dashboard**: https://app.agno.com/
- **Log Files**: `services/aoi-agent/logs/`
- **Metrics**: Prometheus + Grafana (Optional)

## 🤝 Contributing

1. Fork and create a branch
2. Implement changes
3. Run tests
4. Create a pull request

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/aoi/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/aoi/discussions)
- **Documentation**: [Wiki](https://github.com/your-repo/aoi/wiki)

---

**Explore new possibilities with Aoi AI Agent!** 🚀✨