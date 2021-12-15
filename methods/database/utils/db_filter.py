# On-Chain Connectivity/Tooling
from ...onchain.abi import abi
# Item Modules
from ..db_schemas import Item


class ItemFilters:
    def __init__(self, db, contract):
        self.db = db
        self.mintfilter = contract.events.Mint.createFilter(fromBlock="latest")
        self.burnfilter = contract.events.Burn.createFilter(fromBlock="latest")

    def filter(self):
        mints = self.mintfilter.get_new_entries()
        burns = self.mintfilter.get_new_entries()

        if mints:
            for mint in mints:
                itemid = mint['args']['itemid']
                db_item = db_schemas.Item(id=itemid)
                self.db.add(db_item)
                self.db.commit()

        if burns:
            for burn in burns:
                itemid = mint['args']['itemid']
                db_item = db_schemas.Item(id=itemid)
                self.db.delete(db_item)
                self.db.commit()

        return True
