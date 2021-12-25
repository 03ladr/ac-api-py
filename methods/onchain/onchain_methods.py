"""
On-Chain Methods/Functions
"""
from ..cryptography.aes_methods import aes_decrypt
from .onchain_objects import TXReqs
from ..exceptions.exception_objects import PrivateKeyError
from eth_utils.exceptions import ValidationError

def sendtx(function, tx_reqs: TXReqs):
    """
    Send On-Chain Transaction
    """
    # Loading senders account
    privatekey = aes_decrypt(tx_reqs.privatekey, tx_reqs.passkey)
    try:
        sender = tx_reqs.w3.eth.account.privateKeyToAccount(privatekey.decode())
    except (ValidationError, ValueError):
        raise PrivateKeyError

    # Building tx
    txdeps = {
        'from': sender.address,
        'gasPrice': tx_reqs.w3.eth.gas_price,
        'nonce': tx_reqs.w3.eth.getTransactionCount(sender.address)
    }
    rawtx = function.buildTransaction(txdeps)

    # Signing then sending transaction
    signedtx = sender.signTransaction(rawtx)
    txoutput = tx_reqs.w3.eth.sendRawTransaction(signedtx.rawTransaction)

    # Returning tx hash
    return txoutput
