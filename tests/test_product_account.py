import mock
import pytest

import pythclient.pythaccounts
from pythclient.exceptions import NotLoadedException
from pythclient.solana import SolanaPublicKey, SolanaClient
from pythclient.pythaccounts import (
    _VERSION_2,
    PythPriceAccount,
    PythProductAccount,
    _read_attribute_string,
)


@pytest.fixture
def solana_client():
    return SolanaClient(
        endpoint="https://example.com",
        ws_endpoint="wss://example.com",
    )


@pytest.fixture
def product_account_bytes():
    return bytes(
        [
            61, 210, 182, 54, 134, 164, 80, 236, 114, 144, 223, 58, 30,
            11, 88, 60, 4, 129, 246, 81, 53, 30, 223, 167, 99, 111, 57, 174,
            213, 92, 248, 163, 10, 97, 115, 115, 101, 116, 95, 116, 121,
            112, 101, 6, 67, 114, 121, 112, 116, 111, 6, 115, 121, 109, 98,
            111, 108, 7, 66, 67, 72, 47, 85, 83, 68, 7, 99, 111, 117, 110,
            116, 114, 121, 2, 85, 83, 14, 113, 117, 111, 116, 101, 95, 99,
            117, 114, 114, 101, 110, 99, 121, 3, 85, 83, 68, 11, 100, 101,
            115, 99, 114, 105, 112, 116, 105, 111, 110, 7, 66, 67, 72, 47,
            85, 83, 68, 5, 116, 101, 110, 111, 114, 4, 83, 112, 111, 116,
            14, 103, 101, 110, 101, 114, 105, 99, 95, 115, 121, 109, 98,
            111, 108, 6, 66, 67, 72, 85, 83, 68
        ]
    )


@pytest.fixture
def product_account(solana_client):
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
    product_account, product_account_bytes, solana_client
):
    actual = PythProductAccount(
        key=product_account.key,
        solana=solana_client,
    )
    assert actual.attrs == {}

    actual.update_from(buffer=product_account_bytes, version=_VERSION_2)

    assert dict(actual) == dict(product_account)


def test_update_from_null_first_price_account_key(
    product_account, product_account_bytes, solana_client
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
    product_account, product_account_bytes, solana_client
):
    actual = PythProductAccount(
        key=product_account.key,
        solana=solana_client,
    )

    def fake_read_attribute_string(buffer: bytes, offset: int):
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
def test_human_readable(func, product_account):
    expected = (
        "PythProductAccount BCH/USD (5uKdRzB3FzdmwyCHrqSGq4u2URja617jqtKkM71BVrkw)"
    )
    assert func(product_account) == expected


def test_prices_property_not_loaded(product_account):
    with pytest.raises(NotLoadedException):
        product_account.prices


def test_symbol_property(product_account):
    assert product_account.symbol == "BCH/USD"


def test_symbol_property_unknown(product_account, solana_client):
    actual = PythProductAccount(
        key=product_account.key,
        solana=solana_client,
    )
    assert actual.symbol == "Unknown"
