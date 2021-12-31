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
from ..onchain.onchain_methods import buildtx
from ..onchain.onchain_objects import TXReqs
# Error Handling
import web3.exceptions as exceptions
from ..exceptions.exception_handlers import OnChainExceptionHandler


def create_item(ipfs, tx_reqs: TXReqs,
                item_obj: item_objects.ItemCreate) -> bool:
    """
    Create Item Token
    """
    # Generates NFT metadata URL (hosted on IPFS)
    metadata_uri = create_metadata(ipfs, item_obj)
    # Mints Item NFT via smart contract
    try:
        signed_tx = buildtx(
            tx_reqs.contract.functions.mintItemToken(metadata_uri), tx_reqs)
        tx_reqs.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    except exceptions.ContractLogicError as Error:
        OnChainExceptionHandler(Error)
    # Returns True indicating successful creation
    return True


def create_metadata(ipfs, item_obj: item_objects.ItemCreate) -> str:
    """
    Create Item Token metadata -> host on IPFS
    """
    item_json = json.loads(item_obj.json())
    ipfs_metadata = ipfs.add_json(item_json)
    # Returns URL to IPFS-hosted metadata
    return "http://127.0.0.1:8080/ipfs/{cid}".format(cid=ipfs_metadata)


def transfer_item(database: Session, tx_reqs: TXReqs, item_id: int,
                  receiver: str) -> bool:
    """
    Transfer Item Token
    """
    # Transfers item NFT via smart contract
    try:
        signed_tx = buildtx(
            tx_reqs.contract.functions.transferItemToken(
                item_id,
                get_user_publickey(database, receiver).decode()), tx_reqs)
        tx_reqs.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    except exceptions.ContractLogicError as Error:
        OnChainExceptionHandler(Error)
    # Returns True indicating successful transfer
    return True


def get_item(database: Session, tx_reqs: TXReqs, item_id: int) -> dict:
    """
    Get Item Token (metadata) after validating existence in-database
    """
    # Obtains items existence in-database
    item_obj = database.query(db_schemas.Item).filter(
        db_schemas.Item.id == item_id).first()
    if not item_obj:
        return None
    # Obtains and formats JSONized metadata
    metadata = get_metadata(tx_reqs, item_id)
    metadata['transfer_count'] = item_obj.transfers
    metadata['avg_hold_time'] = str(item_obj.holdtime_avg).split('.')[:-1][0]
    metadata['creation_date'] = item_obj.creation_date.strftime("%m/%d/%y")
    # If set to stolen or lost, add report information to the metadata
    if item_obj.stolen_status or item_obj.lost_status == True:
        report = {
                    'stolen':item_obj.stolen_status, 
                    'lost':item_obj.lost_status
                }
        metadata['report'] = report
    # Returns formatted metadata
    return metadata


def get_metadata(tx_reqs: TXReqs, item_id: int) -> dict:
    """
    Get Item Token metadata
    """
    # Fetches metadata URI -> loads as JSON
    try:
        rawuri = tx_reqs.contract.functions.tokenURI(item_id).call()
    except exceptions.ContractLogicError as Error:
        OnChainExceptionHandler(Error)
    uri = urlopen(rawuri)
    metadata = json.load(uri)
    metadata['id'] = item_id
    # Return JSONized metadata object
    return metadata


def get_user_items(database: Session, tx_reqs: TXReqs, address: str) -> List[dict]:
    """
    Get Item Tokens currently owned by a user
    """
    owned_ids = tx_reqs.contract.functions.ownedItemTokens(address).call()
    owned_items = [get_item(database, tx_reqs, id) for id in owned_ids]
    # Return list of item metadatas
    return owned_items


def set_item_claimability(tx_reqs: TXReqs, item_id: int) -> bool:
    """
    Set claimability status of an Item Token
    """
    try:
        signed_tx = buildtx(
            tx_reqs.contract.functions.setItemClaimability(item_id), tx_reqs)
        item_claimability = tx_reqs.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    except exceptions.ContractLogicError as Error:
        OnChainExceptionHandler(Error)
    # Return newly set claimability status
    return item_claimability


def get_item_claimability(tx_reqs: TXReqs, item_id: int) -> bool:
    """
    Get claimability status of an Item Token
    """
    try:
        item_claimability = tx_reqs.contract.functions.viewItemClaimability(
            item_id).call()
    except exceptions.ContractLogicError as Error:
        OnChainExceptionHandler(Error)
    # Return item claimability boolean
    return item_claimability


def claim_item(tx_reqs: TXReqs, item_id: int) -> bool:
    """
    Claim Item Token
    """
    try:
        signed_tx = buildtx(tx_reqs.contract.functions.claimItemToken(item_id),
                            tx_reqs)
        tx_reqs.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    except exceptions.ContractLogicError as Error:
        OnChainExceptionHandler(Error)
    # Return True indicating successful burn
    return True


def get_item_transfercount(database: Session, item_id: int) -> int:
    """
    Get transfer count of item
    """
    transfercount = database.query(db_schemas.Item).filter(
        db_schemas.Item.id == item_id).options(load_only('id')).first()
    if not transfercount:
        return None
    # Return transfer count
    return transfercount.transfers


def burn_item_token(tx_reqs: TXReqs, item_id: int) -> bool:
    """
    Burn Item Token
    """
    try:
        signed_tx = buildtx(tx_reqs.contract.functions.burnItemToken(item_id),
                            tx_reqs)
        tx_reqs.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    except exceptions.ContractLogicError as Error:
        OnChainExceptionHandler(Error)
    # Return True indicating successful burn
    return True
