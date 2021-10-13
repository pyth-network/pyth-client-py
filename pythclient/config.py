"""
Library-wide settings.
"""

backoff_max_value = 16
backoff_max_tries = 8

# The following getter functions are passed to the backoff decorators

def get_backoff_max_value():
    return backoff_max_value

def get_backoff_max_tries():
    return backoff_max_tries
