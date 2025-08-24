# Aoi - Universal AI Agent Ecosystem

**🌐 Language**: [English](README.md) | [日本語](README.ja.md)

![Aoi Logo](https://img.shields.io/badge/Aoi-Universal_AI_Agent-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-green?style=flat-square)
![Agno](https://img.shields.io/badge/Agno-Framework-orange?style=flat-square)
![Gemini](https://img.shields.io/badge/Gemini-LLM-purple?style=flat-square)
![Status](https://img.shields.io/badge/Status-Production_Ready-brightgreen?style=flat-square)

## 📖 Overview

**Aoi (葵)** is a revolutionary cross-platform AI agent ecosystem that seamlessly integrates with your daily workflow. Named after the Japanese word for "hollyhock," Aoi embodies growth, adaptability, and natural intelligence.

### 🌟 What Makes Aoi Special

**Aoi** represents the culmination of modern AI agent technology, featuring:
- **Cross-Platform Intelligence**: Seamlessly works across Obsidian, browsers, and web interfaces
- **Persistent Memory**: Remembers context and conversations across all platforms
- **Personality-Driven Interaction**: Features a caring, knowledgeable AI personality that adapts to your needs
- **Evidence-Based Responses**: Always provides sources and reasoning for its answers
- **Real-Time Knowledge Integration**: Automatically syncs with your Obsidian knowledge base

### 🎯 Key Features

- **🌐 Cross-Platform Integration**: Works seamlessly across Obsidian, browsers, and web interfaces
- **🧠 Intelligent Memory System**: Persistent memory that spans all platforms and conversations
- **👥 Adaptive Personality**: Three distinct personality modes (Professional, Caring Sister, Casual)
- **📚 Knowledge Base Integration**: Real-time sync with your Obsidian vault
- **🔍 Evidence-Based AI**: Always provides sources and reasoning for responses
- **⚡ Real-Time Sync**: Instant synchronization across all connected platforms

## ⚡ Platform Integrations

### 🔧 Available Platforms

- **📝 Obsidian Plugin**: Native integration with your knowledge management workflow
- **🌐 Browser Extension**: AI assistance on any website with context awareness
- **💻 Web Interface**: Full-featured web application for comprehensive interactions
- **🔗 Cross-Platform Memory**: Seamless conversation continuity across all platforms
- **📊 Unified Dashboard**: Monitor and manage AI interactions from a single interface

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
Aoi Cross-Platform Ecosystem
┌─────────────────────────────────────────────────────────────────┐
│                     Cross-Platform Layer                       │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  Obsidian Plugin│ Browser Extension│      Web Interface          │
│   (Knowledge)   │  (Web Context)  │    (Full Features)          │
├─────────────────┴─────────────────┴─────────────────────────────┤
│                    Unified Memory System                       │
│              (Cross-Platform Synchronization)                  │
├─────────────────────────────────────────────────────────────────┤
│                     Core Agent (Agno)                          │
│                  ┌─────────────────────┐                       │
│                  │   Aoi Personality   │                       │
│                  │     (葵 System)     │                       │
│                  └─────────────────────┘                       │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   Gemini LLM    │  Vector Search  │      Session Store          │
│   (Reasoning)   │ (Weaviate+Jina) │       (Redis)              │
├─────────────────┴─────────────────┴─────────────────────────────┤
│                   Knowledge Base (Obsidian)                    │
│                  Real-time Sync & Evidence                     │
└─────────────────────────────────────────────────────────────────┘
```

### 📁 Directory Structure

```
Aoi/
├── services/
│   └── core-agent/           # Python Agno Core Service
│       ├── src/
│       │   ├── aoi/          # Aoi Agent Implementation
│       │   │   ├── core/     # Core Agent Logic
│       │   │   ├── memory/   # Cross-Platform Memory
│       │   │   ├── personality/ # Aoi Personality System
│       │   │   └── platforms/   # Platform Adapters
│       │   ├── knowledge/    # Knowledge Base Management
│       │   ├── tools/        # Custom Tools & MCP Integration
│       │   └── api/          # FastAPI Routes
│       ├── requirements.txt
│       ├── Dockerfile
│       └── .env.example
├── obsidian-plugin/          # Obsidian Plugin (TypeScript)
│   ├── main.ts              # Plugin Main Logic (1194 lines)
│   ├── manifest.json        # Plugin Manifest
│   ├── settings.ts          # Settings Management
│   └── README.md            # Plugin Documentation
├── browser-extension/        # Browser Extension (Manifest V3)
│   ├── manifest.json        # Extension Manifest
│   ├── content.js           # Content Script
│   ├── background.js        # Background Script
│   └── popup.html           # Extension Popup
├── agent-ui/                # Next.js Web Interface
│   ├── src/
│   │   ├── components/      # UI Components
│   │   ├── pages/          # Page Definitions
│   │   └── store/          # State Management
│   └── package.json
├── obsidian-data/           # Knowledge Base (.md files)
├── docker-compose.yml       # Infrastructure Configuration
├── README.md               # English Documentation
├── README.ja.md            # Japanese Documentation
├── DEVELOPMENT_PLAN.md     # Development Roadmap
└── .env.example            # Environment Variables Template
```

## 🚀 Quick Start

### 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+** (for web interface)
- **Docker & Docker Compose**
- **Git**
- **Obsidian** (for plugin integration)
- **Modern Browser** (Chrome, Firefox, Edge for extension)

### 🔑 Required API Keys

Obtain the following API keys in advance:

1. **Google AI Studio**: [Gemini API Key](https://makersuite.google.com/app/apikey)
2. **Jina AI**: [Jina Embeddings API Key](https://jina.ai/)
3. **Weaviate Cloud**: [Weaviate API Key](https://console.weaviate.cloud/) (Optional)
4. **Agno**: [Agno API Key](https://app.agno.com/) (Optional)

### 🎯 Current Implementation Status

- ✅ **Obsidian Plugin**: Fully implemented with personality system and cross-platform memory
- ✅ **Browser Extension**: Basic structure ready for implementation
- ✅ **Core Agent**: Foundation with Agno framework and cross-platform adapters
- 🚧 **Web Interface**: Planned for future development
- ✅ **Cross-Platform Memory**: Implemented and tested

### ⚙️ Installation Steps

#### 1. Clone Repository

```bash
git clone https://github.com/your-username/Aoi.git
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

#### 4. Install Obsidian Plugin

```bash
# Copy plugin to Obsidian plugins directory
cp -r obsidian-plugin/ /path/to/your/vault/.obsidian/plugins/aoi-agent/

# Or create symbolic link for development
ln -s $(pwd)/obsidian-plugin /path/to/your/vault/.obsidian/plugins/aoi-agent
```

1. Open Obsidian
2. Go to Settings → Community Plugins
3. Enable "Aoi Agent" plugin
4. Configure memory server URL and platform settings

#### 5. Install Browser Extension (Optional)

**Chrome/Edge:**
1. Open `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `browser-extension/` directory

**Firefox:**
1. Open `about:debugging`
2. Click "This Firefox"
3. Click "Load Temporary Add-on"
4. Select `browser-extension/manifest.json`

#### 6. Start Core Agent Service (Optional)

```bash
cd services/core-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start agent service
python src/main.py
```

#### 7. Access Points

- **Obsidian Plugin**: Available in Obsidian command palette (Ctrl/Cmd + P)
- **Browser Extension**: Click extension icon in browser toolbar
- **Core Agent API**: http://localhost:7777 (when running)
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

### Obsidian Plugin Usage

1. **Open Command Palette**: `Ctrl/Cmd + P`
2. **Search for Aoi commands**:
   - `Aoi: Chat with Agent` - Start conversation
   - `Aoi: Analyze Current Note` - Analyze active note
   - `Aoi: Generate Summary` - Create note summary
   - `Aoi: Memory Sync` - Sync cross-platform memory

3. **Personality System**:
   - Configure agent personality in plugin settings
   - Adaptive responses based on your interaction style
   - Consistent personality across platforms

### Browser Extension Usage

1. **Click Extension Icon** in browser toolbar
2. **Context-Aware Assistance**:
   - Analyze current webpage content
   - Extract and summarize information
   - Generate insights from web content

3. **Cross-Platform Memory**:
   - Seamlessly access Obsidian notes
   - Sync insights across platforms
   - Maintain conversation context

### Core Agent API Usage

```python
import requests

# Send message to agent
response = requests.post('http://localhost:7777/chat', json={
    'message': 'Analyze this code snippet',
    'context': 'python development',
    'platform': 'api'
})

print(response.json())
```

### 🔍 Knowledge Base Search

```python
# Direct usage example with Python API
from aoi_agent import AoiAgent

agent = AoiAgent()
response = agent.search_knowledge("Tell me about machine learning")
print(response)
```

### Advanced Features

- **Cross-Platform Memory**: Seamless context sharing between Obsidian, browser, and API
- **Adaptive Personality**: Consistent AI personality that learns from your interactions
- **Evidence-Based Responses**: All insights backed by your knowledge base
- **Real-time Sync**: Instant synchronization across all platforms

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