# Utilities
from random import randrange
import json

# Database tooling
from sqlalchemy.orm import Session
from sqlalchemy import or_
from os import urandom

# Local modules
from . import item_objects
from ..users.user_objects import User
from .modules.create_metadata import create_metadata
from .modules.mint_nft import mint_nft
from ..db import db_schemas
from ..vars.strids import ItemID, UserID


# Gets item by ID.
def get_item_by(db: Session, itemid: ItemID):
    return db.query(db_schemas.Item).filter(db_schemas.Item.id == itemid).first()


# Get all items
def get_items(db: Session, skap: int = 0, limit: int = 100):
    return db.query(db_schemas.Item).offset(skip).limit(limit).all()


# Item creation
def create_item(db: Session, w3, item: item_objects.ItemCreate, sender: User):
    # Generating NFT metadata URL (hosted on IPFS)
    metadata = create_metadata(item)
    
    # Mint NFT via smart contract
    itemid = mint_nft(w3, metadata, sender.publickey)
    
    if not itemid or metadata:
        return None

    # Committing to database
    db_item = db_schemas.Item(
        id=bytes(itemid, 'utf-8'),
        owner_id=sender.id,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    # Returning item object
    return db_item


# Will need to import more complex module handling transfer facilitation fully
# ...as in with our smart contract
def transfer_item(db: Session, itemid: ItemID, receiverid: bytes):
    db_item = db.query(db_schemas.Item).filter(db_schemas.Item.id == itemid)
    if not db_item:
        return False

    db_item.update({"owner_id": receiverid})
    db.commit()
    return True
