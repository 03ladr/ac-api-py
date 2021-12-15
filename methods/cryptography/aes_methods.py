# Cryptography Modules
from Crypto.Cipher import AES


IV = bytes(16 * "\x00", "utf-8")


def aes_encrypt(to_encrypt: str, key: str):
    key = bytes(key, "utf-8")
    to_encrypt = bytes(to_encrypt, "utf-8")
    encryptor = AES.new(key, AES.MODE_CFB, IV=IV)
    return encryptor.encrypt(to_encrypt).hex()


def aes_decrypt(to_decrypt: str, key: str):
    key = bytes(key, "utf-8")
    to_decrypt = bytes(to_decrypt, "utf-8")
    decryptor = AES.new(key, AES.MODE_CFB, IV=IV)
    return decryptor.decrypt(to_decrypt)
