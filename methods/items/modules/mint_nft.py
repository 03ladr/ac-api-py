# Minting product NFT with provided metadata
def mint_nft(contract, tokenURI: str, sender):
    try:
        contract.functions.mintItemToken(tokenURI).transact({"from":sender})
    except:
        return False
    
    # Returns True indicating successful creation
    return True
