# Querying owner of NFT via Token ID
def nft_owner(contract, tokenid: int, sender):
    try:
        owner = contract.functions.ownedBy(tokenid).call({"from":sender})
    except:
        return None

    # Returns owner Keccak hash
    return owner.hex()

