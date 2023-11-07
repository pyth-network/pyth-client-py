import datetime
from zoneinfo import ZoneInfo

from pythclient.calendar import (get_next_market_close, get_next_market_open,
                                 is_market_open)

NY_TZ = ZoneInfo("America/New_York")
UTC_TZ = ZoneInfo("UTC")

# Define constants for equity market
EQUITY_OPEN_WED_2023_6_21_12 = datetime.datetime(2023, 6, 21, 12, 0, 0, tzinfo=NY_TZ)
EQUITY_CLOSE_WED_2023_6_21_17 = datetime.datetime(2023, 6, 21, 17, 0, 0, tzinfo=NY_TZ)
EQUITY_CLOSE_SAT_2023_6_10_17 = datetime.datetime(2023, 6, 10, 17, 0, 0, tzinfo=NY_TZ)
EQUITY_HOLIDAY_MON_2023_6_19 = datetime.datetime(2023, 6, 19, tzinfo=NY_TZ)
EQUITY_HOLIDAY_NEXT_DAY_EARLY_CLOSE_OPEN_THU_2023_11_23_9_30 = datetime.datetime(2023, 11, 23, 9, 30, 0, tzinfo=NY_TZ)
EQUITY_HOLIDAY_NEXT_DAY_EARLY_CLOSE_CLOSE_THU_2023_11_23_13 = datetime.datetime(2023, 11, 23, 13, 0, 0, tzinfo=NY_TZ)
EQUITY_EARLY_CLOSE_OPEN_FRI_2023_11_24_11 = datetime.datetime(2023, 11, 24, 11, 0, 0, tzinfo=NY_TZ)
EQUITY_EARLY_CLOSE_CLOSE_FRI_2023_11_24_14 = datetime.datetime(2023, 11, 24, 14, 0, 0, tzinfo=NY_TZ)

# Define constants for fx & metal market
FX_METAL_OPEN_WED_2023_6_21_21 = datetime.datetime(2023, 6, 21, 21, 0, 0, tzinfo=NY_TZ)
FX_METAL_OPEN_WED_2023_6_21_23 = datetime.datetime(2023, 6, 21, 23, 0, 0, tzinfo=NY_TZ)
FX_METAL_CLOSE_SUN_2023_6_18_16 = datetime.datetime(2023, 6, 18, 16, 0, 0, tzinfo=NY_TZ)
FX_METAL_HOLIDAY_SUN_2023_1_1 = datetime.datetime(2023, 1, 1, tzinfo=NY_TZ)

# Define constants for rates market
RATES_OPEN_WED_2023_6_21_12 = datetime.datetime(2023, 6, 21, 8, 0, 0, tzinfo=NY_TZ)
RATES_CLOSE_WED_2023_6_21_17 = datetime.datetime(2023, 6, 21, 17, 0, 0, tzinfo=NY_TZ)
RATES_CLOSE_SAT_2023_6_10_17 = datetime.datetime(2023, 6, 10, 17, 0, 0, tzinfo=NY_TZ)
RATES_HOLIDAY_MON_2023_6_19 = datetime.datetime(2023, 6, 19, tzinfo=NY_TZ)
RATES_HOLIDAY_NEXT_DAY_EARLY_CLOSE_OPEN_THU_2023_11_23_8 = datetime.datetime(2023, 11, 23, 8, 0, 0, tzinfo=NY_TZ)
RATES_HOLIDAY_NEXT_DAY_EARLY_CLOSE_CLOSE_THU_2023_11_23_13 = datetime.datetime(2023, 11, 23, 13, 0, 0, tzinfo=NY_TZ)
RATES_EARLY_CLOSE_OPEN_FRI_2023_11_24_11 = datetime.datetime(2023, 11, 24, 11, 0, 0, tzinfo=NY_TZ)
RATES_EARLY_CLOSE_CLOSE_FRI_2023_11_24_14 = datetime.datetime(2023, 11, 24, 14, 0, 0, tzinfo=NY_TZ)

# Define constants for cryptocurrency market
CRYPTO_OPEN_WED_2023_6_21_12 = datetime.datetime(2023, 6, 21, 12, 0, 0, tzinfo=NY_TZ)
CRYPTO_OPEN_SUN_2023_6_18_12 = datetime.datetime(2023, 6, 18, 12, 0, 0, tzinfo=NY_TZ)


def format_datetime_to_unix_timestamp(dt: datetime.datetime):
    # Convert the datetime object to a Unix timestamp in UTC
    timestamp = dt.astimezone(UTC_TZ).timestamp()
    unix_timestamp_utc = int(timestamp)
    return unix_timestamp_utc

def test_is_market_open():
    # equity
    # weekday, within equity market hours
    assert is_market_open("equity", EQUITY_OPEN_WED_2023_6_21_12) == True

    # weekday, out of equity market hours
    assert is_market_open("equity", EQUITY_CLOSE_WED_2023_6_21_17) == False

    # weekend, out of equity market hours
    assert is_market_open("equity", EQUITY_CLOSE_SAT_2023_6_10_17) == False

    # weekday, NYSE holiday
    assert is_market_open("equity", EQUITY_HOLIDAY_MON_2023_6_19) == False

    # weekday, NYSE early close holiday
    assert is_market_open("equity", EQUITY_EARLY_CLOSE_OPEN_FRI_2023_11_24_11) == True
    assert is_market_open("equity", EQUITY_EARLY_CLOSE_CLOSE_FRI_2023_11_24_14) == False

    # fx & metal
    # weekday, within fx & metal market hours
    assert is_market_open("fx", FX_METAL_OPEN_WED_2023_6_21_21) == True
    assert is_market_open("metal", FX_METAL_OPEN_WED_2023_6_21_21) == True

    # weekday, out of fx & metal market hours
    assert is_market_open("fx", FX_METAL_CLOSE_SUN_2023_6_18_16) == False
    assert is_market_open("metal", FX_METAL_CLOSE_SUN_2023_6_18_16) == False

    # fx & metal holiday
    assert is_market_open("fx", FX_METAL_HOLIDAY_SUN_2023_1_1) == False
    assert is_market_open("metal", FX_METAL_HOLIDAY_SUN_2023_1_1) == False

    # rates
    # weekday, within rates market hours
    assert is_market_open("rates", RATES_OPEN_WED_2023_6_21_12) == True

    # weekday, out of rates market hours
    assert is_market_open("rates", RATES_CLOSE_WED_2023_6_21_17) == False

    # weekend, out of rates market hours
    assert is_market_open("rates", RATES_CLOSE_SAT_2023_6_10_17) == False

    # weekday, NYSE holiday
    assert is_market_open("rates", RATES_HOLIDAY_MON_2023_6_19) == False

    # weekday, NYSE early close holiday
    assert is_market_open("rates", RATES_EARLY_CLOSE_OPEN_FRI_2023_11_24_11) == True
    assert is_market_open("rates", RATES_EARLY_CLOSE_CLOSE_FRI_2023_11_24_14) == False

    # crypto
    assert is_market_open("crypto", CRYPTO_OPEN_WED_2023_6_21_12) == True
    assert is_market_open("crypto", CRYPTO_OPEN_SUN_2023_6_18_12) == True


def test_get_next_market_open():
    # equity within market hours
    assert (
        get_next_market_open("equity", EQUITY_OPEN_WED_2023_6_21_12)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 22, 9, 30, 0, tzinfo=NY_TZ))
    )

    # equity out of market hours
    assert (
        get_next_market_open("equity", EQUITY_CLOSE_WED_2023_6_21_17)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 22, 9, 30, 0, tzinfo=NY_TZ))
    )

    # equity weekend
    assert (
        get_next_market_open("equity", EQUITY_CLOSE_SAT_2023_6_10_17)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 12, 9, 30, 0, tzinfo=NY_TZ))
    )

    # equity holiday
    assert (
        get_next_market_open("equity", EQUITY_HOLIDAY_MON_2023_6_19)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 20, 9, 30, 0, tzinfo=NY_TZ))
    )

    # equity holiday next day early close holiday
    assert (
        get_next_market_open("equity", EQUITY_HOLIDAY_NEXT_DAY_EARLY_CLOSE_OPEN_THU_2023_11_23_9_30)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 11, 24, 9, 30, 0, tzinfo=NY_TZ))
    )

    # equity early close holiday
    assert (
        get_next_market_open("equity", EQUITY_EARLY_CLOSE_OPEN_FRI_2023_11_24_11)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 11, 27, 9, 30, 0, tzinfo=NY_TZ))
    )
    assert (
        get_next_market_open("equity", EQUITY_EARLY_CLOSE_CLOSE_FRI_2023_11_24_14)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 11, 27, 9, 30, 0, tzinfo=NY_TZ))
    )

    # fx & metal within market hours (before 10pm UTC)
    assert (
        get_next_market_open("fx", FX_METAL_OPEN_WED_2023_6_21_21)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 25, 17, 0, 0, tzinfo=NY_TZ))
    )
    assert (
        get_next_market_open("metal", FX_METAL_OPEN_WED_2023_6_21_21)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 25, 17, 0, 0, tzinfo=NY_TZ))
    )
    # fx & metal within market hours (after 10pm UTC)
    assert (
        get_next_market_open("fx", FX_METAL_OPEN_WED_2023_6_21_23)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 25, 17, 0, 0, tzinfo=NY_TZ))
    )
    assert (
        get_next_market_open("metal", FX_METAL_OPEN_WED_2023_6_21_23)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 25, 17, 0, 0, tzinfo=NY_TZ))
    )

    # fx & metal out of market hours
    assert (
        get_next_market_open("fx", FX_METAL_CLOSE_SUN_2023_6_18_16)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 18, 17, 0, 0, tzinfo=NY_TZ))
    )
    assert (
        get_next_market_open("metal", FX_METAL_CLOSE_SUN_2023_6_18_16)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 18, 17, 0, 0, tzinfo=NY_TZ))
    )

    # fx & metal holiday
    assert (
        get_next_market_open("fx", FX_METAL_HOLIDAY_SUN_2023_1_1)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 1, 2, 17, 0, 0, tzinfo=NY_TZ))
    )
    assert (
        get_next_market_open("metal", FX_METAL_HOLIDAY_SUN_2023_1_1)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 1, 2, 17, 0, 0, tzinfo=NY_TZ))
    )

    # rates within market hours
    assert (
        get_next_market_open("rates", RATES_OPEN_WED_2023_6_21_12)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 22, 8, 0, 0, tzinfo=NY_TZ))
    )

    # rates out of market hours
    assert (
        get_next_market_open("rates", RATES_CLOSE_WED_2023_6_21_17)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 22, 8, 0, 0, tzinfo=NY_TZ))
    )

    # rates weekend
    assert (
        get_next_market_open("rates", RATES_CLOSE_SAT_2023_6_10_17)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 12, 8, 0, 0, tzinfo=NY_TZ))
    )

    # rates holiday
    assert (
        get_next_market_open("rates", RATES_HOLIDAY_MON_2023_6_19)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 20, 8, 0, 0, tzinfo=NY_TZ))
    )

    # rates holiday next day early close holiday
    assert (
        get_next_market_open("rates", RATES_HOLIDAY_NEXT_DAY_EARLY_CLOSE_OPEN_THU_2023_11_23_8)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 11, 24, 8, 0, 0, tzinfo=NY_TZ))
    )

    # rates early close holiday
    assert (
        get_next_market_open("rates", RATES_EARLY_CLOSE_OPEN_FRI_2023_11_24_11)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 11, 27, 8, 0, 0, tzinfo=NY_TZ))
    )
    assert (
        get_next_market_open("rates", RATES_EARLY_CLOSE_CLOSE_FRI_2023_11_24_14)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 11, 27, 8, 0, 0, tzinfo=NY_TZ))
    )


    # crypto
    assert get_next_market_open("crypto", CRYPTO_OPEN_WED_2023_6_21_12) == None
    assert get_next_market_open("crypto", CRYPTO_OPEN_SUN_2023_6_18_12) == None


def test_get_next_market_close():
    # equity within market hours
    assert (
        get_next_market_close("equity", EQUITY_OPEN_WED_2023_6_21_12)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 21, 16, 0, 0, tzinfo=NY_TZ))
    )

    # equity out of market hours
    assert (
        get_next_market_close("equity", EQUITY_CLOSE_WED_2023_6_21_17)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 22, 16, 0, 0, tzinfo=NY_TZ))
    )

    # equity weekend
    assert (
        get_next_market_close("equity", EQUITY_CLOSE_SAT_2023_6_10_17)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 12, 16, 0, 0, tzinfo=NY_TZ))
    )

    # equity holiday
    assert (
        get_next_market_close("equity", EQUITY_HOLIDAY_MON_2023_6_19)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 20, 16, 0, 0, tzinfo=NY_TZ))
    )

    # equity holiday next day early close holiday
    assert (
        get_next_market_close("equity", EQUITY_HOLIDAY_NEXT_DAY_EARLY_CLOSE_CLOSE_THU_2023_11_23_13)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 11, 24, 13, 0, 0, tzinfo=NY_TZ))
    )

    # equity early close holiday
    assert (
        get_next_market_close("equity", EQUITY_EARLY_CLOSE_OPEN_FRI_2023_11_24_11)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 11, 24, 13, 0, 0, tzinfo=NY_TZ))
    )
    assert (
        get_next_market_close("equity", EQUITY_EARLY_CLOSE_CLOSE_FRI_2023_11_24_14)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 11, 27, 16, 0, 0, tzinfo=NY_TZ))
    )

    # fx & metal within market hours (before 10pm UTC)
    assert (
        get_next_market_close("fx", FX_METAL_OPEN_WED_2023_6_21_21)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 23, 17, 0, 0, tzinfo=NY_TZ))
    )
    assert (
        get_next_market_close("metal", FX_METAL_OPEN_WED_2023_6_21_21)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 23, 17, 0, 0, tzinfo=NY_TZ))
    )

    # fx & metal within market hours (after 10pm UTC)
    assert (
        get_next_market_close("fx", FX_METAL_OPEN_WED_2023_6_21_23)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 23, 17, 0, 0, tzinfo=NY_TZ))
    )
    assert (
        get_next_market_close("metal", FX_METAL_OPEN_WED_2023_6_21_23)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 23, 17, 0, 0, tzinfo=NY_TZ))
    )

    # fx & metal out of market hours
    assert (
        get_next_market_close("fx", FX_METAL_CLOSE_SUN_2023_6_18_16)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 23, 17, 0, 0, tzinfo=NY_TZ))
    )
    assert (
        get_next_market_close("metal", FX_METAL_CLOSE_SUN_2023_6_18_16)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 23, 17, 0, 0, tzinfo=NY_TZ))
    )

    # fx & metal holiday
    assert (
        get_next_market_close("fx", FX_METAL_HOLIDAY_SUN_2023_1_1)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 1, 6, 17, 0, 0, tzinfo=NY_TZ))
    )
    assert (
        get_next_market_close("metal", FX_METAL_HOLIDAY_SUN_2023_1_1)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 1, 6, 17, 0, 0, tzinfo=NY_TZ))
    )

    # rates within market hours
    assert (
        get_next_market_close("rates", RATES_OPEN_WED_2023_6_21_12)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 21, 17, 0, 0, tzinfo=NY_TZ))
    )

    # rates out of market hours
    assert (
        get_next_market_close("rates", RATES_CLOSE_WED_2023_6_21_17)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 22, 17, 0, 0, tzinfo=NY_TZ))
    )

    # rates weekend
    assert (
        get_next_market_close("rates", RATES_CLOSE_SAT_2023_6_10_17)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 12, 17, 0, 0, tzinfo=NY_TZ))
    )

    # rates holiday
    assert (
        get_next_market_close("rates", RATES_HOLIDAY_MON_2023_6_19)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 6, 20, 17, 0, 0, tzinfo=NY_TZ))
    )

    # rates holiday next day early close holiday
    assert (
        get_next_market_close("rates", RATES_HOLIDAY_NEXT_DAY_EARLY_CLOSE_CLOSE_THU_2023_11_23_13)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 11, 24, 13, 0, 0, tzinfo=NY_TZ))
    )

    # rates early close holiday
    assert (
        get_next_market_close("rates", RATES_EARLY_CLOSE_OPEN_FRI_2023_11_24_11)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 11, 24, 13, 0, 0, tzinfo=NY_TZ))
    )
    assert (
        get_next_market_close("rates", RATES_EARLY_CLOSE_CLOSE_FRI_2023_11_24_14)
        == format_datetime_to_unix_timestamp(datetime.datetime(2023, 11, 27, 17, 0, 0, tzinfo=NY_TZ))
    )

    # crypto
    assert get_next_market_close("crypto", CRYPTO_OPEN_WED_2023_6_21_12) == None
    assert get_next_market_close("crypto", CRYPTO_OPEN_SUN_2023_6_18_12) == None
