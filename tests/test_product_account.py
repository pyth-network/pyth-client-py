import mock
import base64
import pytest
from typing import Callable, Optional, Tuple

import pythclient.pythaccounts
from pythclient.exceptions import NotLoadedException
from pythclient.solana import SolanaPublicKey, SolanaClient
from pythclient.pythaccounts import (
    _VERSION_2,
    PythProductAccount,
    _read_attribute_string,
)


@pytest.fixture
def product_account_bytes() -> bytes:
    # Manually split up base64 encoded str for readability
    return base64.b64decode((
        b'PdK2NoakUOxykN86HgtYPASB9lE1Ht+nY285rtVc+KMKYXNzZXRfdHlwZQZDcnlw'
        b'dG8Gc3ltYm9sB0JDSC9VU0QHY291bnRyeQJVUw5xdW90ZV9jdXJyZW5jeQNVU0QL'
        b'ZGVzY3JpcHRpb24HQkNIL1VTRAV0ZW5vcgRTcG90DmdlbmVyaWNfc3ltYm9sBkJDSFVTRA=='
    ))


@pytest.fixture
def product_account(solana_client: SolanaClient):
    product_account = PythProductAccount(
        key=SolanaPublicKey("5uKdRzB3FzdmwyCHrqSGq4u2URja617jqtKkM71BVrkw"),
        solana=solana_client,
    )
    product_account.attrs = {
        "asset_type": "Crypto",
        "symbol": "BCH/USD",
        "country": "US",
        "quote_currency": "USD",
        "description": "BCH/USD",
        "tenor": "Spot",
        "generic_symbol": "BCHUSD",
    }
    product_account.first_price_account_key = SolanaPublicKey(
        "5ALDzwcRJfSyGdGyhP3kP628aqBNHZzLuVww7o9kdspe",
    )
    return product_account


def test_product_account_update_from(
    product_account: PythProductAccount, product_account_bytes: bytes, solana_client: SolanaClient
):
    actual = PythProductAccount(
        key=product_account.key,
        solana=solana_client,
    )
    assert actual.attrs == {}

    actual.update_from(buffer=product_account_bytes, version=_VERSION_2)

    assert dict(actual) == dict(product_account)


def test_update_from_null_first_price_account_key(
    product_account: PythProductAccount, product_account_bytes: bytes, solana_client: SolanaClient
):
    actual = PythProductAccount(
        key=product_account.key,
        solana=solana_client,
    )
    product_account.first_price_account_key = None

    # Zero out the first price account key
    bad_bytes = (
        bytes(b"\x00" * SolanaPublicKey.LENGTH)
        + product_account_bytes[SolanaPublicKey.LENGTH:]
    )

    actual.update_from(buffer=bad_bytes, version=_VERSION_2)

    assert dict(actual) == dict(product_account)


def test_product_account_update_from_invalid_attr_key(
    product_account: PythProductAccount, product_account_bytes: bytes, solana_client: SolanaClient
):
    actual = PythProductAccount(
        key=product_account.key,
        solana=solana_client,
    )

    def fake_read_attribute_string(buffer: bytes, offset: int) -> Tuple[Optional[str], str]:
        results = _read_attribute_string(buffer, offset)
        if results[0] == "generic_symbol":
            return (None, results[1])
        return results

    with mock.patch.object(pythclient.pythaccounts, "_read_attribute_string") as mocked:
        mocked.side_effect = fake_read_attribute_string

        # Call PythProductAccount.update_from()
        actual.update_from(buffer=product_account_bytes, version=_VERSION_2)

    del product_account.attrs["generic_symbol"]

    assert dict(actual) == dict(product_account)


@pytest.mark.parametrize("func", [str, repr])
def test_human_readable(func: Callable, product_account: PythProductAccount):
    expected = (
        "PythProductAccount BCH/USD (5uKdRzB3FzdmwyCHrqSGq4u2URja617jqtKkM71BVrkw)"
    )
    assert func(product_account) == expected


def test_prices_property_not_loaded(product_account: PythProductAccount):
    with pytest.raises(NotLoadedException):
        product_account.prices


def test_symbol_property(product_account):
    assert product_account.symbol == "BCH/USD"


def test_symbol_property_unknown(product_account: PythProductAccount, solana_client: SolanaClient):
    actual = PythProductAccount(
        key=product_account.key,
        solana=solana_client,
    )
    assert actual.symbol == "Unknown"
