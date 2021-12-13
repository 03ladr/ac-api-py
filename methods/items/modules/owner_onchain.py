# ABI variable
from .abi import abi

# Querying owner of NFT via Token ID
def nft_owner(w3, contract, tokenid, sender):
    contract = w3.eth.contract(address=contract, abi=abi)
    try:
        owner = contract.functions.ownedBy(tokenid).call({"from":sender})
    except:
        return None

    # Returns owner Keccak hash
    return owner.hex()

