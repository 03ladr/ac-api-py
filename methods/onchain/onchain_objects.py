# Typing
from pydantic import BaseModel
from typing import Optional
# On-Chain Connectivity/Tooling
from .onchain_config import w3, contract

class TXReqs: #TX send object
    def __init__(self, privatekey: Optional[bytes] = None, passkey: Optional[bytes] = None, w3=w3, contract=contract):
        self.privatekey: bytes = privatekey
        self.passkey: str = passkey
        self.w3 = w3
        self.contract = contract
