from ..cryptography.aes_methods import *
def sendtx(function, TXReqs):
    # Loading senders account
    privatekey = aes_decrypt(TXReqs.privatekey, TXReqs.passkey)
    sender = TXReqs.w3.eth.account.privateKeyToAccount(privatekey.decode())
    
    # Building tx
    txdeps = {'from': sender.address, 
            'gasPrice': TXReqs.w3.eth.gas_price, 
            'nonce': TXReqs.w3.eth.getTransactionCount(sender.address)
            }
    rawtx = function.buildTransaction(txdeps)
    
    # Signing then sending transaction
    signedtx = sender.signTransaction(rawtx)
    txoutput = TXReqs.w3.eth.sendRawTransaction(signedtx.rawTransaction)

    # Returning tx hash
    return txoutput
