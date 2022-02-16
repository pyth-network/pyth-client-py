import pytest
import base64
from pythclient.pythaccounts import PythPriceStatus, PythPriceInfo
from dataclasses import asdict


@pytest.fixture
def price_info_trading():
    return PythPriceInfo(
        raw_price=59609162000,
        raw_confidence_interval=43078500,
        price_status=PythPriceStatus.TRADING,
        pub_slot=105367617,
        exponent=-8,
    )


@pytest.fixture
def price_info_trading_bytes():
    return base64.b64decode(b'EKH74A0AAABkU5ECAAAAAAEAAAAAAAAAQchHBgAAAAA=')


@pytest.mark.parametrize(
    "raw_price,raw_confidence_interval,price_status,pub_slot,exponent,price,confidence_interval",
    [
        (
            1234567890,
            3.0,
            PythPriceStatus.TRADING,
            12345,
            -8,
            12.345678900000001,
            3.0000000000000004e-08,
        ),
        (0, 0, PythPriceStatus.UNKNOWN, 100001, -9, 0.0, 0.0),
    ],
    ids=["price_status_trading", "price_status_unknown"],
)
class TestPythPriceInfo:
    def test_price_info(
        self,
        raw_price,
        raw_confidence_interval,
        price_status,
        pub_slot,
        exponent,
        price,
        confidence_interval,
    ):
        actual = PythPriceInfo(
            raw_price=raw_price,
            raw_confidence_interval=raw_confidence_interval,
            price_status=price_status,
            pub_slot=pub_slot,
            exponent=exponent,
        )
        for key, actual_value in asdict(actual).items():
            assert actual_value == locals().get(key), f"'{key}' mismatch"

    def test_price_info_iter(
        self,
        raw_price,
        raw_confidence_interval,
        price_status,
        pub_slot,
        exponent,
        price,
        confidence_interval,
    ):
        actual = asdict(
            PythPriceInfo(
                raw_price=raw_price,
                raw_confidence_interval=raw_confidence_interval,
                price_status=price_status,
                pub_slot=pub_slot,
                exponent=exponent,
            )
        )
        expected = {
            "raw_price": raw_price,
            "raw_confidence_interval": raw_confidence_interval,
            "price_status": price_status,
            "pub_slot": pub_slot,
            "exponent": exponent,
            "price": price,
            "confidence_interval": confidence_interval,
        }
        assert actual == expected


def test_price_info_deserialise(price_info_trading, price_info_trading_bytes):
    actual = PythPriceInfo.deserialise(
        buffer=price_info_trading_bytes,
        offset=0,
        exponent=price_info_trading.exponent,
    )
    assert asdict(actual) == asdict(price_info_trading)


def test_price_info_str(price_info_trading):
    expected = "PythPriceInfo status PythPriceStatus.TRADING price 596.09162"
    assert str(price_info_trading) == expected
    assert repr(price_info_trading) == expected
