# Utilities
import json
from urllib.request import urlopen
# Database tooling
from sqlalchemy.orm import Session
from sqlalchemy import or_
# Local modules
from . import item_objects
from ..database import db_schemas
from ..users.user_objects import User
from ..onchain.onchain_methods import sendtx

# Item creation
def create_item(ipfs, item_obj: item_objects.ItemCreate, TXReqs):
    # Generates NFT metadata URL (hosted on IPFS)
    metadataURI = create_metadata(ipfs, item_obj)
    # Mints Item NFT via smart contract
    minted = sendtx(TXReqs.contract.functions.mintItemToken(metadataURI), TXReqs)
    # Returns False if Item creation failed
    if not minted:
        return False
    # Returns True indicating successful creation
    return True

# Create and host item token metadata
def create_metadata(item_obj: item_objects.ItemCreate):
    item_json = json.loads(item_obj.json())
    ipfs_metadata = ipfs.add_json(item_json)
    return "http://127.0.0.1:8080/ipfs/{cid}".format(cid=ipfs_metadata)

# Transfer item token
def transfer_item(TXReqs, itemid: int, receiver: str):
    # Transfers item NFT via smart contract
    receiver = '0x2499f0d596a9e6C634Bf6191f6B5B6FB33E89997'
    transferred = sendtx(TXReqs.contract.functions.transferItemToken(itemid, receiver), TXReqs)
    # Returns False if Item transfer failed
    if not transferred:
        return False
    # Returns True indicating successful transfer
    return True

# Get item by ID
def get_item(db: Session, TXReqs, itemid: int):
    # Verifies items existence in-db
    itemid = db.query(db_schemas.Item).filter(
        db_schemas.Item.id == itemid).first().id
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
