# ABI variable
from .abi import abi

CONTRACT_ADDRESS = "0xea88Ab6925D6634c57EEd18138E5268F357225E4"

# Minting product NFT with provided metadata
def mint_nft(w3, tokenURI: str, sender):
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
    try:
        tokenid = contract.functions.createItemToken(tokenURI).transact({"from":sender})
    except:
        return None
    
    # Returning Keccak tokenid
    return tokenid.hex()
