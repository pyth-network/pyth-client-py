import datetime
from zoneinfo import ZoneInfo

import pytest

from pythclient.calendar import (
    get_next_market_close,
    get_next_market_open,
    is_market_open,
)

NY_TZ = ZoneInfo("America/New_York")
UTC_TZ = ZoneInfo("UTC")


@pytest.fixture
def equity_open_weekday_datetime():
    # A weekday, within equity market hours
    return datetime.datetime(2023, 6, 21, 12, 0, 0, tzinfo=NY_TZ)


@pytest.fixture
def equity_close_weekday_datetime():
    # A weekday, out of equity market hours
    return datetime.datetime(2023, 6, 21, 17, 0, 0, tzinfo=NY_TZ)


@pytest.fixture
def equity_close_weekend_datetime():
    # A weekend, out of equity market hours
    return datetime.datetime(2023, 6, 10, 17, 0, 0, tzinfo=NY_TZ)


@pytest.fixture
def equity_holiday_datetime():
    # A weekday, NYSE holiday
    return datetime.datetime(2023, 6, 19, tzinfo=NY_TZ)


@pytest.fixture
def equity_early_holiday_open_datetime():
    # A weekday, NYSE early close holiday
    return datetime.datetime(2023, 11, 24, 11, 0, 0, tzinfo=NY_TZ)


@pytest.fixture
def equity_early_holiday_close_datetime():
    # A weekday, NYSE early close holiday
    return datetime.datetime(2023, 11, 24, 14, 0, 0, tzinfo=NY_TZ)


@pytest.fixture
def fx_metal_open_weekday_datetime():
    # A weekday, within fx & metal market hours
    return datetime.datetime(2023, 6, 21, 22, 0, 0, tzinfo=NY_TZ)


@pytest.fixture
def fx_metal_close_weekend_datetime():
    # A weekend, out of fx & metal market hours
    return datetime.datetime(2023, 6, 18, 16, 0, 0, tzinfo=NY_TZ)


@pytest.fixture
def fx_metal_holiday_datetime():
    # CBOE holiday
    return datetime.datetime(2023, 1, 1, tzinfo=NY_TZ)


@pytest.fixture
def crypto_open_weekday_datetime():
    return datetime.datetime(2023, 6, 21, 12, 0, 0, tzinfo=NY_TZ)


@pytest.fixture
def crypto_open_weekend_datetime():
    return datetime.datetime(2023, 6, 18, 12, 0, 0, tzinfo=NY_TZ)


def test_is_market_open(
    equity_open_weekday_datetime,
    equity_close_weekday_datetime,
    equity_close_weekend_datetime,
    equity_holiday_datetime,
    equity_early_holiday_open_datetime,
    equity_early_holiday_close_datetime,
    fx_metal_open_weekday_datetime,
    fx_metal_close_weekend_datetime,
    fx_metal_holiday_datetime,
    crypto_open_weekday_datetime,
    crypto_open_weekend_datetime,
):
    # equity
    # weekday, within equity market hours
    assert is_market_open("equity", equity_open_weekday_datetime) == True

    # weekday, out of equity market hours
    assert is_market_open("equity", equity_close_weekday_datetime) == False

    # weekend, out of equity market hours
    assert is_market_open("equity", equity_close_weekend_datetime) == False

    # weekday, NYSE holiday
    assert is_market_open("equity", equity_holiday_datetime) == False

    # weekday, NYSE early close holiday
    assert is_market_open("equity", equity_early_holiday_open_datetime) == True
    assert is_market_open("equity", equity_early_holiday_close_datetime) == False

    # fx & metal
    # weekday, within fx & metal market hours
    assert is_market_open("fx", fx_metal_open_weekday_datetime) == True
    assert is_market_open("metal", fx_metal_open_weekday_datetime) == True

    # weekday, out of fx & metal market hours
    assert is_market_open("fx", fx_metal_close_weekend_datetime) == False
    assert is_market_open("metal", fx_metal_close_weekend_datetime) == False

    # fx & metal holiday
    assert is_market_open("fx", fx_metal_holiday_datetime) == False
    assert is_market_open("metal", fx_metal_holiday_datetime) == False

    # crypto
    assert is_market_open("crypto", crypto_open_weekday_datetime) == True
    assert is_market_open("crypto", crypto_open_weekend_datetime) == True


def test_get_next_market_open(
    equity_open_weekday_datetime,
    equity_close_weekday_datetime,
    equity_close_weekend_datetime,
    equity_holiday_datetime,
    equity_early_holiday_open_datetime,
    equity_early_holiday_close_datetime,
    fx_metal_open_weekday_datetime,
    fx_metal_close_weekend_datetime,
    fx_metal_holiday_datetime,
    crypto_open_weekday_datetime,
    crypto_open_weekend_datetime,
):
    # equity within market hours
    assert (
        get_next_market_open("equity", equity_open_weekday_datetime)
        == datetime.datetime(2023, 6, 22, 9, 30, 0, tzinfo=NY_TZ)
        .astimezone(UTC_TZ)
        .strftime("%Y-%m-%dT%H:%M:%S")
        + "Z"
    )

    # equity out of market hours
    assert (
        get_next_market_open("equity", equity_close_weekday_datetime)
        == datetime.datetime(2023, 6, 22, 9, 30, 0, tzinfo=NY_TZ)
        .astimezone(UTC_TZ)
        .strftime("%Y-%m-%dT%H:%M:%S")
        + "Z"
    )

    # equity weekend
    assert (
        get_next_market_open("equity", equity_close_weekend_datetime)
        == datetime.datetime(2023, 6, 12, 9, 30, 0, tzinfo=NY_TZ)
        .astimezone(UTC_TZ)
        .strftime("%Y-%m-%dT%H:%M:%S")
        + "Z"
    )

    # equity holiday
    assert (
        get_next_market_open("equity", equity_holiday_datetime)
        == datetime.datetime(2023, 6, 20, 9, 30, 0, tzinfo=NY_TZ)
        .astimezone(UTC_TZ)
        .strftime("%Y-%m-%dT%H:%M:%S")
        + "Z"
    )

    # equity early close holiday
    assert (
        get_next_market_open("equity", equity_early_holiday_open_datetime)
        == datetime.datetime(2023, 11, 27, 9, 30, 0, tzinfo=NY_TZ)
        .astimezone(UTC_TZ)
        .strftime("%Y-%m-%dT%H:%M:%S")
        + "Z"
    )
    assert (
        get_next_market_open("equity", equity_early_holiday_close_datetime)
        == datetime.datetime(2023, 11, 27, 9, 30, 0, tzinfo=NY_TZ)
        .astimezone(UTC_TZ)
        .strftime("%Y-%m-%dT%H:%M:%S")
        + "Z"
    )

    # fx & metal within market hours
    assert (
        get_next_market_open("fx", fx_metal_open_weekday_datetime)
        == datetime.datetime(2023, 6, 25, 17, 0, 0, tzinfo=NY_TZ)
        .astimezone(UTC_TZ)
        .strftime("%Y-%m-%dT%H:%M:%S")
        + "Z"
    )
    assert (
        get_next_market_open("metal", fx_metal_open_weekday_datetime)
        == datetime.datetime(2023, 6, 25, 17, 0, 0, tzinfo=NY_TZ)
        .astimezone(UTC_TZ)
        .strftime("%Y-%m-%dT%H:%M:%S")
        + "Z"
    )

    # fx & metal out of market hours
    assert (
        get_next_market_open("fx", fx_metal_close_weekend_datetime)
        == datetime.datetime(2023, 6, 18, 17, 0, 0, tzinfo=NY_TZ)
        .astimezone(UTC_TZ)
        .strftime("%Y-%m-%dT%H:%M:%S")
        + "Z"
    )
    assert (
        get_next_market_open("metal", fx_metal_close_weekend_datetime)
        == datetime.datetime(2023, 6, 18, 17, 0, 0, tzinfo=NY_TZ)
        .astimezone(UTC_TZ)
        .strftime("%Y-%m-%dT%H:%M:%S")
        + "Z"
    )

    # fx & metal holiday
    assert (
        get_next_market_open("fx", fx_metal_holiday_datetime)
        == datetime.datetime(2023, 1, 2, 17, 0, 0, tzinfo=NY_TZ)
        .astimezone(UTC_TZ)
        .strftime("%Y-%m-%dT%H:%M:%S")
        + "Z"
    )
    assert (
        get_next_market_open("metal", fx_metal_holiday_datetime)
        == datetime.datetime(2023, 1, 2, 17, 0, 0, tzinfo=NY_TZ)
        .astimezone(UTC_TZ)
        .strftime("%Y-%m-%dT%H:%M:%S")
        + "Z"
    )

    # crypto
    assert get_next_market_open("crypto", crypto_open_weekday_datetime) == None
    assert get_next_market_open("crypto", crypto_open_weekend_datetime) == None


def test_get_next_market_close(
    equity_open_weekday_datetime,
    equity_close_weekday_datetime,
    equity_close_weekend_datetime,
    equity_holiday_datetime,
    equity_early_holiday_open_datetime,
    equity_early_holiday_close_datetime,
    fx_metal_open_weekday_datetime,
    fx_metal_close_weekend_datetime,
    fx_metal_holiday_datetime,
    crypto_open_weekday_datetime,
    crypto_open_weekend_datetime,
):
    # equity within market hours
    assert (
        get_next_market_close("equity", equity_open_weekday_datetime)
        == datetime.datetime(2023, 6, 21, 16, 0, 0, tzinfo=NY_TZ)
        .astimezone(UTC_TZ)
        .strftime("%Y-%m-%dT%H:%M:%S")
        + "Z"
    )

    # equity out of market hours
    assert (
        get_next_market_close("equity", equity_close_weekday_datetime)
        == datetime.datetime(2023, 6, 22, 16, 0, 0, tzinfo=NY_TZ)
        .astimezone(UTC_TZ)
        .strftime("%Y-%m-%dT%H:%M:%S")
        + "Z"
    )

    # equity weekend
    assert (
        get_next_market_close("equity", equity_close_weekend_datetime)
        == datetime.datetime(2023, 6, 12, 16, 0, 0, tzinfo=NY_TZ)
        .astimezone(UTC_TZ)
        .strftime("%Y-%m-%dT%H:%M:%S")
        + "Z"
    )

    # equity holiday
    assert (
        get_next_market_close("equity", equity_holiday_datetime)
        == datetime.datetime(2023, 6, 20, 16, 0, 0, tzinfo=NY_TZ)
        .astimezone(UTC_TZ)
        .strftime("%Y-%m-%dT%H:%M:%S")
        + "Z"
    )

    # equity early close holiday
    assert (
        get_next_market_close("equity", equity_early_holiday_open_datetime)
        == datetime.datetime(2023, 11, 24, 13, 0, 0, tzinfo=NY_TZ)
        .astimezone(UTC_TZ)
        .strftime("%Y-%m-%dT%H:%M:%S")
        + "Z"
    )
    assert (
        get_next_market_close("equity", equity_early_holiday_close_datetime)
        == datetime.datetime(2023, 11, 27, 16, 0, 0, tzinfo=NY_TZ)
        .astimezone(UTC_TZ)
        .strftime("%Y-%m-%dT%H:%M:%S")
        + "Z"
    )

    # fx & metal within market hours
    assert (
        get_next_market_close("fx", fx_metal_open_weekday_datetime)
        == datetime.datetime(2023, 6, 23, 17, 0, 0, tzinfo=NY_TZ)
        .astimezone(UTC_TZ)
        .strftime("%Y-%m-%dT%H:%M:%S")
        + "Z"
    )
    assert (
        get_next_market_close("metal", fx_metal_open_weekday_datetime)
        == datetime.datetime(2023, 6, 23, 17, 0, 0, tzinfo=NY_TZ)
        .astimezone(UTC_TZ)
        .strftime("%Y-%m-%dT%H:%M:%S")
        + "Z"
    )

    # fx & metal out of market hours
    assert (
        get_next_market_close("fx", fx_metal_close_weekend_datetime)
        == datetime.datetime(2023, 6, 23, 17, 0, 0, tzinfo=NY_TZ)
        .astimezone(UTC_TZ)
        .strftime("%Y-%m-%dT%H:%M:%S")
        + "Z"
    )
    assert (
        get_next_market_close("metal", fx_metal_close_weekend_datetime)
        == datetime.datetime(2023, 6, 23, 17, 0, 0, tzinfo=NY_TZ)
        .astimezone(UTC_TZ)
        .strftime("%Y-%m-%dT%H:%M:%S")
        + "Z"
    )

    # fx & metal holiday
    assert (
        get_next_market_close("fx", fx_metal_holiday_datetime)
        == datetime.datetime(2023, 1, 6, 17, 0, 0, tzinfo=NY_TZ)
        .astimezone(UTC_TZ)
        .strftime("%Y-%m-%dT%H:%M:%S")
        + "Z"
    )
    assert (
        get_next_market_close("metal", fx_metal_holiday_datetime)
        == datetime.datetime(2023, 1, 6, 17, 0, 0, tzinfo=NY_TZ)
        .astimezone(UTC_TZ)
        .strftime("%Y-%m-%dT%H:%M:%S")
        + "Z"
    )

    # crypto
    assert get_next_market_close("crypto", crypto_open_weekday_datetime) == None
    assert get_next_market_close("crypto", crypto_open_weekend_datetime) == None
