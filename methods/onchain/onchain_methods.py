"""
On-Chain Methods/Functions
"""
# AES decryption module
from ..cryptography.aes_methods import aes_decrypt
# Transaction Sending Object
from .onchain_objects import TXReqs
# Exception Objects
from ..exceptions.exception_objects import PrivateKeyError
from eth_utils.exceptions import ValidationError
# SignedTransaction Object
from eth_account.datastructures import SignedTransaction


def buildtx(function, tx_reqs: TXReqs) -> SignedTransaction:
    """
    Send On-Chain Transaction
    """
    # Loading senders account
    privatekey = aes_decrypt(tx_reqs.privatekey, tx_reqs.passkey)
    try:
        sender = tx_reqs.w3.eth.account.privateKeyToAccount(
            privatekey.decode())
    except (ValidationError, ValueError):
        raise PrivateKeyError

    # Building tx
    txdeps = {
        'from': sender.address,
        'gasPrice': tx_reqs.w3.eth.gas_price,
        'nonce': tx_reqs.w3.eth.getTransactionCount(sender.address)
    }
    rawtx = function.buildTransaction(txdeps)

    # Signing and returning transaction object
    signed_tx = sender.signTransaction(rawtx)
    return signed_tx
