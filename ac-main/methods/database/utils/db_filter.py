"""
Smart contract event log --> database population module
"""
from ..db_schemas import Item


class ItemFilters:
    """
    Smart contract event log filter -
    Checks for mint, burn and transfer events
    """
    def __init__(self, db, contract):
        self.db = db
        self.mintfilter = contract.events.Mint.createFilter(fromBlock="latest")

    def filter(self) -> bool:
        """
        Filter function
        """
        mints = self.mintfilter.get_new_entries()

        if mints:
            for mint in mints:
                item_id = mint['args']['itemid']
                contradr = mint['args']['contradr']
                db_item = Item(id=item_id, brand=contradr)
                self.db.add(db_item)
                self.db.commit()

        return True
