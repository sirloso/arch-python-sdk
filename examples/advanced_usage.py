#!/usr/bin/env python3
"""
Advanced usage examples for Arch Python SDK
Demonstrates complex patterns, error handling, and real-world scenarios
"""

import asyncio
import sys
import os
import logging
from typing import List, Dict, Any

# Add src to Python path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from arch_sdk import ArchSDK, ArchRPCProvider, RPCConfig, NetworkMode, RPCError

# Configure logging for examples
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def custom_configuration_example():
    """Demonstrate advanced SDK configuration"""
    print("⚙️  Custom Configuration Example")
    print("-" * 40)
    
    # Create custom configuration
    config = RPCConfig(
        rpc_endpoint="http://localhost:9002",
        network_mode=NetworkMode.REGTEST,
        timeout=60,
        max_retries=5,
        retry_delay=2.0,
        headers={
            "User-Agent": "my-arch-app/1.0",
            "X-Client-Version": "advanced-example"
        }
    )
    
    sdk = ArchSDK(
        rpc_endpoint=config.rpc_endpoint,
        network_mode=config.network_mode.value,
        timeout=config.timeout,
        max_retries=config.max_retries,
        retry_delay=config.retry_delay,
        headers=config.headers
    )
    
    try:
        async with sdk:
            print(f"📡 Connected with custom config")
            print(f"🌐 Network: {config.network_mode.value}")
            print(f"⏱️  Timeout: {config.timeout}s")
            print(f"🔄 Max retries: {config.max_retries}")
            
            # Test the connection
            is_ready = await sdk.is_node_ready()
            print(f"✅ Node ready: {is_ready}")
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")


async def comprehensive_error_handling():
    """Demonstrate comprehensive error handling patterns"""
    print("\n🛡️  Comprehensive Error Handling")
    print("-" * 40)
    
    sdk = ArchSDK()
    
    async with sdk:
        # Test 1: Handle RPC errors gracefully
        print("🧪 Testing RPC error handling...")
        
        try:
            # Try to get info for a non-existent account
            fake_pubkey = [0] * 32  # All zeros - likely doesn't exist
            await sdk.read_account_info(fake_pubkey)
            
        except RPCError as e:
            print(f"✅ Caught RPC error: {e.code} - {e.message}")
            if e.data:
                print(f"   Additional data: {e.data}")
                
        except Exception as e:
            print(f"⚠️  Unexpected error: {e}")
        
        # Test 2: Handle connection issues
        print("\n🔌 Testing connection resilience...")
        
        try:
            # This should work with retries
            block_count = await sdk.get_block_count()
            print(f"✅ Block count retrieved: {block_count}")
            
        except Exception as e:
            print(f"❌ Connection failed even with retries: {e}")


async def batch_account_operations():
    """Demonstrate batch operations for multiple accounts"""
    print("\n👥 Batch Account Operations")
    print("-" * 40)
    
    sdk = ArchSDK()
    
    async with sdk:
        # Create multiple test pubkeys
        test_pubkeys = []
        for i in range(3):
            # Create different pubkeys for testing
            pubkey = [i+1] * 32  # [1,1,1...], [2,2,2...], [3,3,3...]
            test_pubkeys.append(pubkey)
        
        print(f"📋 Testing with {len(test_pubkeys)} accounts...")
        
        try:
            # Use get_multiple_accounts for batch operation
            accounts = await sdk.get_multiple_accounts(test_pubkeys)
            print(f"✅ Retrieved {len(accounts)} account records")
            
            for i, account in enumerate(accounts):
                print(f"   Account {i+1}: {type(account)}")
                
        except Exception as e:
            print(f"❌ Batch operation failed: {e}")
        
        # Alternative: Process accounts individually with better error handling
        print("\n🔄 Individual account processing...")
        
        for i, pubkey in enumerate(test_pubkeys):
            try:
                account_info = await sdk.read_account_info(pubkey)
                print(f"✅ Account {i+1}: Found data")
                
            except RPCError as e:
                if e.code == -32602:  # Invalid params or account not found
                    print(f"⚠️  Account {i+1}: Not found (expected)")
                else:
                    print(f"❌ Account {i+1}: Error {e.code}")
                    
            except Exception as e:
                print(f"❌ Account {i+1}: Unexpected error: {e}")


async def program_account_filtering():
    """Demonstrate advanced program account filtering"""
    print("\n🔍 Advanced Program Account Filtering")
    print("-" * 40)
    
    sdk = ArchSDK()
    
    async with sdk:
        # Example program ID (this would be a real program in practice)
        program_id = [80,82,242,228,43,246,248,133,88,238,139,124,88,96,107,32,
                      71,40,52,251,90,42,66,176,66,32,147,203,137,211,253,40]
        
        print("🔍 Testing different filter combinations...")
        
        # Test 1: Filter by data size only
        try:
            size_filter = [{"DataSize": 165}]
            accounts = await sdk.get_program_accounts(program_id, size_filter)
            print(f"✅ Size filter (165 bytes): {len(accounts)} accounts")
            
        except Exception as e:
            print(f"⚠️  Size filter failed: {e}")
        
        # Test 2: Filter by data content
        try:
            content_filter = [{"DataContent": {"offset": 0, "bytes": [1, 2, 3, 4]}}]
            accounts = await sdk.get_program_accounts(program_id, content_filter)
            print(f"✅ Content filter: {len(accounts)} accounts")
            
        except Exception as e:
            print(f"⚠️  Content filter failed: {e}")
        
        # Test 3: Combined filters
        try:
            combined_filters = [
                {"DataSize": 165},
                {"DataContent": {"offset": 0, "bytes": [1, 2, 3, 4]}}
            ]
            accounts = await sdk.get_program_accounts(program_id, combined_filters)
            print(f"✅ Combined filters: {len(accounts)} accounts")
            
        except Exception as e:
            print(f"⚠️  Combined filters failed: {e}")


async def block_monitoring_with_details():
    """Advanced block monitoring with detailed information"""
    print("\n📊 Advanced Block Monitoring")
    print("-" * 40)
    
    sdk = ArchSDK()
    
    async with sdk:
        try:
            # Get comprehensive block information
            block_count = await sdk.get_block_count()
            best_hash = await sdk.get_best_block_hash()
            
            print(f"📈 Current state:")
            print(f"   Block count: {block_count}")
            print(f"   Best block: {best_hash[:16]}...")
            
            if block_count > 0:
                # Get detailed block information
                latest_block = await sdk.get_block(best_hash)
                print(f"\n📦 Latest block details:")
                print(f"   Type: {type(latest_block)}")
                print(f"   Keys: {list(latest_block.keys()) if isinstance(latest_block, dict) else 'N/A'}")
                
                # Get block by height for comparison
                latest_by_height = await sdk.get_block_by_height(block_count - 1)
                print(f"\n📏 Same block by height:")
                print(f"   Retrieved successfully: {latest_by_height is not None}")
                
                # Show hash progression for last few blocks
                print(f"\n🔗 Recent block hashes:")
                for i in range(max(0, block_count - 3), block_count):
                    try:
                        block_hash = await sdk.get_block_hash(i)
                        print(f"   Block {i}: {block_hash[:16]}...")
                    except Exception as e:
                        print(f"   Block {i}: Error - {e}")
            
        except Exception as e:
            print(f"❌ Block monitoring error: {e}")


async def transaction_operations_demo():
    """Demonstrate transaction-related operations"""
    print("\n💳 Transaction Operations Demo")
    print("-" * 40)
    
    sdk = ArchSDK()
    
    async with sdk:
        # Note: We'll only demonstrate read operations to avoid modifying state
        
        print("🔍 Testing transaction queries...")
        
        # Test with a sample transaction ID (this would be real in practice)
        sample_txid = "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        
        try:
            transaction = await sdk.get_processed_transaction(sample_txid)
            print(f"✅ Transaction found: {transaction}")
            
        except RPCError as e:
            if "not found" in e.message.lower():
                print(f"⚠️  Transaction not found (expected for sample ID)")
            else:
                print(f"❌ Transaction query error: {e}")
                
        except Exception as e:
            print(f"❌ Unexpected transaction error: {e}")
        
        print("\n💡 Note: send_transaction and send_transactions require valid transaction data")
        print("   These methods are available but not demonstrated to avoid state changes")


async def network_operations_advanced():
    """Advanced network operations and monitoring"""
    print("\n🌐 Advanced Network Operations")
    print("-" * 40)
    
    sdk = ArchSDK()
    
    async with sdk:
        # Check node readiness with detailed info
        try:
            is_ready = await sdk.is_node_ready()
            print(f"✅ Node readiness: {is_ready}")
            
            # Get comprehensive blockchain state
            block_count = await sdk.get_block_count()
            best_hash = await sdk.get_best_block_hash()
            
            print(f"📊 Network state:")
            print(f"   Ready: {is_ready}")
            print(f"   Block height: {block_count}")
            print(f"   Tip hash: {best_hash[:16]}...")
            
        except Exception as e:
            print(f"❌ Network operations error: {e}")
        
        print("\n⚠️  Note: start_dkg and reset_network are administrative operations")
        print("   These modify network state and have specific restrictions")


async def real_world_application_pattern():
    """Demonstrate a real-world application pattern"""
    print("\n🌟 Real-World Application Pattern")
    print("-" * 40)
    
    class ArchNetworkMonitor:
        """Example application class using the SDK"""
        
        def __init__(self):
            self.sdk = ArchSDK(
                rpc_endpoint="http://localhost:9002",
                network_mode="regtest",
                timeout=30,
                max_retries=3
            )
            self.last_block_count = 0
        
        async def start(self):
            await self.sdk.rpc.connect()
            print("🚀 Monitor started")
        
        async def stop(self):
            await self.sdk.rpc.disconnect()
            print("🛑 Monitor stopped")
        
        async def check_for_new_blocks(self) -> bool:
            """Check if new blocks have been produced"""
            try:
                current_count = await self.sdk.get_block_count()
                
                if current_count > self.last_block_count:
                    print(f"📈 New block detected: {current_count}")
                    self.last_block_count = current_count
                    return True
                    
                return False
                
            except Exception as e:
                print(f"❌ Block check error: {e}")
                return False
        
        async def get_network_status(self) -> Dict[str, Any]:
            """Get comprehensive network status"""
            try:
                return {
                    "ready": await self.sdk.is_node_ready(),
                    "block_count": await self.sdk.get_block_count(),
                    "best_hash": await self.sdk.get_best_block_hash()
                }
            except Exception as e:
                print(f"❌ Status error: {e}")
                return {"error": str(e)}
    
    # Demonstrate the monitor
    monitor = ArchNetworkMonitor()
    
    try:
        await monitor.start()
        
        # Get initial status
        status = await monitor.get_network_status()
        print(f"📊 Initial status: {status}")
        
        # Check for new blocks
        has_new_blocks = await monitor.check_for_new_blocks()
        print(f"🔍 New blocks: {has_new_blocks}")
        
    finally:
        await monitor.stop()


async def main():
    """Run all advanced examples"""
    print("🚀 Arch Network Python SDK - Advanced Usage Examples")
    print("=" * 70)
    
    # Run all advanced examples
    await custom_configuration_example()
    await comprehensive_error_handling()
    await batch_account_operations()
    await program_account_filtering()
    await block_monitoring_with_details()
    await transaction_operations_demo()
    await network_operations_advanced()
    await real_world_application_pattern()
    
    print("\n" + "=" * 70)
    print("✅ All advanced examples completed!")
    print("\n🎯 Key takeaways:")
    print("1. Always use proper error handling with try/except blocks")
    print("2. Configure timeouts and retries for production use")
    print("3. Use batch operations when possible for efficiency")
    print("4. Structure your code with classes for complex applications")
    print("5. Monitor network state and handle disconnections gracefully")


if __name__ == "__main__":
    asyncio.run(main())
