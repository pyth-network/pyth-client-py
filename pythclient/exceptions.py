class RateLimitedException(Exception):
    """
    Raised when the client is rate-limited.
    """
    pass

class SolanaException(Exception):
    """
    Raised when the Solana API returns an error.
    """
    pass

class WebSocketClosedException(Exception):
    """
    Raised when the WebSocket is closed while we are waiting for an update.
    """

class NotLoadedException(Exception):
    """
    Raised when the child accounts are not yet loaded.
    """

class MissingAccountException(Exception):
    """
    Raised when an account is needed but is missing.
    """
