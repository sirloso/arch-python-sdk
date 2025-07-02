"""Custom exceptions for Arch SDK"""

class RPCError(Exception):
    """Custom exception for RPC errors"""
    def __init__(self, code: int, message: str, data=None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(f"RPC Error {code}: {message}")
