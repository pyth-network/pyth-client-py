"""
Library-wide settings.
"""

BACKOFF_MAX_VALUE = 16
BACKOFF_MAX_TRIES = 8

# The following getter functions are passed to the backoff decorators

def get_backoff_max_value() -> int:
    return BACKOFF_MAX_VALUE

def get_backoff_max_tries() -> int:
    return BACKOFF_MAX_TRIES
