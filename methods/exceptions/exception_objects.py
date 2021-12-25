"""
Error Exception Objects
"""


class PrivateKeyError(Exception):
    """
    Exception Raised Upon Incorrect Private Key Input
    """
    def __init__(self, message="Incorrect private key"):
        self.message = message
        super().__init__(self.message)


class NonExistentTokenError(Exception):
    """
    Exception Raised Upon Nonexistent Token Interaction
    """
    def __init__(self, message="Nonexistent Item Token"):
        self.message = message
        super().__init__(self.message)


class OwnershipError(Exception):
    """
    Exception Raised Upon Non-Owner Item Token Interaction
    """
    def __init__(self, message="Caller is not owner"):
        self.message = message
        super().__init__(self.message)


class NotOperatorError(Exception):
    """
    Exception Raised Upon Forbidden Non-Operator Interaction
    """
    def __init__(self, message="Caller is not an operator"):
        self.message = message
        super().__init__(self.message)


class NotClaimableError(Exception):
    """
    Exception Raised Upon Claiming Non-Claimable Item Token
    """
    def __init__(self, message="Item Token is not claimable"):
        self.message = message
        super().__init__(self.message)
