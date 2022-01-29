"""
On-Chain Objects
"""
from typing import Optional

from .onchain_config import proxy_contract, w3


class TXReqs:
    """
    TX Sending Object
    """
    def __init__(self,
                 contract: str,
                 abi: list,
                 privatekey: Optional[bytes] = None,
                 passkey: Optional[str] = None):
        self.privatekey = privatekey
        self.passkey = passkey
        self.w3 = w3
        self.contract = w3.eth.contract(address=contract, abi=abi)


class ProxyTXReqs:
    """
    TX Sending Object
    """
    def __init__(self, target: str, privatekey: bytes, passkey: str):
        self.w3 = w3
        self.contract = proxy_contract
        self.target = target
        self.privatekey = privatekey
        self.passkey = passkey
