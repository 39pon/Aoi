#!/usr/bin/env python3
# =============================================================================
# DeepL MCP Server Integration Test
# =============================================================================

import asyncio
import sys
import os
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import after path setup
try:
    from aoi.mcp.integration import MCPIntegration
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the correct directory")
    sys.exit(1)


async def test_deepl_integration():
    """
    Test DeepL MCP Server integration.
    """
    print("🚀 Testing DeepL MCP Server Integration...")
    
    # Initialize MCP integration
    mcp = MCPIntegration()
    
    try:
        # Initialize the integration
        success = await mcp.initialize()
        if not success:
            print("❌ Failed to initialize MCP integration")
            return False
        
        print("✅ MCP integration initialized successfully")
        
        # Test DeepL translation
        print("\n📝 Testing DeepL translation...")
        
        # Test Japanese to English translation
        result = await mcp.execute_tool(
            server_name="deepl",
            tool_name="translate",
            args={
                "text": "こんにちは、世界！",
                "target_lang": "EN",
                "source_lang": "JA"
            }
        )
        
        print(f"Translation result: {result}")
        
        # Test language detection
        print("\n🔍 Testing language detection...")
        
        detect_result = await mcp.execute_tool(
            server_name="deepl",
            tool_name="detect_language",
            args={
                "text": "Hello, world!"
            }
        )
        
        print(f"Language detection result: {detect_result}")
        
        # Test supported languages
        print("\n🌐 Testing supported languages...")
        
        languages_result = await mcp.execute_tool(
            server_name="deepl",
            tool_name="get_languages",
            args={}
        )
        
        print(f"Supported languages: {languages_result}")
        
        # Test using client methods
        print("\n🔧 Testing MCP client methods...")
        
        if mcp.client:
            # Test translate method
            translate_response = await mcp.client.deepl_translate(
                text="Thank you for using Aoi!",
                target_lang="JA",
                source_lang="EN"
            )
            
            print(f"Client translate response: {translate_response}")
            
            # Test detect language method
            detect_response = await mcp.client.deepl_detect_language(
                text="Bonjour le monde!"
            )
            
            print(f"Client detect response: {detect_response}")
            
            # Test get languages method
            languages_response = await mcp.client.deepl_get_languages()
            
            print(f"Client languages response: {languages_response}")
        
        print("\n✅ All DeepL integration tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        if mcp.is_initialized:
            await mcp.shutdown()
            print("🧹 MCP integration shutdown completed")


if __name__ == "__main__":
    print("🔧 DeepL MCP Server Integration Test")
    print("=" * 50)
    
    # Check environment variables
    deepl_key = os.getenv("DEEPL_API_KEY")
    if deepl_key and deepl_key != "your-deepl-api-key-here":
        print(f"🔑 DeepL API Key found: {deepl_key[:10]}...")
    else:
        print("⚠️  DeepL API Key not set - using mock responses")
    
    # Run the test
    success = asyncio.run(test_deepl_integration())
    
    if success:
        print("\n🎉 DeepL integration test PASSED!")
        sys.exit(0)
    else:
        print("\n💥 DeepL integration test FAILED!")
        sys.exit(1)