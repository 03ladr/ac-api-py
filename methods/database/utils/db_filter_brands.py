"""
Smart contract event log --> database population module
"""
# Utilities
from datetime import datetime
# Database Dependencies
from ..db_schemas import Item, TransferLog
from sqlalchemy.orm import load_only


class ItemFilters:
    """
    Smart contract event log filter -
    Checks for mint, burn and transfer events
    """
    def __init__(self, db, contract):
        self.db = db
        self.mintfilter = contract.events.Mint.createFilter(fromBlock="latest")
        self.burnfilter = contract.events.Burn.createFilter(fromBlock="latest")
        self.transferfilter = contract.events.ItemTransfer.createFilter(
            fromBlock="latest")

    def filter(self) -> bool:
        """
        Filter function
        """
        current_time = datetime.now()

        mints = self.mintfilter.get_new_entries()
        burns = self.burnfilter.get_new_entries()
        transfers = self.transferfilter.get_new_entries()

        if mints:
            for mint in mints:
                item_id = mint['args']['itemid']
                db_item = Item(id=item_id, creation_date=datetime.now(), transfers=0)
                self.db.add(db_item)
                self.db.commit()

        if burns:
            for burn in burns:
                item_id = burn['args']['itemid']
                self.db.query(Item).filter(id=item_id).delete()
                self.db.commit()

        if transfers:
            for transfer in transfers:
                item_id = transfer['args']['itemid']
                item_obj = self.db.query(Item).filter(
                    Item.id == item_id).options(
                        load_only('transfers', 'creation_date')).first() 
                elapsed_time = current_time - item_obj.creation_date
                try:
                    avg_hold_time = elapsed_time / item_obj.transfers
                except ZeroDivisionError:
                    avg_hold_time = elapsed_time
                self.db.query(Item).filter(Item.id == item_id).update(
                        {
                            'transfers': item_obj.transfers + 1,
                            'holdtime_avg': avg_hold_time,
                            'report_to': None,
                            'missing_status': False
                        })
                self.db.query(TransferLog).filter(TransferLog.tx_id == transfers['tx_id']).update(
                        {
                            'id': item_id,
                            'date': current_time,
                            'to': transfer['args']['to'],
                            'from': transfer['args']['from']
                        }) 
                self.db.commit()

        return True
