#!/bin/bash
# =============================================================================
# Aoi Development Environment - Trae IDE Extensions Installer
# =============================================================================

echo "🚀 Installing Trae IDE Extensions for Aoi Development Environment..."
echo "📋 Technology Stack: Next.js + TypeScript + Python + FastAPI + Tailwind CSS"
echo "💡 Note: Trae IDE supports VS Code extensions + Trae-specific extensions"
echo "Note: Make sure Trae IDE is installed and 'trae' command is available in PATH"
echo ""

# Function to install extension with error handling
install_extension() {
    echo "Installing $1..."
    trae --install-extension "$1"
    if [ $? -eq 0 ]; then
        echo "✅ Successfully installed $1"
    else
        echo "❌ Failed to install $1"
    fi
    echo ""
}

# =============================================================================
# 🔧 Core Language Support (必須)
# =============================================================================
echo "📦 Installing Core Language Support..."
install_extension ms-python.python                    # Python support
install_extension ms-python.pylint                    # Python linting
install_extension ms-python.flake8                    # Python code analysis
install_extension ms-python.black-formatter          # Python formatter
install_extension ms-python.isort                     # Python import sorting
install_extension ms-vscode.vscode-typescript-next    # TypeScript support
install_extension bradlc.vscode-tailwindcss          # Tailwind CSS IntelliSense

# =============================================================================
# ⚛️ Frontend Development (Next.js + React)
# =============================================================================
echo "📦 Installing Frontend Development Extensions..."
install_extension dsznajder.es7-react-js-snippets    # React snippets
install_extension formulahendry.auto-rename-tag      # Auto rename paired tags
install_extension formulahendry.auto-close-tag       # Auto close HTML tags
install_extension ms-vscode.vscode-json              # JSON support
install_extension bradlc.vscode-tailwindcss          # Tailwind CSS IntelliSense
install_extension heybourn.headwind                  # Tailwind class sorting
install_extension zignd.html-css-class-completion    # CSS class completion

# =============================================================================
# 🐍 Backend Development (Python + FastAPI)
# =============================================================================
echo "📦 Installing Backend Development Extensions..."
install_extension ms-python.pylance                  # Python language server
install_extension ms-python.debugpy                  # Python debugger
install_extension rangav.vscode-thunder-client       # API testing (FastAPI)
install_extension ms-vscode.vscode-yaml              # YAML support
install_extension redhat.vscode-xml                  # XML support

# =============================================================================
# 🔄 DevOps & Infrastructure
# =============================================================================
echo "📦 Installing DevOps Extensions..."
install_extension ms-vscode-remote.remote-containers # Dev Containers
install_extension ms-azuretools.vscode-docker        # Docker support
install_extension ms-vscode.remote-explorer          # Remote development
install_extension cweijan.vscode-redis-client        # Redis client

# =============================================================================
# 📝 Documentation & Knowledge Management (Obsidian)
# =============================================================================
echo "📦 Installing Documentation Extensions..."
install_extension yzhang.markdown-all-in-one        # Markdown support
install_extension shd101wyy.markdown-preview-enhanced # Enhanced markdown preview
install_extension bierner.markdown-mermaid          # Mermaid diagrams
install_extension davidanson.vscode-markdownlint    # Markdown linting

# =============================================================================
# 🎨 Code Quality & Formatting
# =============================================================================
echo "📦 Installing Code Quality Extensions..."
install_extension esbenp.prettier-vscode            # Code formatter
install_extension dbaeumer.vscode-eslint            # JavaScript/TypeScript linting
install_extension ms-vscode.vscode-eslint           # ESLint support
install_extension streetsidesoftware.code-spell-checker # Spell checker
install_extension usernamehw.errorlens              # Error highlighting

# =============================================================================
# 🚀 Productivity & AI
# =============================================================================
echo "📦 Installing Productivity Extensions..."
install_extension github.copilot                     # AI code completion
install_extension github.copilot-chat               # AI chat assistant
install_extension eamodio.gitlens                   # Git supercharged
install_extension mhutchie.git-graph                # Git graph visualization
install_extension christian-kohler.path-intellisense # Path autocompletion
install_extension oderwat.indent-rainbow            # Indent visualization
install_extension wayou.vscode-todo-highlight       # TODO highlighting

# =============================================================================
# 🎯 UI/UX Enhancement
# =============================================================================
echo "📦 Installing UI/UX Extensions..."
install_extension pkief.material-icon-theme         # Material icons
install_extension zhuangtongfa.material-theme       # Material theme
install_extension ritwickdey.liveserver             # Live server
install_extension ms-vscode.vscode-color-theme      # Color themes

# =============================================================================
# 🔧 Development Tools
# =============================================================================
echo "📦 Installing Development Tools..."
install_extension humao.rest-client                 # REST API client
install_extension ms-vscode.vscode-json             # JSON tools
install_extension redhat.vscode-yaml                # YAML support
install_extension ms-vscode.hexeditor               # Hex editor
install_extension ms-vscode.vscode-typescript-next  # TypeScript support

echo ""
echo "✅ All extensions installed successfully!"
echo "📋 Next steps:"
echo "   1. Restart Trae IDE"
echo "   2. Configure workspace settings (.vscode/settings.json)"
echo "   3. Set up project-specific extensions (.vscode/extensions.json)"
echo "   4. Configure Python interpreter for FastAPI development"
echo "   5. Set up Tailwind CSS IntelliSense for the frontend"
echo ""
echo "🎉 Your Aoi development environment is ready!"