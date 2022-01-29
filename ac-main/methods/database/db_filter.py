"""
Smart contract event log --> database population module
"""
from ..db_schemas import Item, Operator, User


class TokenFilters:
    """
    Smart contract event log filter -
    Checks for mint, burn and deploy events
    """
    def __init__(self, db, contract):
        self.db = db
        self.mintfilter = contract.events.Mint.createFilter(fromBlock="latest")
        self.burnfilter = contract.events.Burn.createFilter(fromBlock="latest")
        self.deployfilter = contract.events.Deploy.createFilter(
            fromBlock="latest")

    def filter(self) -> bool:
        """
        Filter function
        """
        mints = self.mintfilter.get_new_entries()
        burns = self.burnfilter.get_new_entries()
        deploys = self.deployfilter.get_new_entries()

        if mints:
            for mint in mints:
                item_id = mint['args']['itemid']
                contadr = mint['args']['contadr']
                db_item = Item(id=item_id, brand=contadr)
                self.db.add(db_item)
                self.db.commit()

        if burns:
            for burn in burns:
                item_id = burn['args']['itemid']
                contadr = burn['args']['contadr']
                self.db.query(Item).filter(Item.id == item_id).delete()
                self.db.commit()

        if deploys:
            for deploy in deploys:
                operator = deploy['args']['operator']
                contadr = deploy['args']['contadr']
                db_user = self.db.query(User).filter(
                    User.publickey == operator).first()
                db_operator = Operator(id=db_user.id, contract=contadr)
                self.db.add(db_operator)
                self.db.commit()

        return True
