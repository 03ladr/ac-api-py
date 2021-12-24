"""
On-Chain Objects
"""
# Typing
from typing import Optional
# On-Chain Connectivity/Tooling
from .onchain_config import w3, contract


class TXReqs:
    """
    TX Sending Object
    """
    def __init__(self,
                 privatekey: Optional[bytes] = None,
                 passkey: Optional[bytes] = None):
        self.privatekey: bytes = privatekey
        self.passkey: str = passkey
        self.w3 = w3
        self.contract = contract
