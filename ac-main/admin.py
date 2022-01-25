"""
Curses Admin Interface
To be replaced with fastapi
"""
from os import getenv

from cursesmenu import *
from cursesmenu.items import *
from methods.database import db_schemas
from methods.database.database import SessionLocal
from methods.onchain.onchain_config import contract, w3
from methods.users import user_methods


Session = SessionLocal()


def user_interface():
    """
    Curses interface
    """
    menu = CursesMenu("Authentichain Administrative Control", "Main Menu")
    f1 = FunctionItem("Set user as Operator", set_operator)
    f2 = FunctionItem("Credit Account", credit_account)
    menu.append_item(f1)
    menu.append_item(f2)
    menu.show()


def set_operator():
    """
    Set user as operator by attribute
    """
    user_attr = input("(Select User)> ")
    operator_brand = input("(Select Brand)> ")
    user_publickey = user_methods.get_user_publickey(Session, user_attr)
    contract.functions.grantRole(OPERATOR_ROLE,
                                 user_publickey.decode()).transact(
                                     {"from": getenv('CONTRACT_CREATOR')})
    Session.query(
        db_schemas.User).filter(db_schemas.User.publickey == user_publickey).update({
            "type":
            "operator",
            "brand":
            operator_brand
        })
    Session.commit()


def credit_account():
    """
    Credit given account with n-ether
    """
    user_attr = input("(Select Recipient)> ")
    sender_key = input("(Provide senders private key)> ")
    send_amount = w3.toWei(input("(Amount to credit recipient)> "), 'ether')
    sender = w3.eth.account.privateKeyToAccount(sender_key)
    db_user = user_methods.get_user_publickey(Session, user_attr)
    raw_tx = {
            'to': db_user.decode(),
            'value': send_amount,
            'from': sender.address,
            'gas': 21000,
            'gasPrice': w3.eth.gasPrice,
            'nonce': w3.eth.getTransactionCount(sender.address)
            }
    signed_tx = sender.signTransaction(raw_tx)
    w3.eth.sendRawTransaction(signed_tx.rawTransaction)


user_interface()
