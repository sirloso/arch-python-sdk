#!/usr/bin/env python3
"""
Basic usage examples for Arch Python SDK
Simple examples to get started with the Arch Network RPC provider
"""

import asyncio
import sys
import os

# Add src to Python path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from arch_sdk import ArchSDK, ArchRPCProvider

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
            
            # Test node readiness
            try:
                is_ready = await sdk.is_node_ready()
                print(f"💚 Node ready: {is_ready}")
            except Exception as e:
                print(f"⚠️  Node readiness check failed: {e}")
            
            print("🎉 Connection test completed!")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Make sure you have:")
        print("1. Arch validator running on localhost:9002")
        print("2. Node is properly configured and synced")


async def get_basic_info():
    """Get basic blockchain information"""
    print("\n📊 Getting basic blockchain information...")
    
    sdk = ArchSDK()
    
    try:
        async with sdk:
            # Get current block count
            block_count = await sdk.get_block_count()
            print(f"📈 Current block count: {block_count}")
            
            # Get best block hash
            best_hash = await sdk.get_best_block_hash()
            print(f"🎯 Best block hash: {best_hash}")
            
            # Get block hash for a specific height
            if block_count > 0:
                genesis_hash = await sdk.get_block_hash(0)
                print(f"🏗️  Genesis block hash: {genesis_hash}")
            
    except Exception as e:
        print(f"❌ Error getting blockchain info: {e}")


async def work_with_accounts():
    """Basic account operations"""
    print("\n👤 Working with accounts...")
    
    sdk = ArchSDK()
    
    try:
        async with sdk:
            # Example pubkey (32 bytes)
            example_hex = "0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20"
            pubkey = ArchRPCProvider.pubkey_from_hex(example_hex)
            
            print(f"🔑 Using pubkey: {example_hex}")
            
            try:
                # Get account address
                address = await sdk.get_account_address(pubkey)
                print(f"🏠 Account address: {address}")
            except Exception as e:
                print(f"⚠️  Account address error: {e}")
            
            try:
                # Get account info
                account_info = await sdk.read_account_info(pubkey)
                print(f"📋 Account info: {account_info}")
            except Exception as e:
                print(f"⚠️  Account info error: {e}")
                
    except Exception as e:
        print(f"❌ Error with account operations: {e}")


async def utility_examples():
    """Demonstrate utility functions"""
    print("\n🔧 Utility function examples...")
    
    try:
        # Convert hex to pubkey array
        hex_pubkey = "1234567890abcdef" * 8  # 64 characters = 32 bytes
        pubkey_array = ArchRPCProvider.pubkey_from_hex(hex_pubkey)
        
        print(f"📝 Original hex: {hex_pubkey}")
        print(f"🔢 As byte array: [{pubkey_array[0]}, {pubkey_array[1]}, ..., {pubkey_array[-1]}] (32 bytes)")
        
        # Convert back to hex
        hex_result = ArchRPCProvider.pubkey_to_hex(pubkey_array)
        print(f"🔄 Back to hex: {hex_result}")
        
        # Verify round-trip
        assert hex_pubkey == hex_result
        print("✅ Round-trip conversion successful!")
        
    except Exception as e:
        print(f"❌ Utility function error: {e}")


async def simple_block_query():
    """Simple block querying example"""
    print("\n🧱 Simple block querying...")
    
    sdk = ArchSDK()
    
    try:
        async with sdk:
            # Get current state
            block_count = await sdk.get_block_count()
            
            if block_count > 0:
                print(f"📊 Total blocks: {block_count}")
                
                # Get the latest block
                best_hash = await sdk.get_best_block_hash()
                latest_block = await sdk.get_block(best_hash)
                
                print(f"📦 Latest block hash: {best_hash[:16]}...")
                print(f"🔍 Block data type: {type(latest_block)}")
                
                # Get genesis block
                genesis_block = await sdk.get_block_by_height(0)
                print(f"🏗️  Genesis block retrieved: {type(genesis_block)}")
                
            else:
                print("⚠️  No blocks available yet")
                
    except Exception as e:
        print(f"❌ Block query error: {e}")


async def main():
    """Run all basic examples"""
    print("🚀 Arch Network Python SDK - Basic Usage Examples")
    print("=" * 60)
    
    # Run all basic examples
    await test_connection()
    await get_basic_info()
    await work_with_accounts()
    await utility_examples()
    await simple_block_query()
    
    print("\n" + "=" * 60)
    print("✅ All basic examples completed!")
    print("\n💡 Next steps:")
    print("1. Try the advanced_usage.py examples")
    print("2. Run comprehensive_test.py for full method testing")
    print("3. Build your own application using these patterns")


if __name__ == "__main__":
    asyncio.run(main())
