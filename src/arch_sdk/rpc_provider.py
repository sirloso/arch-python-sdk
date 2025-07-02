"""
Arch Network RPC Provider - Complete Implementation
Based on: https://book.arch.network/rpc/http-methods.html
"""

import asyncio
import aiohttp
import json
import logging
from typing import Any, Dict, List, Optional, Union

from .types import RPCConfig, NetworkMode, AccountInfo, TransactionInfo
from .exceptions import RPCError

logger = logging.getLogger(__name__)

class ArchRPCProvider:
    """
    Complete Python RPC provider for Arch Network
    Implements all methods from the official documentation
    """
    
    def __init__(self, config: RPCConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self._request_id = 0
        
    async def __aenter__(self):
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
    
    async def connect(self) -> None:
        """Initialize the HTTP session"""
        if self.session is None:
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'arch-python-sdk/1.0.0'
            }
            
            if self.config.headers:
                headers.update(self.config.headers)
                
            if self.config.auth_token:
                headers['Authorization'] = f'Bearer {self.config.auth_token}'
            
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(headers=headers, timeout=timeout)
            logger.info(f"Connected to Arch RPC at {self.config.rpc_endpoint}")
    
    async def disconnect(self) -> None:
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Disconnected from Arch RPC")
    
    def _get_next_id(self) -> int:
        """Get next request ID"""
        self._request_id += 1
        return self._request_id
    
    async def _make_request(self, method: str, params: Any = None) -> Any:
        """Make a JSON-RPC request"""
        if not self.session:
            await self.connect()
        
        request_data = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": method,
            "params": params or []
        }
        
        for attempt in range(self.config.max_retries):
            try:
                logger.debug(f"Making RPC call: {method} (attempt {attempt + 1})")
                
                async with self.session.post(
                    self.config.rpc_endpoint,
                    json=request_data
                ) as response:
                    
                    if response.status != 200:
                        raise RPCError(
                            response.status,
                            f"HTTP Error: {response.status} {response.reason}"
                        )
                    
                    result = await response.json()
                    
                    if "error" in result:
                        error = result["error"]
                        raise RPCError(
                            error.get("code", -1),
                            error.get("message", "Unknown error"),
                            error.get("data")
                        )
                    
                    return result.get("result")
                    
            except aiohttp.ClientError as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt == self.config.max_retries - 1:
                    raise RPCError(-1, f"Connection failed: {e}")
                await asyncio.sleep(self.config.retry_delay * (attempt + 1))
            
            except json.JSONDecodeError as e:
                raise RPCError(-1, f"Invalid JSON response: {e}")

    # ===========================================
    # ACCOUNT OPERATIONS
    # ===========================================
    
    async def read_account_info(self, pubkey: List[int]) -> Dict[str, Any]:
        """
        Retrieves information for a specified account.
        
        Args:
            pubkey: Account public key as a 32-byte array
            
        Returns:
            Account information object with data, owner, utxo, is_executable, and tag fields
        """
        return await self._make_request("read_account_info", [pubkey])
    
    async def get_account_address(self, account_pubkey: List[int]) -> str:
        """
        Retrieves the Bitcoin address for a given account public key.
        
        Args:
            account_pubkey: Account public key as a 32-byte array
            
        Returns:
            Bitcoin address string (format depends on network mode)
        """
        return await self._make_request("get_account_address", [account_pubkey])
    
    async def get_program_accounts(self, 
                                   program_id: List[int], 
                                   filters: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Fetches all accounts owned by a specified program ID.
        
        Args:
            program_id: Program public key as a 32-byte array
            filters: Optional array of filter objects:
                - {"DataSize": <size>} - Filter by account data size
                - {"DataContent": {"offset": <offset>, "bytes": <byte_array>}} - Filter by data content
                
        Returns:
            Array of account objects with pubkey and account information
        """
        params = [program_id]
        if filters:
            params.append(filters)
        return await self._make_request("get_program_accounts", params)
    
    async def get_multiple_accounts(self, pubkeys: List[List[int]]) -> List[Dict[str, Any]]:
        """
        Retrieves information for multiple accounts in a single request.
        
        Args:
            pubkeys: Array of account public keys (32-byte arrays)
            
        Returns:
            Array of account information objects
        """
        return await self._make_request("get_multiple_accounts", [pubkeys])

    # ===========================================
    # TRANSACTION OPERATIONS
    # ===========================================
    
    async def send_transaction(self, transaction: Dict[str, Any]) -> str:
        """
        Submits a single transaction to the network.
        
        Args:
            transaction: RuntimeTransaction object containing:
                - version: Transaction version (currently 0)
                - signatures: Array of transaction signatures
                - message: Transaction message with signers and instructions
                
        Returns:
            Transaction ID (txid) string
        """
        return await self._make_request("send_transaction", [transaction])
    
    async def send_transactions(self, transactions: List[List[int]]) -> List[str]:
        """
        Submits multiple transactions to the network.
        
        Args:
            transactions: Array of serialized transactions (byte arrays)
            
        Returns:
            Array of transaction ID strings
        """
        return await self._make_request("send_transactions", [transactions])
    
    async def get_processed_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """
        Retrieves a processed transaction and its status.
        
        Args:
            transaction_id: Transaction ID string
            
        Returns:
            Object containing runtime_transaction, status, and bitcoin_txids
        """
        return await self._make_request("get_processed_transaction", [transaction_id])

    # ===========================================
    # BLOCK OPERATIONS
    # ===========================================
    
    async def get_block(self, 
                        block_hash: str, 
                        filter_option: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieves a block by its hash.
        
        Args:
            block_hash: Block hash string
            filter_option: Optional block transaction filter
            
        Returns:
            Block object with transaction data
        """
        params = [block_hash]
        if filter_option:
            params.append(filter_option)
        return await self._make_request("get_block", params)
    
    async def get_block_by_height(self, 
                                  block_height: int, 
                                  filter_option: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieves a block by its height.
        
        Args:
            block_height: Block height number
            filter_option: Optional block transaction filter
            
        Returns:
            Block object with transaction data
        """
        params = [block_height]
        if filter_option:
            params.append(filter_option)
        return await self._make_request("get_block_by_height", params)
    
    async def get_block_count(self) -> int:
        """
        Retrieves the current block count.
        
        Returns:
            Current block count as a number
        """
        return await self._make_request("get_block_count", [])
    
    async def get_block_hash(self, block_height: int) -> str:
        """
        Retrieves the block hash for a given height.
        
        Args:
            block_height: Block height number
            
        Returns:
            Block hash string
        """
        return await self._make_request("get_block_hash", [block_height])
    
    async def get_best_block_hash(self) -> str:
        """
        Retrieves the hash of the latest block.
        
        Returns:
            Latest block hash string
        """
        return await self._make_request("get_best_block_hash", [])

    # ===========================================
    # NETWORK OPERATIONS
    # ===========================================
    
    async def is_node_ready(self) -> bool:
        """
        Checks if the node is ready to process requests.
        
        Returns:
            Boolean indicating readiness
        """
        return await self._make_request("is_node_ready", [])
    
    async def start_dkg(self) -> Dict[str, Any]:
        """
        Initiates the Distributed Key Generation process.
        
        Restrictions:
        - DKG must not have already occurred
        - Node must be in WaitingForDkg state
        
        Returns:
            Success message or error
        """
        return await self._make_request("start_dkg", [])
    
    async def reset_network(self) -> Dict[str, Any]:
        """
        Resets the network state (leader nodes only).
        
        Restrictions:
        - Only network leader can initiate
        - Specific validator states required
        - 20-second timeout for operations
        
        Returns:
            Success message or error
        """
        return await self._make_request("reset_network", [])

    # ===========================================
    # CONVENIENCE METHODS (Higher-level wrappers)
    # ===========================================
    
    async def get_account_info_by_address(self, address: str) -> AccountInfo:
        """
        Convenience method to get account info using address string instead of pubkey array.
        Note: This requires conversion from address to pubkey which may need additional logic.
        """
        # This would need address-to-pubkey conversion logic
        # For now, raising NotImplementedError to indicate this needs address conversion
        raise NotImplementedError(
            "Address to pubkey conversion not implemented. Use read_account_info with pubkey array instead."
        )
    
    async def get_balance(self, pubkey: List[int]) -> int:
        """
        Get account balance from account info.
        
        Args:
            pubkey: Account public key as 32-byte array
            
        Returns:
            Account balance
        """
        account_info = await self.read_account_info(pubkey)
        # Extract balance from account data - this depends on account structure
        # May need to parse the account data based on Arch Network's account format
        return account_info.get("balance", 0)
    
    async def get_utxos(self, pubkey: List[int]) -> List[Dict[str, Any]]:
        """
        Get UTXOs from account info.
        
        Args:
            pubkey: Account public key as 32-byte array
            
        Returns:
            List of UTXOs
        """
        account_info = await self.read_account_info(pubkey)
        return account_info.get("utxo", [])

    # ===========================================
    # UTILITY METHODS
    # ===========================================
    
    @staticmethod
    def pubkey_from_hex(hex_string: str) -> List[int]:
        """
        Convert hex string to 32-byte array for pubkey.
        
        Args:
            hex_string: Hex string representation of pubkey
            
        Returns:
            32-byte array
        """
        # Remove '0x' prefix if present
        if hex_string.startswith('0x'):
            hex_string = hex_string[2:]
        
        # Ensure it's 64 characters (32 bytes)
        if len(hex_string) != 64:
            raise ValueError("Pubkey hex string must be 64 characters (32 bytes)")
        
        # Convert to byte array
        return [int(hex_string[i:i+2], 16) for i in range(0, 64, 2)]
    
    @staticmethod
    def pubkey_to_hex(pubkey: List[int]) -> str:
        """
        Convert 32-byte array to hex string.
        
        Args:
            pubkey: 32-byte array
            
        Returns:
            Hex string representation
        """
        if len(pubkey) != 32:
            raise ValueError("Pubkey must be 32 bytes")
        
        return ''.join(f'{byte:02x}' for byte in pubkey)


class ArchSDK:
    """
    Main SDK class that wraps the RPC provider
    """
    
    def __init__(self, 
                 rpc_endpoint: str = "http://localhost:9002",
                 network_mode: str = "regtest",
                 **kwargs):
        
        config = RPCConfig(
            rpc_endpoint=rpc_endpoint,
            network_mode=NetworkMode(network_mode),
            **kwargs
        )
        
        self.rpc = ArchRPCProvider(config)
        self.config = config
    
    async def __aenter__(self):
        await self.rpc.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.rpc.disconnect()
    
    # Delegate all RPC methods to the provider
    def __getattr__(self, name):
        """Delegate method calls to the RPC provider"""
        if hasattr(self.rpc, name):
            return getattr(self.rpc, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
