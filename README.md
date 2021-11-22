Pyth Client in Python
=====================

[![pytest](https://github.com/pyth-network/pyth-client-py/actions/workflows/pytest.yml/badge.svg?branch=main)](https://github.com/pyth-network/pyth-client-py/actions/workflows/pytest.yml)

A Python library to retrieve data from Pyth account structures off the Solana blockchain.

**NOTE**: This library requires Python 3.7 or greater due to `from __future__ import annotations`.


Developer Setup
---------------

Using python 3.7 or newer, create, and activate a virtual environment:

    python3 -m venv ve
    . ve/bin/activate

To install this library in editable mode with test dependencies:

    pip install -e '.[testing]'

To run the unit tests:

    pytest

If html based test coverage is more your jam:

    pytest --cov-report=html

The coverage webpages will be in the `htmlcov` directory.
