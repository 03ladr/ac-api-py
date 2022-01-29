"""
Item Token Methods/Functions
"""
import json
from typing import List
from urllib.request import urlopen

from eth_account import Account
from sqlalchemy.orm import Session, load_only
from web3 import exceptions

from ..cryptography.aes_methods import aes_decrypt
from ..database import db_schemas
from ..exceptions.exception_handlers import OnChainExceptionHandler
from ..exceptions.exception_objects import CredentialError, OwnershipError
from ..onchain.onchain_methods import buildtx
from ..onchain.onchain_objects import ProxyTXReqs, TXReqs
from ..users.user_methods import get_user_publickey
from . import item_objects


def create_item(item_obj_list: List[item_objects.ItemCreate], ipfs,
                tx_reqs: ProxyTXReqs) -> bool:
    """
    Create Item Token
    """
    for item_obj in item_obj_list:
        # Generates NFT metadata URL (hosted on IPFS)
        metadata_uri = create_metadata(ipfs, item_obj)
        # Mints Item NFT via smart contract
        try:
            signed_tx = buildtx(
                tx_reqs.contract.functions.MintToken(tx_reqs.target,
                                                     metadata_uri), tx_reqs)
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


def transfer_item(item_id: int, receiver: str, tx_reqs: TXReqs,
                  database: Session) -> bool:
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


def get_item(item_id: int, tx_reqs: TXReqs) -> dict:
    """
    Get Item Token (metadata) after validating existence in-database
    """
    # Obtains and formats JSONized metadata
    metadata = get_metadata(item_id, tx_reqs)

    # If an average hold time and creation date is recorded, add that data to the metadata

    # If set to stolen or lost, add report information to the metadata

    # Returns formatted metadata
    return metadata


def get_metadata(item_id: int, tx_reqs: TXReqs) -> dict:
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


# def get_user_items(database: Session, tx_reqs: TXReqs,
#                    address: str) -> List[dict]:
#     """
#     Get Item Tokens currently owned by a user
#     """
#     owned_ids = tx_reqs.contract.functions.ownedItemTokens(address).call()
#     owned_items = [get_item(tx_reqs, id) for id in owned_ids]
#     # Return list of item metadatas
#     return owned_items


def set_item_claimability(
        item_id: int,
        tx_reqs: TXReqs) -> None:  # return to bool after updating contract
    """
    Set claimability status of an Item Token
    """
    try:
        signed_tx = buildtx(
            tx_reqs.contract.functions.setItemClaimability(item_id), tx_reqs)
        tx_reqs.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        # change to assignment after updating contract
    except exceptions.ContractLogicError as Error:
        OnChainExceptionHandler(Error)
    # Returns?


def get_item_claimability(item_id: int, tx_reqs: TXReqs) -> bool:
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


def claim_item(item_id: int, tx_reqs: TXReqs) -> True:
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


def burn_item_token(item_id: int, tx_reqs: ProxyTXReqs) -> True:
    """
    Burn Item Token
    """
    try:
        signed_tx = buildtx(
            tx_reqs.contract.functions.BurnToken(tx_reqs.target, item_id),
            tx_reqs)
        tx_reqs.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    except exceptions.ContractLogicError as Error:
        OnChainExceptionHandler(Error)
    # Return True indicating successful burn
    return True


def toggle_item_missing(database: Session, tx_reqs: TXReqs,
                        item_id: int) -> bool:
    """
    Report item as stolen/missing
    """
    # If the item token does not exist, raise exception
    try:
        item_owner = tx_reqs.contract.functions.ownerOf(item_id).call()
    except exceptions.ContractLogicError as Error:
        OnChainExceptionHandler(Error)
    # Obtain public key of caller
    try:
        address = Account.from_key(
            aes_decrypt(tx_reqs.privatekey, tx_reqs.passkey)).address
    except TypeError:
        raise CredentialError
    # If the caller is not the token owner, raise exception
    if address != item_owner:
        raise OwnershipError
    # Query db to check current missing status
    item_obj = database.query(
        db_schemas.Item).filter(db_schemas.Item.id == item_id).options(
            load_only('missing_status')).first()
    # Depending on whether the item is set as missing or not, construct an updating db query
    if item_obj.missing_status:
        db_update = {'missing_status': False}
    elif not item_obj.missing_status:
        db_update = {'missing_status': True}
    # Dispatch db update
    database.query(db_schemas.Item).filter(
        db_schemas.Item.id == item_id).update(db_update)
    database.commit()
    # Return updated missing status
    return db_update['missing_status']
