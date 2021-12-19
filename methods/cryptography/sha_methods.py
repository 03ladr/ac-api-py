# Cryptography Modules
from Crypto.Hash import SHAKE256

def create_hash(to_hash: str):
    shake = SHAKE256.new()
    shake.update(bytes(to_hash, "utf-8"))
    return bytes(shake.read(32).hex(), 'utf-8')  # 32 Bit SHA3-256 hash

def verify_hash(plaintext: str, hashed: bytes):
    to_check = create_hash(plaintext)
    verified = to_check == hashed
    return verified  # True or False
