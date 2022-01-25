"""
Error Exception Objects
"""


class PrivateKeyError(Exception):
    """
    Exception raised upon invalid private key input
    """
    def __init__(self, message="Incorrect private key"):
        self.message = message
        super().__init__(self.message)


class NonExistentTokenError(Exception):
    """
    Exception taised upon nonexistent token interaction
    """
    def __init__(self, message="Nonexistent Item Token"):
        self.message = message
        super().__init__(self.message)


class OwnershipError(Exception):
    """
    Exception raised upon non-owner item token interaction
    """
    def __init__(self, message="Caller is not owner"):
        self.message = message
        super().__init__(self.message)


class NotOperatorError(Exception):
    """
    Exception raised upon forbidden non-operator interaction
    """
    def __init__(self, message="Caller is not an operator"):
        self.message = message
        super().__init__(self.message)


class NotClaimableError(Exception):
    """
    Exception raised upon claim attempt on non-claimable item token
    """
    def __init__(self, message="Item Token is not claimable"):
        self.message = message
        super().__init__(self.message)


class UnknownAccountError(Exception):
    """
    Exception raised upon interacting with nonexistent account
    """
    def __init__(self, message="User not found"):
        self.message = message
        super().__init__(self.message)


class CredentialError(Exception):
    """
    Exception raised upon incorrect login credentials
    """
    def __init__(self, message="Credential Exception"):
        self.message = message
        super().__init__(self.message)
