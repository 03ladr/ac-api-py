"""
Exception Handler(s)
"""
# Exception Objects
from .exception_objects import *

def OnChainExceptionHandler(exception: Exception) -> Exception:
    """
    Exception Handler For On-Chain Transactions
    """
    error_type = str(exception).split(":")[-1]
    if "Caller is not token owner" in error_type:
        raise OwnershipError
    elif "owner query for nonexistent token" in error_type:
        raise NonExistentTokenError
    elif "URI query for nonexistent token" in error_type:
        raise NonExistentTokenError
    elif "is missing role" in error_type:
        raise NotOperatorError
    elif "is not claimable" in error_type:
        raise NotClaimableError
