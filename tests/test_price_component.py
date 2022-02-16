import pytest
import base64

from pythclient.solana import SolanaPublicKey
from pythclient.pythaccounts import PythPriceComponent, PythPriceInfo, PythPriceStatus


@pytest.fixture
def price_component_bytes() -> bytes:
    return base64.b64decode((
        b'92Z9u4180xchiUFKI8JrUh2MGcZFBFVV4+KOglaOZXjgewKnDgAAACDF+wAAAAAA'
        b'AQAAAAAAAADTsU8GAAAAAOB7AqcOAAAAIMX7AAAAAAABAAAAAAAAANSxTwYAAAAA'
    ))


@pytest.fixture
def price_component() -> PythPriceComponent:
    exponent = -8
    publisher_key = SolanaPublicKey("HekM1hBawXQu6wK6Ah1yw1YXXeMUDD2bfCHEzo25vnEB")
    last_aggregate_price = PythPriceInfo(**{
        'raw_price': 62931500000,
        'raw_confidence_interval': 16500000,
        'price_status': PythPriceStatus.TRADING,
        'pub_slot': 105886163,
        'exponent': exponent,
    })
    latest_price = PythPriceInfo(**{
        'raw_price': 62931500000,
        'raw_confidence_interval': 16500000,
        'price_status': PythPriceStatus.TRADING,
        'pub_slot': 105886164,
        'exponent': exponent,
    })
    return PythPriceComponent(
        publisher_key,
        last_aggregate_price_info=last_aggregate_price,
        latest_price_info=latest_price,
        exponent=exponent,
    )


def test_valid_deserialise(price_component: PythPriceComponent, price_component_bytes: bytes):
    actual = PythPriceComponent.deserialise(price_component_bytes, exponent=price_component.exponent)

    # To make pyright happy
    assert actual is not None

    # Make the actual assertions
    assert actual == price_component


def test_deserialise_null_publisher_key(price_component: PythPriceComponent, price_component_bytes: bytes):
    # Zero out the solana key (the first 32 bytes of the buffer)
    bad_bytes = bytes(b'\x00' * SolanaPublicKey.LENGTH) + price_component_bytes[SolanaPublicKey.LENGTH:]
    actual = PythPriceComponent.deserialise(bad_bytes, exponent=price_component.exponent)
    assert actual is None
