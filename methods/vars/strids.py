from pydantic import constr

# ID specification
ItemID = bytes
UserID = constr(min_length=10, max_length=10)
