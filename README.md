# Arch Network Python SDK

A comprehensive Python implementation of the Arch Network RPC provider, fully compatible with the official [Arch Network RPC API](https://book.arch.network/rpc/http-methods.html).

## 🚀 Features

- ✅ **Complete RPC Method Coverage** - All 15 official RPC methods implemented
- ✅ **Async/Await Support** - Built with `aiohttp` for high performance
- ✅ **Type Safety** - Full type hints and dataclasses
- ✅ **Error Handling** - Comprehensive error handling with retries
- ✅ **Connection Management** - Automatic connection pooling and cleanup
- ✅ **Multiple Networks** - Support for mainnet, testnet, and regtest
- ✅ **Utility Functions** - Helper methods for pubkey conversion
- ✅ **Comprehensive Examples** - Real-world usage patterns included

## 📋 Supported RPC Methods

### Account Operations
| Method | Description |
|--------|-------------|
| `read_account_info(pubkey)` | Get account information |
| `get_account_address(pubkey)` | Get Bitcoin address for account |
| `get_program_accounts(program_id, filters)` | Get accounts owned by program |
| `get_multiple_accounts(pubkeys)` | Bulk account information |

### Transaction Operations
| Method | Description |
|--------|-------------|
| `send_transaction(transaction)` | Submit single transaction |
| `send_transactions(transactions)` | Submit multiple transactions |
| `get_processed_transaction(txid)` | Get transaction status |

### Block Operations
| Method | Description |
|--------|-------------|
| `get_block(block_hash, filter)` | Get block by hash |
| `get_block_by_height(height, filter)` | Get block by height |
| `get_block_count()` | Get current block count |
| `get_block_hash(height)` | Get block hash by height |
| `get_best_block_hash()` | Get latest block hash |

### Network Operations
| Method | Description |
|--------|-------------|
| `is_node_ready()` | Check node readiness |
| `start_dkg()` | Initiate Distributed Key Generation |
| `reset_network()` | Reset network state (leader only) |

## 🛠️ Installation

### Quick Setup

```bash
# Create project directory
mkdir arch-python-sdk && cd arch-python-sdk

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create requirements.txt
cat > requirements.txt << 'EOF'
aiohttp>=3.8.0
typing-extensions>=4.0.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
black>=22.0.0
EOF

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create project structure
mkdir -p src/arch_sdk examples tests
```

### Project Structure

```
arch-python-sdk/
├── src/
│   └── arch_sdk/
│       ├── __init__.py          # Package exports
│       ├── rpc_provider.py      # Main RPC implementation
│       ├── types.py             # Type definitions
│       └── exceptions.py        # Custom exceptions
├── examples/
│   ├── basic_usage.py          # Basic examples
│   ├── advanced_usage.py       # Advanced patterns
│   └── comprehensive_test.py   # All method testing
├── tests/                      # Test suite
├── requirements.txt            # Dependencies
└── README.md                  # This file
```

## 🚀 Quick Start

### Basic Usage

```python
import asyncio
from arch_sdk import ArchSDK

async def main():
    # Initialize SDK
    sdk = ArchSDK(
        rpc_endpoint="http://localhost:9002",
        network_mode="regtest"
    )
    
    async with sdk:
        # Check node status
        is_ready = await sdk.is_node_ready()
        print(f"Node ready: {is_ready}")
        
        # Get current block information
        block_count = await sdk.get_block_count()
        best_hash = await sdk.get_best_block_hash()
        
        print(f"Block count: {block_count}")
        print(f"Best block: {best_hash}")

asyncio.run(main())
```

### Working with Accounts

```python
import asyncio
from arch_sdk import ArchSDK, ArchRPCProvider

async def account_example():
    sdk = ArchSDK()
    
    async with sdk:
        # Convert hex pubkey to required byte array format
        hex_pubkey = "0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20"
        pubkey = ArchRPCProvider.pubkey_from_hex(hex_pubkey)
        
        try:
            # Get account information
            account_info = await sdk.read_account_info(pubkey)
            print(f"Account data: {account_info}")
            
            # Get Bitcoin address for this account
            address = await sdk.get_account_address(pubkey)
            print(f"Bitcoin address: {address}")
            
        except Exception as e:
            print(f"Account not found: {e}")

asyncio.run(account_example())
```

### Program Account Queries

```python
async def program_example():
    sdk = ArchSDK()
    
    async with sdk:
        # Example program ID (32-byte array)
        program_id = [80,82,242,228,43,246,248,133,88,238,139,124,88,96,107,32,
                      71,40,52,251,90,42,66,176,66,32,147,203,137,211,253,40]
        
        # Filter accounts by size and content
        filters = [
            {"DataSize": 165},
            {"DataContent": {"offset": 0, "bytes": [1, 2, 3, 4]}}
        ]
        
        accounts = await sdk.get_program_accounts(program_id, filters)
        print(f"Found {len(accounts)} program accounts")

asyncio.run(program_example())
```

### Block Monitoring

```python
async def block_monitor():
    sdk = ArchSDK()
    
    async with sdk:
        print("Starting block monitor...")
        
        while True:
            try:
                current_count = await sdk.get_block_count()
                best_hash = await sdk.get_best_block_hash()
                
                print(f"Block {current_count}: {best_hash[:16]}...")
                
                # Get block details
                block = await sdk.get_block(best_hash)
                print(f"Block contains {len(block.get('transactions', []))} transactions")
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except KeyboardInterrupt:
                print("Monitor stopped")
                break
            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(1)

asyncio.run(block_monitor())
```

## ⚙️ Configuration

### Advanced Configuration

```python
from arch_sdk import ArchSDK, RPCConfig, NetworkMode

# Custom configuration
config = RPCConfig(
    rpc_endpoint="http://localhost:9002",
    network_mode=NetworkMode.REGTEST,
    timeout=60,
    max_retries=5,
    retry_delay=2.0,
    headers={"Authorization": "Bearer your-token"}
)

sdk = ArchSDK(
    rpc_endpoint=config.rpc_endpoint,
    network_mode=config.network_mode.value,
    timeout=config.timeout,
    max_retries=config.max_retries,
    retry_delay=config.retry_delay,
    headers=config.headers
)
```

### Network Modes

```python
# Local development (default)
sdk = ArchSDK(network_mode="regtest")

# Testnet
sdk = ArchSDK(
    rpc_endpoint="http://testnet-node:9002",
    network_mode="testnet"
)

# Mainnet
sdk = ArchSDK(
    rpc_endpoint="http://mainnet-node:9002", 
    network_mode="mainnet"
)
```

## 🧪 Running Examples

```bash
# Test connection
python examples/basic_usage.py

# Run comprehensive method testing
python examples/comprehensive_test.py

# Advanced usage patterns
python examples/advanced_usage.py
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/arch_sdk

# Run specific test
pytest tests/test_rpc_provider.py -v
```

## 🔧 Development

### Code Formatting

```bash
# Format code
black src/ tests/ examples/

# Type checking
mypy src/

# Linting
flake8 src/ tests/ examples/
```

### Installing in Development Mode

```bash
pip install -e .
```



## 🔍 Troubleshooting

### Common Issues

#### Connection Refused
```bash
# Check if services are running
ps aux | grep bitcoind
ps aux | grep electrs
ps aux | grep arch

# Check ports
netstat -tlnp | grep -E "(18443|3002|9002)"
```

#### RPC Method Not Found
```python
# Ensure you're using the correct method names
await sdk.is_node_ready()  # ✅ Correct
await sdk.get_health()     # ❌ Wrong - method doesn't exist
```

#### Pubkey Format Issues
```python
# Convert hex strings to byte arrays
hex_pubkey = "0102...1f20"  # 64 character hex string
pubkey = ArchRPCProvider.pubkey_from_hex(hex_pubkey)  # [1,2,...,31,32]
```

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

sdk = ArchSDK(rpc_endpoint="http://localhost:9002")
# Will show detailed request/response logs
```

## 📚 API Reference

### Error Handling

```python
from arch_sdk import RPCError

try:
    result = await sdk.read_account_info(pubkey)
except RPCError as e:
    print(f"RPC Error {e.code}: {e.message}")
    if e.data:
        print(f"Additional info: {e.data}")
```

### Type Definitions

```python
from arch_sdk import AccountInfo, TransactionInfo, NetworkMode

# All types are available for import
network = NetworkMode.REGTEST
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Links

- [Arch Network Documentation](https://book.arch.network/)
- [Official RPC Methods](https://book.arch.network/rpc/http-methods.html)
- [Arch Network GitHub](https://github.com/Arch-Network)
- [TypeScript SDK](https://github.com/SaturnBTC/arch-typescript-sdk)
