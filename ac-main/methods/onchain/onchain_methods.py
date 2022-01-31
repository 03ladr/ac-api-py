"""
On-Chain Methods/Functions
"""
from typing import Union

from eth_account.datastructures import SignedTransaction
from eth_utils.exceptions import ValidationError
from sqlalchemy.orm import Session, load_only

from ..cryptography.aes_methods import aes_decrypt
from ..database import db_schemas
from ..exceptions.exception_objects import (
    NonExistentTokenError,
    NotOperatorError,
    PrivateKeyError,
)
from .ItemContractABI import ItemContractABI
from .ProxyContractABI import ProxyContractABI
from .onchain_objects import ProxyTXReqs, TXReqs


def buildtx(function, tx_reqs: Union[TXReqs,
                                     ProxyTXReqs]) -> SignedTransaction:
    """
    Builds and signs transaction to be dispatched on-chain
    """
    # Loading senders account
    privatekey = aes_decrypt(tx_reqs.privatekey, tx_reqs.passkey)
    try:
        sender = tx_reqs.w3.eth.account.privateKeyToAccount(
            privatekey.decode())
    except (ValidationError, ValueError):
        raise PrivateKeyError

    # Building tx
    txdeps = {
        'from': sender.address,
        'gasPrice': tx_reqs.w3.eth.gas_price,
        'nonce': tx_reqs.w3.eth.getTransactionCount(sender.address)
    }
    rawtx = function.buildTransaction(txdeps)

    # Signing and returning transaction object
    signed_tx = sender.signTransaction(rawtx)
    return signed_tx


def build_mint_tx(db_user: db_schemas.User, passkey: str,
                  database: Session) -> TXReqs:
    """
    Builds transaction sender object for proxy contract token minting
    """
    if db_user.type != "operator":
        raise NotOperatorError
    db_operator = database.query(db_schemas.Operator).filter(
        db_schemas.Operator.id == db_user.id).options(
            load_only('contract')).first()
    if not db_operator:
        raise NotOperatorError
    return ProxyTXReqs(target=db_operator.contract.decode(),
                       privatekey=db_operator.accesskey,
                       passkey=passkey)


def build_burn_tx(item_id: int, db_user: db_schemas.User, passkey: str,
                  database: Session) -> TXReqs:
    """
    Builds transaction sender object for proxy contract token burning
    """
    db_item = database.query(db_schemas.Item).filter(
        db_schemas.Item.id == item_id).options(load_only('contract')).first()
    return ProxyTXReqs(target=db_item.contract.decode(),
                       privatekey=db_user.accesskey,
                       passkey=passkey)


def build_item_call(item_id: int, database: Session) -> TXReqs:
    """
    Builds basic call sender object for item contract interaction
    """
    db_item = database.query(db_schemas.Item).filter(
        db_schemas.Item.id == item_id).options(load_only('contract')).first()
    if not db_item:
        raise NonExistentTokenError
    return TXReqs(contract=db_item.contract.decode(), abi=ItemContractABI)


def build_item_tx(item_id: int, db_user: db_schemas.User, passkey: str,
                  database: Session) -> TXReqs:
    """
    Builds transaction sender object for item contract interaction
    """
    tx_reqs = build_item_call(item_id, database)
    tx_reqs.privatekey, tx_reqs.passkey = db_user.accesskey, passkey
    return tx_reqs
