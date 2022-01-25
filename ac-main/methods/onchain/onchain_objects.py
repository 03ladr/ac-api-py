"""
On-Chain Objects
"""
from typing import Optional

from .onchain_config import w3


class TXReqs:
    """
    TX Sending Object
    """
    def __init__(self,
                 contract: str,
                 abi: list,
                 privatekey: Optional[bytes] = None,
                 passkey: Optional[bytes] = None):
        self.privatekey: bytes = privatekey
        self.passkey: str = passkey
        self.w3 = w3
        self.contract = w3.eth.contract(address=contract, abi=abi)
