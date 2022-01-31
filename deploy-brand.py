"""
Brand Deployment Script
Incomplete
"""

from ac-main.methods.database.database import SessionLocal
from ac-main.methods.onchain.onchan_config import contract, w3
from ac-main.methods.users.user_methods import create_user


def create_retailer_account():
    account = w3.eth.account.create()
    pubkey, privkey_raw = bytes(account.address,
                                'utf-8'), account.privateKey.hex()
