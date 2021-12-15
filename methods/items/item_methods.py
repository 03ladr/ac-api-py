# Utilities
import json
from urllib.request import urlopen
# Database tooling
from sqlalchemy.orm import Session
from sqlalchemy import or_
# Local modules
from . import item_objects
from ..db import db_schemas
from ..users.user_objects import User
from .modules.create_metadata import create_metadata
from .modules.mint_nft import mint_nft

# Item creation
def create_item(contract, ipfs, item_obj: item_objects.ItemCreate, sender: str):
    # Generating NFT metadata URL (hosted on IPFS)
    metadata = create_metadata(ipfs, item_obj)
    
    # Mint NFT via smart contract
    itemid = mint_nft(contract, metadata, sender)
    
    # Returns None if Item creation failed
    if not itemid:
        return None

    # Returns True indicating successful creation
    return True

# Transfer Item
def transfer_item(db: Session, w3, contract, itemid: int, receiver: str, TX):
    rawtx = ac.functions.transferItemToken(itemid, receiver).buildTransaction({'from':TX.sender, 'gasPrice': w3.eth.gas_price, 'nonce':w3.eth.getTransactionCount(TX.sender)})
    signedtx = w3.eth.account.signTransaction(tx, TX.privatekey)

    try:
        w3.eth.sendRawTransaction(signedtx.rawTransaction)
    except:
        return False

    return True

# Gets item by ID
def get_item(db: Session, itemid: int, sender: str):
    itemid = db.query(db_schemas.Item).filter(db_schemas.Item.id == itemid).first().id
    try:
        uri = contract.functions.tokenURI(itemid).call({"from":sender})
        url = urlopen(uri)
        metadata = json.load(url.read())
    except:
        return False
    
    return metadata

# Get all items
def get_items(db: Session, skap: int = 0, limit: int = 100):
    return db.query(db_schemas.Item).offset(skip).limit(limit).all()
