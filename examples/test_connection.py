#!/usr/bin/env python3
"""
Test connection to Arch Network
"""

import asyncio
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from arch_sdk import ArchSDK

async def test_connection():
    """Test basic connection to Arch Network"""
    print("🔌 Testing connection to Arch Network...")
    
    sdk = ArchSDK(
        rpc_endpoint="http://localhost:9002",
        network_mode="regtest"
    )
    
    try:
        async with sdk:
            print("✅ Connected to Arch Network!")
            
            # Test health check
            try:
                health = await sdk.rpc.get_block_count()
                print(f"💚 Node health: {health}")
            except Exception as e:
                print(f"⚠️  Health check failed: {e}")
            
            print("🎉 Connection test completed!")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Make sure you have:")
        print("1. Bitcoin Core running in regtest mode")
        print("2. Electrs running and connected")
        print("3. Arch validator running on localhost:9002")

if __name__ == "__main__":
    asyncio.run(test_connection())
