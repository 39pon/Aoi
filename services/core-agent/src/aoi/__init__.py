# =============================================================================
# Aoi AI Agent Ecosystem - Core Agent
# =============================================================================
"""
Aoi Core Agent - Intelligent AI Agent with Memory and Tool Integration

This module provides the core functionality for the Aoi AI agent ecosystem,
including agent orchestration, memory management, and tool integration.
"""

__version__ = "0.1.0"
__author__ = "Aoi Development Team"
__email__ = "dev@aoi-ai.com"

from .core.agent import AoiAgent
from .core.config import AoiConfig
from .memory.manager import MemoryManager
from .tools.registry import ToolRegistry

__all__ = [
    "AoiAgent",
    "AoiConfig", 
    "MemoryManager",
    "ToolRegistry",
]