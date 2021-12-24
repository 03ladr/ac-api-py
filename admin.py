"""
Admin Method API
"""
# Cryptography modules
from methods.database.database import SessionLocal
from methods.database import db_schemas
# On-Chain Connectivity/Tooling
from methods.onchain.onchain_config import contract
from config import CONTRACT_CREATOR
# User Methods
from methods.users import user_methods
# Curses dependency
from cursesmenu import *
from cursesmenu.items import *

Session = SessionLocal()

def user_interface():
    """
    Curses interface
    """
    menu = CursesMenu("Authentichain Administrative Control", "Main Menu")
    f1 = FunctionItem("Set user as Operator", set_operator)
    menu.append_item(f1)
    menu.show()


def set_operator():
    """
    Set user as operator by attribute
    """
    user_attr = input("(Select User)> ")
    operator_brand = input("(Select Brand)> ")
    db_user = user_methods.get_user_by(Session, user_attr)
    contract.functions.grantRole(user_methods.OPERATOR_ROLE,
                                 db_user.publickey.decode()).transact(
                                    {"from": CONTRACT_CREATOR})
    Session.query(db_schemas.User).filter(db_schemas.User.id == db_user.id).update({
        "type": "operator", "brand": operator_brand}
    )
    Session.commit()


user_interface()
