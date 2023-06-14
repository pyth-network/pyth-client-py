import datetime

import pytz

TZ = pytz.timezone("America/New_York")

EQUITY_OPEN = datetime.time(9, 30, 0, tzinfo=TZ)
EQUITY_CLOSE = datetime.time(16, 0, 0, tzinfo=TZ)
EQUITY_EARLY_CLOSE = datetime.time(13, 0, 0, tzinfo=TZ)

# EQUITY_HOLIDAYS and EQUITY_EARLY_HOLIDAYS will need to be updated each year
# From https://www.nyse.com/markets/hours-calendars
EQUITY_HOLIDAYS = [
    datetime.datetime(2023, 1, 2, tzinfo=TZ).date(),
    datetime.datetime(2023, 1, 16, tzinfo=TZ).date(),
    datetime.datetime(2023, 2, 20, tzinfo=TZ).date(),
    datetime.datetime(2023, 4, 7, tzinfo=TZ).date(),
    datetime.datetime(2023, 5, 29, tzinfo=TZ).date(),
    datetime.datetime(2023, 6, 19, tzinfo=TZ).date(),
    datetime.datetime(2023, 7, 4, tzinfo=TZ).date(),
    datetime.datetime(2022, 9, 4, tzinfo=TZ).date(),
    datetime.datetime(2023, 11, 23, tzinfo=TZ).date(),
    datetime.datetime(2023, 12, 25, tzinfo=TZ).date(),
]
EQUITY_EARLY_HOLIDAYS = [
    datetime.datetime(2023, 7, 3, tzinfo=TZ).date(),
    datetime.datetime(2023, 11, 24, tzinfo=TZ).date(),
]

FX_METAL_OPEN_CLOSE_TIME = datetime.time(17, 0, 0, tzinfo=TZ)

# FX_METAL_HOLIDAYS will need to be updated each year
# From https://www.cboe.com/about/hours/fx/
FX_METAL_HOLIDAYS = [
    datetime.datetime(2023, 1, 1, tzinfo=TZ).date(),
    datetime.datetime(2023, 12, 25, tzinfo=TZ).date(),
]


def is_market_open(asset_type: str, dt: datetime.datetime) -> bool:
    day, date, time = dt.weekday(), dt.date(), dt.time()

    if asset_type == "equity":
        if date in EQUITY_HOLIDAYS or date in EQUITY_EARLY_HOLIDAYS:
            if (
                date in EQUITY_EARLY_HOLIDAYS
                and time >= EQUITY_OPEN
                and time <= EQUITY_EARLY_CLOSE
            ):
                return True
            return False
        if day < 5 and time >= EQUITY_OPEN and time <= EQUITY_CLOSE:
            return True
        return False

    if asset_type in ["fx", "metal"]:
        if date in FX_METAL_HOLIDAYS:
            return False
        # On Friday the market is closed after 5pm
        if day == 4 and time > FX_METAL_OPEN_CLOSE_TIME:
            return False
        # On Saturday the market is closed all the time
        if day == 5:
            return False
        # On Sunday the market is closed before 5pm
        if day == 6 and time < FX_METAL_OPEN_CLOSE_TIME:
            return False

        return True

    # all other markets (crypto)
    return True


def get_next_market_open(asset_type: str, dt: datetime.datetime) -> str:
    time = dt.time()

    if is_market_open(asset_type, dt):
        return dt.astimezone(pytz.UTC).strftime("%Y-%m-%dT%H:%M:%S") + "Z"

    if asset_type == "equity":
        if time < EQUITY_OPEN:
            next_market_open = dt.replace(
                hour=EQUITY_OPEN.hour,
                minute=EQUITY_OPEN.minute,
                second=0,
                microsecond=0,
            )
        else:
            next_market_open = dt.replace(
                hour=EQUITY_OPEN.hour,
                minute=EQUITY_OPEN.minute,
                second=0,
                microsecond=0,
            )
            next_market_open += datetime.timedelta(days=1)
    elif asset_type in ["fx", "metal"]:
        if time < FX_METAL_OPEN_CLOSE_TIME:
            next_market_open = dt.replace(
                hour=FX_METAL_OPEN_CLOSE_TIME.hour,
                minute=FX_METAL_OPEN_CLOSE_TIME.minute,
                second=0,
                microsecond=0,
            )
        else:
            next_market_open = dt.replace(
                hour=FX_METAL_OPEN_CLOSE_TIME.hour,
                minute=FX_METAL_OPEN_CLOSE_TIME.minute,
                second=0,
                microsecond=0,
            )
            next_market_open += datetime.timedelta(days=1)
    else:
        next_market_open = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        next_market_open += datetime.timedelta(days=1)

    while not is_market_open(asset_type, next_market_open):
        next_market_open += datetime.timedelta(days=1)

    return next_market_open.astimezone(pytz.UTC).strftime("%Y-%m-%dT%H:%M:%S") + "Z"
