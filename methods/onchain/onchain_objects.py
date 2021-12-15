# On-Chain Connectivity/Tooling
from .onchain_config import w3, contract
# Cryptography Modules
from ..cryptography.aes_methods import aes_decrypt
# Typing
from pydantic import BaseModel

class TXReqs: #TX send object
    def __init__(self, publickey, privatekey, passkey, w3=w3, contract=contract):
        self.publickey: str = publickey
        self.privatekey: str = privatekey
        self.passkey: str = passkey
        self.w3 = w3
        self.contract = contract
    def decrypt_privatekey():
        return aes_decrypt(self.privatekey, self.passkey)
