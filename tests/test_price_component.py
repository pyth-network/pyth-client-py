import pytest

from pythclient.solana import SolanaPublicKey
from pythclient.pythaccounts import PythPriceComponent, PythPriceInfo, PythPriceStatus


@pytest.fixture
def price_component_bytes() -> bytes:
    return bytes(
        [
            247, 102, 125, 187, 141, 124, 211, 23, 33, 137, 65, 74, 35,
            194, 107, 82, 29, 140, 25, 198, 69, 4, 85, 85, 227, 226, 142,
            130, 86, 142, 101, 120, 224, 123, 2, 167, 14, 0, 0, 0, 32, 197,
            251, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 211, 177, 79, 6, 0,
            0, 0, 0, 224, 123, 2, 167, 14, 0, 0, 0, 32, 197, 251, 0, 0, 0,
            0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 212, 177, 79, 6, 0, 0, 0, 0,
        ]
    )


@pytest.fixture
def price_component():
    exponent = -8
    publisher_key = SolanaPublicKey("HekM1hBawXQu6wK6Ah1yw1YXXeMUDD2bfCHEzo25vnEB")
    last_aggregate_price = PythPriceInfo(**{
        'raw_price': 62931500000,
        'raw_confidence_interval': 16500000,
        'price_status': PythPriceStatus.TRADING,
        'slot': 105886163,
        'exponent': exponent,
    })
    latest_price = PythPriceInfo(**{
        'raw_price': 62931500000,
        'raw_confidence_interval': 16500000,
        'price_status': PythPriceStatus.TRADING,
        'slot': 105886164,
        'exponent': exponent,
    })
    return PythPriceComponent(
        publisher_key,
        last_aggregate_price_info=last_aggregate_price,
        latest_price_info=latest_price,
        exponent=exponent,
    )


def test_valid_deserialise(price_component, price_component_bytes):
    actual = PythPriceComponent.deserialise(price_component_bytes, exponent=price_component.exponent)

    # To make pyright happy
    assert actual is not None

    # Make the actual assertions
    assert dict(actual) == dict(price_component)


def test_deserialise_null_publisher_key(price_component, price_component_bytes):
    # Zero out the solana key (the first 32 bytes of the buffer)
    bad_bytes = bytes(b'\x00' * SolanaPublicKey.LENGTH) + price_component_bytes[SolanaPublicKey.LENGTH:]
    actual = PythPriceComponent.deserialise(bad_bytes, exponent=price_component.exponent)
    assert actual is None
