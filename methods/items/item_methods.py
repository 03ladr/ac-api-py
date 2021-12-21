"""
Item Token Methods/Functions
"""
# Utilities
import json
from urllib.request import urlopen
# Typing
from typing import List
# Database tooling
from sqlalchemy.orm import Session
# Local modules
from . import item_objects
from ..database import db_schemas
from ..users.user_methods import get_user_publickey
from ..onchain.onchain_methods import sendtx
from ..onchain.onchain_objects import TXReqs

def create_item(ipfs, item_obj: item_objects.ItemCreate, TXReqs) -> bool:
    """
    Create Item Token
    """
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


def create_metadata(ipfs, item_obj: item_objects.ItemCreate) -> str:
    """
    Create Item Token metadata -> host on IPFS
    """
    item_json = json.loads(item_obj.json())
    ipfs_metadata = ipfs.add_json(item_json)
    return "http://127.0.0.1:8080/ipfs/{cid}".format(cid=ipfs_metadata)


def transfer_item(TXReqs: TXReqs, itemid: int, receiver: str) -> bool:
    """
    Transfer Item Token
    """
    # Transfers item NFT via smart contract
    transferred = sendtx(
        TXReqs.contract.functions.transferItemToken(
            itemid, get_user_publickey(receiver)), TXReqs)
    # Returns False if Item transfer failed
    if not transferred:
        return False
    # Returns True indicating successful transfer
    return True


def get_item(db: Session, TXReqs: TXReqs, itemid: int):
    """
    Get Item Token (metadata) after validating existence in-database
    """
    # Verifies items existence in-db
    itemid = db.query(
        db_schemas.Item).filter(db_schemas.Item.id == itemid).first().id
    # Returns JSON Metadata Object
    return get_metadata(TXReqs, itemid)


def get_metadata(TXReqs: TXReqs, itemid: int):
    """
    Get Item Token metadata
    """
    # Fetches metadata URI -> loads as JSON
    rawuri = TXReqs.contract.functions.tokenURI(itemid).call()
    uri = urlopen(rawuri)
    metadata = json.load(uri)
    metadata['id'] = itemid
    return metadata


def get_user_items(TXReqs, address: str) -> List:
    """
    Get Item Tokens currently owned by a user
    """
    owned_ids = TXReqs.contract.functions.ownedItemTokens(address).call()
    owned_items = [get_metadata(TXReqs, id) for id in owned_ids]
    return owned_items


def set_item_claimability(TXReqs, itemid: int) -> bool:
    """
    Set claimability status of an Item Token
    """
    item_claimability = sendtx(TXReqs.contract.functions.setItemClaimability(itemid), TXReqs)
    return item_claimability


def get_item_claimability(TXReqs, itemid: int) -> bool:
    """
    Get claimability status of an Item Token
    """
    item_claimability = TXReqs.contract.functions.viewItemClaimability(itemid).call()
    return item_claimability


def get_item_transfercount(db, itemid: int) -> int:
    """
    Get transfer count of item
    """
    transfercount = db.query(db_schemas.Item).filter(db_schemas.Item.id == itemid).one()
    return transfercount
