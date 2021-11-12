Pyth Client in Python
=====================

A Python library to retrieve data from Pyth account structures off the Solana blockchain.

**NOTE**: This library requires Python 3.7 or greater due to `from __future__ import annotations`.


Developer Setup
---------------

To install this library in editable mode with test dependencies:

    pip install -e '.[testing]'

To run the unit tests:

    pytest --cov=pythclient

If html based test coverage is more your jam:

    pytest --cov-report=html --cov=pythclient

The coverage webpages will be in the `htmlcov` directory.
