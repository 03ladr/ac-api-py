# Cryptography Modules
from Crypto.Cipher import AES

IV = bytes(16 * "\x00", "utf-8")
pad = lambda entry: bytes(
    (entry + (16 - len(entry) % 16) * chr(16 - len(entry) % 16)), 'utf-8')
unpad = lambda entry: entry[:-ord(entry[len(entry) - 1:])]


def aes_encrypt(to_encrypt: str, key: str):
    raw = pad(to_encrypt)
    encryptor = AES.new(pad(key), AES.MODE_CBC, IV=IV)
    return encryptor.encrypt(raw)


def aes_decrypt(to_decrypt: bytes, key: str):
    decryptor = AES.new(pad(key), AES.MODE_CBC, IV=IV)
    return unpad(decryptor.decrypt(to_decrypt))
