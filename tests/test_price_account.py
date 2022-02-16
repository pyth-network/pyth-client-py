import pytest
import base64
from dataclasses import asdict

from pythclient.pythaccounts import (
    MAX_SLOT_DIFFERENCE,
    PythPriceAccount,
    PythPriceType,
    PythPriceStatus,
    PythProductAccount,
)
from pythclient.solana import SolanaPublicKey, SolanaClient


# Yes, this sucks, but it is actually a monster datastructure (2K)
@pytest.fixture
def price_account_bytes():
    return base64.b64decode((
        b'AQAAAPj///8TAAAAEAAAANupUgYAAAAA2qlSBgAAAAB4XGx3EAAAAJ86jskAAAAA3CH+HAEA'
        b'AAD6ORUDAAAAABzzZ5MAAAAA3CH+HAEAAAABAAAAAAAAAAAAAAAAAAAASNYDPXM+J5UMLgNR'
        b'4lBUkc2RVIJPcW2VE1FMdLn5j1gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANmp'
        b'UgYAAAAAIB/LdhAAAADEKi0CAAAAAAAAAAAAAAAAIB/LdhAAAADk7y4CAAAAAAEAAAAAAAAA'
        b'26lSBgAAAAD3Zn27jXzTFyGJQUojwmtSHYwZxkUEVVXj4o6CVo5leGBYnXYQAAAAYBBIAQAA'
        b'AAABAAAAAAAAANipUgYAAAAAYFiddhAAAABgEEgBAAAAAAEAAAAAAAAA2alSBgAAAAAWD7rB'
        b'Ovfd2AXTFwo94Ma9lxJqHgLA0lnQqG74IdblxyAfy3YQAAAACyXuAAAAAAABAAAAAAAAANip'
        b'UgYAAAAAIB/LdhAAAAALJe4AAAAAAAEAAAAAAAAA2alSBgAAAAAF0gZPMxz/3cq+lvo2VSTd'
        b'ZPSzhuiFo00VLL6uBCzq9cgcPHEQAAAAVAF9BAAAAAABAAAAAAAAANmpUgYAAAAAyBw8cRAA'
        b'AABUAX0EAAAAAAEAAAAAAAAA2qlSBgAAAADiuY8mkITUiAURyBFdzvBPU8fiB5kuA//RJt+U'
        b'TeTbBEB4h9UNAAAAQFSJAAAAAAABAAAAAAAAANfOOgYAAAAAQHiH1Q0AAABAVIkAAAAAAAEA'
        b'AAAAAAAA1846BgAAAAAa5QKj6UK4sRzDdElrTZxcOfgMXawfRZ81og7BuHMIndC7Q3UQAAAA'
        b'cNddAAAAAAABAAAAAAAAANipUgYAAAAA0LtDdRAAAABw110AAAAAAAEAAAAAAAAA2alSBgAA'
        b'AAANw7zqkVVpdgiwXwSnCtCaQVFyqpu190CHOsB4KysaRYA0/X4QAAAA6PWmKgAAAAABAAAA'
        b'AAAAANipUgYAAAAAgDT9fhAAAADo9aYqAAAAAAEAAAAAAAAA2alSBgAAAAAH8ss5/bAp3FF4'
        b'TSjvF5Edl8GmnIVyOhtiVbNCU0OtdaDilHgQAAAAQHh9AQAAAAABAAAAAAAAANmpUgYAAAAA'
        b'oOKUeBAAAABAeH0BAAAAAAEAAAAAAAAA2qlSBgAAAACfPqV71Am6AMQNkq5XE0HCfjwvft+s'
        b'4cJKUbGhXDGytwB+w3YQAAAAAJDQAwAAAAABAAAAAAAAANapUgYAAAAAAH7DdhAAAAAAkNAD'
        b'AAAAAAEAAAAAAAAA1qlSBgAAAABDgo+jYZ2mvK7WiRfeHXzOkhfexyuuEjBj/3vn3S+WPp+1'
        b'Y3cQAAAAIND8AwAAAAABAAAAAAAAANipUgYAAAAAn7VjdxAAAADQDPwDAAAAAAEAAAAAAAAA'
        b'2alSBgAAAAAYg7EkbdpdBxc9vTjVZwAHFYQsH9DolucLCm3S5RpPl5CJPXoQAAAAoH4mAQAA'
        b'AAABAAAAAAAAANSpUgYAAAAAkIk9ehAAAACgfiYBAAAAAAEAAAAAAAAA1KlSBgAAAABDt3hL'
        b'b4VmyzKDZfvOC0BGFSO67OeFF7MVXDHaozgpj6CarHYQAAAA4MrUAgAAAAABAAAAAAAAANip'
        b'UgYAAAAAoJqsdhAAAADgytQCAAAAAAEAAAAAAAAA2alSBgAAAAD1nd3vzBZrLYmko8zz/sS7'
        b'S5ihUbTAN/9hXrt4QuM9dQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        b'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACp6tPj00vMhTS7LGUOsnqMjD8aItaIKEMoU4xC'
        b'qOgjQwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        b'AAAAAAAAAAAAAAAAAADQyjMc9dnucWvIxpCjAKuoQDs3FBy2OwJlwJjAxY5jrEDJD3cQAAAA'
        b'iO90AgAAAAABAAAAAAAAANipUgYAAAAAQMkPdxAAAACI73QCAAAAAAEAAAAAAAAA2alSBgAA'
        b'AABfyWT+IQLDTV2m/OVBHX+euZaDX9doeSPt8Afh6snTmyAfy3YQAAAA8MjSAAAAAAABAAAA'
        b'AAAAANipUgYAAAAAIB/LdhAAAADwyNIAAAAAAAEAAAAAAAAA2alSBgAAAADshtw0V/2qFXMo'
        b'0kCdNAHTz61GgIqwRBk8Hn7J+tXPYra163kQAAAAmhIJAwAAAAABAAAAAAAAANipUgYAAAAA'
        b'trXreRAAAACaEgkDAAAAAAEAAAAAAAAA2alSBgAAAADYb4QN6+LtpmaFm/jCx0LD5ke+Thdt'
        b'/FIl2ATx1J/iLU9xK3YQAAAAUQDeAQAAAAABAAAAAAAAANipUgYAAAAAT3ErdhAAAABRAN4B'
        b'AAAAAAEAAAAAAAAA2alSBgAAAAD3oTB6i0MnB/D217PntQNBRQJinx7o+cT2tZFViRokLtlj'
        b'UXkQAAAAhB8gAgAAAAABAAAAAAAAANipUgYAAAAA2WNReRAAAACEHyACAAAAAAEAAAAAAAAA'
        b'2alSBgAAAAAQObH1+gS8Ag0HeG1UdQRs2fQLBW50YN8kJo4QAHwOnZ+DNHgQAAAAYe1IAgAA'
        b'AAABAAAAAAAAANipUgYAAAAAn4M0eBAAAABh7UgCAAAAAAEAAAAAAAAA2alSBgAAAAA='
    ))

@pytest.fixture
def price_account(solana_client: SolanaClient) -> PythPriceAccount:
    return PythPriceAccount(
        key=SolanaPublicKey("5ALDzwcRJfSyGdGyhP3kP628aqBNHZzLuVww7o9kdspe"),
        solana=solana_client,
    )

def test_price_account_update_from(price_account_bytes: bytes, price_account: PythPriceAccount):
    price_account.update_from(buffer=price_account_bytes, version=2, offset=0)

    assert price_account.price_type == PythPriceType.PRICE
    assert price_account.exponent == -8
    assert price_account.num_components == 19
    assert len(price_account.price_components) == price_account.num_components
    assert price_account.last_slot == 106080731
    assert price_account.valid_slot == 106080730
    assert price_account.product_account_key == SolanaPublicKey(
        "5uKdRzB3FzdmwyCHrqSGq4u2URja617jqtKkM71BVrkw"
    )
    assert price_account.next_price_account_key is None
    assert asdict(price_account.aggregate_price_info) == {
        "raw_price": 70712500000,
        "raw_confidence_interval": 36630500,
        "price_status": PythPriceStatus.TRADING,
        "pub_slot": 106080731,
        "exponent": -8,
        "price": 707.125,
        "confidence_interval": 0.366305,
    }
    # Only assert the first element of the 19 price components
    assert asdict(price_account.price_components[0]) == {
        "publisher_key": SolanaPublicKey(
            "HekM1hBawXQu6wK6Ah1yw1YXXeMUDD2bfCHEzo25vnEB"
        ),
        "last_aggregate_price_info": {
            "raw_price": 70709500000,
            "raw_confidence_interval": 21500000,
            "price_status": PythPriceStatus.TRADING,
            "pub_slot": 106080728,
            "exponent": -8,
            "price": 707.095,
            "confidence_interval": 0.215,
        },
        "latest_price_info": {
            "raw_price": 70709500000,
            "raw_confidence_interval": 21500000,
            "price_status": PythPriceStatus.TRADING,
            "pub_slot": 106080729,
            "exponent": -8,
            "price": 707.095,
            "confidence_interval": 0.215,
        },
        "exponent": -8,
    }
    assert price_account.min_publishers == 0


def test_price_account_str(
        price_account_bytes: bytes, price_account: PythPriceAccount, solana_client: SolanaClient,
):
    expected_empty = "PythPriceAccount PythPriceType.UNKNOWN (5ALDzwcRJfSyGdGyhP3kP628aqBNHZzLuVww7o9kdspe)"
    assert str(price_account) == expected_empty

    expected = "PythPriceAccount PythPriceType.PRICE (5ALDzwcRJfSyGdGyhP3kP628aqBNHZzLuVww7o9kdspe)"
    price_account.update_from(buffer=price_account_bytes, version=2, offset=0)
    assert str(price_account) == expected

    price_account.product = PythProductAccount(
        key=SolanaPublicKey("5uKdRzB3FzdmwyCHrqSGq4u2URja617jqtKkM71BVrkw"),
        solana=solana_client,
    )
    price_account.product.attrs = {
        "symbol": "FOO/BAR",
    }
    expected_with_product = (
        "PythPriceAccount FOO/BAR PythPriceType.PRICE (5ALDzwcRJfSyGdGyhP3kP628aqBNHZzLuVww7o9kdspe)"
    )
    assert str(price_account) == expected_with_product


def test_price_account_agregate_conf_interval(
    price_account_bytes: bytes, price_account: PythPriceAccount,
):
    price_account.update_from(buffer=price_account_bytes, version=2, offset=0)
    price_account.slot = price_account.aggregate_price_info.pub_slot
    assert price_account.aggregate_price_confidence_interval == 0.366305


def test_price_account_agregate_price(
    price_account_bytes: bytes, price_account: PythPriceAccount,
):
    price_account.update_from(buffer=price_account_bytes, version=2, offset=0)
    price_account.slot = price_account.aggregate_price_info.pub_slot
    assert price_account.aggregate_price == 707.125

def test_price_account_unknown_status(
    price_account_bytes: bytes, price_account: PythPriceAccount,
):
    price_account.update_from(buffer=price_account_bytes, version=2, offset=0)
    price_account.slot = price_account.aggregate_price_info.pub_slot
    price_account.aggregate_price_info.price_status = PythPriceStatus.UNKNOWN

    assert price_account.aggregate_price is None
    assert price_account.aggregate_price_confidence_interval is None

def test_price_account_get_aggregate_price_status_still_trading(
    price_account_bytes: bytes, price_account: PythPriceAccount
):
    price_account.update_from(buffer=price_account_bytes, version=2, offset=0)
    price_account.slot = price_account.aggregate_price_info.pub_slot + MAX_SLOT_DIFFERENCE

    price_status = price_account.aggregate_price_status
    assert price_status == PythPriceStatus.TRADING

def test_price_account_get_aggregate_price_status_got_stale(
    price_account_bytes: bytes, price_account: PythPriceAccount
):
    price_account.update_from(buffer=price_account_bytes, version=2, offset=0)
    price_account.slot = price_account.aggregate_price_info.pub_slot + MAX_SLOT_DIFFERENCE + 1

    price_status = price_account.aggregate_price_status
    assert price_status == PythPriceStatus.UNKNOWN
