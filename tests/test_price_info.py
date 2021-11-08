import pytest
from pythclient.pythaccounts import PythPriceStatus, PythPriceInfo


@pytest.fixture
def price_info_trading():
    return PythPriceInfo(
        raw_price=59609162000,
        raw_confidence_interval=43078500,
        price_status=PythPriceStatus.TRADING,
        slot=105367617,
        exponent=-8,
    )


@pytest.fixture
def price_info_trading_bytes():
    return bytes([
            16, 161, 251, 224, 13, 0, 0, 0, 100, 83, 145, 2, 0, 0,
            0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 65, 200, 71, 6, 0, 0, 0, 0,
    ])


@pytest.mark.parametrize(
    "raw_price,raw_confidence_interval,price_status,slot,exponent,price,confidence_interval",
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
)
class TestPythPriceInfo:
    def test_price_info(
        self,
        raw_price,
        raw_confidence_interval,
        price_status,
        slot,
        exponent,
        price,
        confidence_interval,
    ):
        actual = PythPriceInfo(
            raw_price=raw_price,
            raw_confidence_interval=raw_confidence_interval,
            price_status=price_status,
            slot=slot,
            exponent=exponent,
        )
        for key, actual_value in dict(actual).items():
            assert actual_value == locals().get(key), f"'{key}' mismatch"

    def test_price_info_iter(
        self,
        raw_price,
        raw_confidence_interval,
        price_status,
        slot,
        exponent,
        price,
        confidence_interval,
    ):
        actual = dict(
            PythPriceInfo(
                raw_price=raw_price,
                raw_confidence_interval=raw_confidence_interval,
                price_status=price_status,
                slot=slot,
                exponent=exponent,
            )
        )
        expected = {
            "raw_price": raw_price,
            "raw_confidence_interval": raw_confidence_interval,
            "price_status": price_status,
            "slot": slot,
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
    assert dict(actual) == dict(price_info_trading)


def test_price_info_str(price_info_trading):
    expected = "PythPriceInfo status PythPriceStatus.TRADING price 596.09162"
    assert str(price_info_trading) == expected
    assert repr(price_info_trading) == expected
