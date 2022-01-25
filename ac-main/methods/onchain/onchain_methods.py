"""
On-Chain Methods/Functions
"""
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
from .MintContractABI import MintContractABI
from .onchain_objects import TXReqs


def buildtx(function, tx_reqs: TXReqs) -> SignedTransaction:
    """
    Send On-Chain Transaction
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
    Gets user account and returns it if an operator
    """
    if db_user.type != "operator":
        raise NotOperatorError
    db_operator = database.query(db_schemas.Operator).filter(
        db_schemas.Operator.id == db_user.id).options(
            load_only('contract')).first()
    if not db_operator:
        raise NotOperatorError
    return TXReqs(privatekey=db_user.accesskey,
                  contract=db_operator.contract.decode(),
                  abi=MintContractABI,
                  passkey=passkey)


def build_item_call(database: Session, item_id: int) -> TXReqs:
    db_item = database.query(db_schemas.Item).filter(
        db_schemas.Item.id == item_id).options(load_only('contract')).first()
    if not db_item:
        raise NonExistentTokenError
    return TXReqs(contract=db_item.contract.decode(), abi=ItemContractABI)


def build_item_tx(database: Session, db_user: db_schemas.User, passkey: str,
                  item_id: int) -> TXReqs:
    tx_reqs = build_item_call(database, item_id)
    tx_reqs.privatekey, tx_reqs.passkey = db_user.accesskey, passkey
    return tx_reqs
