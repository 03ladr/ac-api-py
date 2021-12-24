"""
Item Token Methods/Functions
"""
# Utilities
import json
from urllib.request import urlopen
# Typing
from typing import List
# Database tooling
from sqlalchemy.orm import Session, load_only
# Local modules
from . import item_objects
from ..database import db_schemas
from ..users.user_methods import get_user_publickey
from ..onchain.onchain_methods import sendtx
from ..onchain.onchain_objects import TXReqs


def create_item(ipfs, tx_reqs: TXReqs, item_obj: item_objects.ItemCreate) -> bool:
    """
    Create Item Token
    """
    # Generates NFT metadata URL (hosted on IPFS)
    metadata_uri = create_metadata(ipfs, item_obj)
    # Mints Item NFT via smart contract
    minted = sendtx(tx_reqs.contract.functions.mintItemToken(metadata_uri),
                    tx_reqs)
    # Returns None if Item creation failed
    if not minted:
        return None
    # Returns True indicating successful creation
    return True


def create_metadata(ipfs, item_obj: item_objects.ItemCreate) -> str:
    """
    Create Item Token metadata -> host on IPFS
    """
    item_json = json.loads(item_obj.json())
    ipfs_metadata = ipfs.add_json(item_json)
    return "http://127.0.0.1:8080/ipfs/{cid}".format(cid=ipfs_metadata)


def transfer_item(database: Session, tx_reqs: TXReqs, item_id: int,
                  receiver: str) -> bool:
    """
    Transfer Item Token
    """
    # Transfers item NFT via smart contract
    transferred = sendtx(
        tx_reqs.contract.functions.transferItemToken(
            item_id,
            get_user_publickey(database, receiver).decode()), tx_reqs)
    # Returns None if Item transfer failed
    if not transferred:
        return None
    # Returns True indicating successful transfer
    return True


def get_item(database: Session, tx_reqs: TXReqs, item_id: int):
    """
    Get Item Token (metadata) after validating existence in-database
    """
    # Verifies items existence in-database
    item_id = database.query(db_schemas.Item).filter(
        db_schemas.Item.id == item_id).options(load_only('id')).first()
    if not item_id:
        return None

    # Returns JSON Metadata Object
    return get_metadata(tx_reqs, item_id.id)


def get_metadata(tx_reqs: TXReqs, item_id: int):
    """
    Get Item Token metadata
    """
    # Fetches metadata URI -> loads as JSON
    rawuri = tx_reqs.contract.functions.tokenURI(item_id).call()
    uri = urlopen(rawuri)
    metadata = json.load(uri)
    metadata['id'] = item_id
    return metadata


def get_user_items(tx_reqs: TXReqs, address: str) -> List:
    """
    Get Item Tokens currently owned by a user
    """
    owned_ids = tx_reqs.contract.functions.ownedItemTokens(address).call()
    owned_items = [get_metadata(tx_reqs, id) for id in owned_ids]
    return owned_items


def set_item_claimability(tx_reqs: TXReqs, item_id: int) -> bool:
    """
    Set claimability status of an Item Token
    """
    item_claimability = sendtx(
        tx_reqs.contract.functions.setItemClaimability(item_id), tx_reqs)
    return item_claimability


def get_item_claimability(tx_reqs: TXReqs, item_id: int) -> bool:
    """
    Get claimability status of an Item Token
    """
    item_claimability = tx_reqs.contract.functions.viewItemClaimability(
        item_id).call()
    return item_claimability


def claim_item(tx_reqs: TXReqs, item_id: int) -> bool:
    """
    Claim Item Token
    """
    sendtx(tx_reqs.contract.functions.claimItemToken(item_id), tx_reqs)
    return True


def get_item_transfercount(database, item_id: int) -> int:
    """
    Get transfer count of item
    """
    transfercount = database.query(db_schemas.Item).filter(
        db_schemas.Item.id == item_id).options(load_only('id')).first()
    return transfercount.id


def burn_item_token(tx_reqs: TXReqs, item_id: int) -> bool:
    """
    Burn Item Token
    """
    sendtx(tx_reqs.contract.functions.burnItemToken(item_id), tx_reqs)
    return True
