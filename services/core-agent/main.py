#!/usr/bin/env python3
# =============================================================================
# Aoi Core Agent - Main Entry Point
# =============================================================================

import asyncio
import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

import uvicorn
from loguru import logger
from aoi.core.config import AoiConfig
from aoi.api.server import app

def setup_logging(config: AoiConfig) -> None:
    """
    Setup logging configuration.
    
    Args:
        config: Configuration object.
    """
    # Remove default logger
    logger.remove()
    
    # Add console logger
    logger.add(
        sys.stderr,
        level=config.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # Add file logger if specified
    if config.log_file:
        logger.add(
            config.log_file,
            level=config.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention="7 days",
            compression="gz"
        )

def validate_environment(config: AoiConfig) -> bool:
    """
    Validate the environment and configuration.
    
    Args:
        config: Configuration object.
    
    Returns:
        bool: True if environment is valid.
    """
    logger.info("Validating environment...")
    
    # Check required API keys
    missing_keys = config.get_missing_keys()
    if missing_keys:
        logger.warning(f"Missing API keys: {missing_keys}")
        logger.warning("Some features may not be available.")
    
    # Check database connections
    logger.info(f"Redis URL: {config.redis_url}")
    logger.info(f"Weaviate URL: {config.weaviate_url}")
    
    # Check Obsidian vault path
    vault_path = Path(config.obsidian_vault_path)
    if not vault_path.exists():
        logger.warning(f"Obsidian vault path does not exist: {vault_path}")
        logger.info("Creating Obsidian vault directory...")
        vault_path.mkdir(parents=True, exist_ok=True)
    
    logger.success("Environment validation completed")
    return True

def main() -> None:
    """
    Main entry point for the Aoi Core Agent.
    """
    # Load configuration
    config = AoiConfig()
    
    # Setup logging
    setup_logging(config)
    
    logger.info("="*60)
    logger.info("🤖 Aoi Core Agent Starting...")
    logger.info("="*60)
    
    # Validate environment
    if not validate_environment(config):
        logger.error("Environment validation failed")
        sys.exit(1)
    
    # Display configuration
    logger.info(f"Agent Name: {config.agent_name}")
    logger.info(f"Agent Version: {config.agent_version}")
    logger.info(f"Debug Mode: {config.debug_mode}")
    logger.info(f"API Host: {config.api_host}")
    logger.info(f"API Port: {config.api_port}")
    logger.info(f"Log Level: {config.log_level}")
    
    try:
        # Start the FastAPI server
        logger.info("Starting FastAPI server...")
        
        uvicorn.run(
            app,
            host=config.api_host,
            port=config.api_port,
            workers=config.api_workers,
            log_level=config.log_level.lower(),
            reload=config.debug_mode,
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
    finally:
        logger.info("🤖 Aoi Core Agent Shutdown")
        logger.info("="*60)

if __name__ == "__main__":
    main()