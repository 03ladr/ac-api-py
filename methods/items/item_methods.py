# Utilities
import json
from urllib.request import urlopen
# Database tooling
from sqlalchemy.orm import Session
# Local modules
from . import item_objects
from ..database import db_schemas
from ..users.user_methods import get_user_publickey
from ..onchain.onchain_methods import sendtx


# Item creation
def create_item(ipfs, item_obj: item_objects.ItemCreate, TXReqs) -> bool:
    # Generates NFT metadata URL (hosted on IPFS)
    metadataURI = create_metadata(ipfs, item_obj)
    # Mints Item NFT via smart contract
    minted = sendtx(TXReqs.contract.functions.mintItemToken(metadataURI),
                    TXReqs)
    # Returns False if Item creation failed
    if not minted:
        return False
    # Returns True indicating successful creation
    return True


# Create and host item token metadata
def create_metadata(ipfs, item_obj: item_objects.ItemCreate) -> str:
    item_json = json.loads(item_obj.json())
    ipfs_metadata = ipfs.add_json(item_json)
    return "http://127.0.0.1:8080/ipfs/{cid}".format(cid=ipfs_metadata)


# Transfer item token
def transfer_item(TXReqs, itemid: int, receiver: str) -> Bool:
    # Transfers item NFT via smart contract
    transferred = sendtx(
        TXReqs.contract.functions.transferItemToken(
            itemid, get_user_publickey(receiver)), TXReqs)
    # Returns False if Item transfer failed
    if not transferred:
        return False
    # Returns True indicating successful transfer
    return True


# Get item by ID
def get_item(db: Session, TXReqs, itemid: int):
    # Verifies items existence in-db
    itemid = db.query(
        db_schemas.Item).filter(db_schemas.Item.id == itemid).first().id
    # Returns JSON Metadata Object
    return get_metadata(TXReqs, itemid)


# Get item token metadata
def get_metadata(TXReqs, itemid):
    # Fetches metadata URI -> loads as JSON
    rawuri = TXReqs.contract.functions.tokenURI(itemid).call()
    uri = urlopen(rawuri)
    metadata = json.load(uri)
    metadata['id'] = itemid
    return metadata


# Get items owned by a user
def get_user_items(TXReqs, address: str) -> List:
    owned_ids = TXReqs.contract.functions.ownedItemTokens(address).call()
    owned_items = [get_metadata(TXReqs, id) for id in owned_ids]
    return owned_items


# Set claimability status of item
def set_item_claimability(TXReqs, itemid: int) -> bool:
    item_claimability = sendtx(TXReqs.contract.functions.setItemClaimability(itemid), TXReqs)
    return item_claimability
    

# Get claimability status of item
def get_item_claimability(TXReqs, itemid: int) -> bool:
    item_claimability = TXReqs.contract.functions.viewItemClaimability(itemid).call()
    return item_claimability


# Get transfer count of item
def get_item_transfercount(db, itemid: int) -> None:
    return None # Not Implemented
