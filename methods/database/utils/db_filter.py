"""
Smart contract event log --> database population module
"""
# Database Item
from ..db_schemas import Item


class ItemFilters:
    """
    Smart contract event log filter -
    Checks for mint, burn and transfer events
    """
    def __init__(self, db, contract):
        self.db = db
        self.mintfilter = contract.events.Mint.createFilter(fromBlock="latest")
        self.burnfilter = contract.events.Burn.createFilter(fromBlock="latest")
        self.transferfilter = contract.events.Transfer.createFilter(fromBlock="latest")

    def filter(self) -> bool:
        mints = self.mintfilter.get_new_entries()
        burns = self.mintfilter.get_new_entries()
        transfers = self.transferfilter.get_new_entries()

        if mints:
            for mint in mints:
                itemid = mint['args']['itemid']
                db_item = Item(id=itemid)
                self.db.add(db_item)
                self.db.commit()

        if burns:
            for burn in burns:
                itemid = mint['args']['itemid']
                db_item = Item(id=itemid)
                self.db.delete(db_item)
                self.db.commit()

        if transfers:
            for transfer in transfers:
                itemid = transfer['args']['itemid']
                transfercount = self.db.query(Item).filter(
                    Item.id == itemid).options(
                        load_only('id')).one()
                self.db.query(Item).filter(
                    Item.id == itemid).update(
                        {'transfers': transfercount + 1})

        return True
