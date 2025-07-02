"""Type definitions for Arch SDK"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum

class NetworkMode(Enum):
    MAINNET = "mainnet"
    TESTNET = "testnet"
    REGTEST = "regtest"

@dataclass
class RPCConfig:
    """Configuration for RPC connection"""
    rpc_endpoint: str = "http://localhost:9002"
    network_mode: NetworkMode = NetworkMode.REGTEST
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    auth_token: Optional[str] = None
    headers: Optional[Dict[str, str]] = None

@dataclass
class AccountInfo:
    """Account information structure"""
    address: str
    balance: int
    utxos: List[Dict[str, Any]]
    transaction_count: int
    programs: List[str]

@dataclass
class TransactionInfo:
    """Transaction information structure"""
    txid: str
    block_hash: Optional[str]
    block_height: Optional[int]
    confirmations: int
    inputs: List[Dict[str, Any]]
    outputs: List[Dict[str, Any]]
    fee: int
    timestamp: Optional[int]
