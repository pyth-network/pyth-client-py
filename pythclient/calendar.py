import datetime
from zoneinfo import ZoneInfo

NY_TZ = ZoneInfo("America/New_York")
UTC_TZ = ZoneInfo("UTC")

EQUITY_OPEN = datetime.time(9, 30, 0, tzinfo=NY_TZ)
EQUITY_CLOSE = datetime.time(16, 0, 0, tzinfo=NY_TZ)

NYSE_EARLY_CLOSE = datetime.time(13, 0, 0, tzinfo=NY_TZ)

# NYSE_HOLIDAYS and NYSE_EARLY_HOLIDAYS will need to be updated each year
# From https://www.nyse.com/markets/hours-calendars
NYSE_HOLIDAYS = [
    datetime.datetime(2023, 1, 2, tzinfo=NY_TZ).date(),
    datetime.datetime(2023, 1, 16, tzinfo=NY_TZ).date(),
    datetime.datetime(2023, 2, 20, tzinfo=NY_TZ).date(),
    datetime.datetime(2023, 4, 7, tzinfo=NY_TZ).date(),
    datetime.datetime(2023, 5, 29, tzinfo=NY_TZ).date(),
    datetime.datetime(2023, 6, 19, tzinfo=NY_TZ).date(),
    datetime.datetime(2023, 7, 4, tzinfo=NY_TZ).date(),
    datetime.datetime(2022, 9, 4, tzinfo=NY_TZ).date(),
    datetime.datetime(2023, 11, 23, tzinfo=NY_TZ).date(),
    datetime.datetime(2023, 12, 25, tzinfo=NY_TZ).date(),
]
NYSE_EARLY_HOLIDAYS = [
    datetime.datetime(2023, 7, 3, tzinfo=NY_TZ).date(),
    datetime.datetime(2023, 11, 24, tzinfo=NY_TZ).date(),
]

FX_METAL_OPEN_CLOSE_TIME = datetime.time(17, 0, 0, tzinfo=NY_TZ)

# FX_METAL_HOLIDAYS will need to be updated each year
# From https://www.cboe.com/about/hours/fx/
FX_METAL_HOLIDAYS = [
    datetime.datetime(2023, 1, 1, tzinfo=NY_TZ).date(),
    datetime.datetime(2023, 12, 25, tzinfo=NY_TZ).date(),
]

RATES_OPEN = datetime.time(8, 0, 0, tzinfo=NY_TZ)
RATES_CLOSE = datetime.time(17, 0, 0, tzinfo=NY_TZ)


def is_market_open(asset_type: str, dt: datetime.datetime) -> bool:
    # make sure time is in NY timezone
    dt = dt.astimezone(NY_TZ)
    day, date, time = dt.weekday(), dt.date(), dt.time()

    if asset_type == "equity":
        if date in NYSE_HOLIDAYS or date in NYSE_EARLY_HOLIDAYS:
            if (
                date in NYSE_EARLY_HOLIDAYS
                and time >= EQUITY_OPEN
                and time < NYSE_EARLY_CLOSE
            ):
                return True
            return False
        if day < 5 and time >= EQUITY_OPEN and time < EQUITY_CLOSE:
            return True
        return False

    if asset_type in ["fx", "metal"]:
        if date in FX_METAL_HOLIDAYS:
            return False
        # On Friday the market is closed after 5pm
        if day == 4 and time >= FX_METAL_OPEN_CLOSE_TIME:
            return False
        # On Saturday the market is closed all the time
        if day == 5:
            return False
        # On Sunday the market is closed before 5pm
        if day == 6 and time < FX_METAL_OPEN_CLOSE_TIME:
            return False

        return True

    if asset_type == "rates":
        if date in NYSE_HOLIDAYS or date in NYSE_EARLY_HOLIDAYS:
            if (
                date in NYSE_EARLY_HOLIDAYS
                and time >= RATES_OPEN
                and time < NYSE_EARLY_CLOSE
            ):
                return True
            return False
        if day < 5 and time >= RATES_OPEN and time < RATES_CLOSE:
            return True
        return False

    # all other markets (crypto)
    return True


def get_next_market_open(asset_type: str, dt: datetime.datetime) -> int:
    # make sure time is in NY timezone
    dt = dt.astimezone(NY_TZ)
    time = dt.time()

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
        if dt.weekday() == 6 and time < FX_METAL_OPEN_CLOSE_TIME:
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
            while is_market_open(asset_type, next_market_open):
                next_market_open += datetime.timedelta(days=1)
    elif asset_type == "rates":
        if time < RATES_OPEN:
            next_market_open = dt.replace(
                hour=RATES_OPEN.hour,
                minute=RATES_OPEN.minute,
                second=0,
                microsecond=0,
            )
        else:
            next_market_open = dt.replace(
                hour=RATES_OPEN.hour,
                minute=RATES_OPEN.minute,
                second=0,
                microsecond=0,
            )
            next_market_open += datetime.timedelta(days=1)
    else:
        return None

    while not is_market_open(asset_type, next_market_open):
        next_market_open += datetime.timedelta(days=1)

    return int(next_market_open.timestamp())


def get_next_market_close(asset_type: str, dt: datetime.datetime) -> int:
    # make sure time is in NY timezone
    dt = dt.astimezone(NY_TZ)
    time = dt.time()

    if asset_type == "equity":
        if dt.date() in NYSE_EARLY_HOLIDAYS:
            if time < NYSE_EARLY_CLOSE:
                next_market_close = dt.replace(
                    hour=NYSE_EARLY_CLOSE.hour,
                    minute=NYSE_EARLY_CLOSE.minute,
                    second=0,
                    microsecond=0,
                )
            else:
                next_market_close = dt.replace(
                    hour=EQUITY_CLOSE.hour,
                    minute=EQUITY_CLOSE.minute,
                    second=0,
                    microsecond=0,
                )
                next_market_close += datetime.timedelta(days=1)
        elif dt.date() in NYSE_HOLIDAYS:
            next_market_open = get_next_market_open(asset_type, dt)
            next_market_open_date = (
                datetime.datetime.fromtimestamp(next_market_open)
                .astimezone(NY_TZ)
                .date()
            )
            if next_market_open_date in NYSE_EARLY_HOLIDAYS:
                next_market_close = (
                    datetime.datetime.fromtimestamp(next_market_open)
                    .astimezone(NY_TZ)
                    .replace(
                        hour=NYSE_EARLY_CLOSE.hour,
                        minute=NYSE_EARLY_CLOSE.minute,
                        second=0,
                        microsecond=0,
                    )
                )
            else:
                next_market_close = (
                    datetime.datetime.fromtimestamp(next_market_open)
                    .astimezone(NY_TZ)
                    .replace(
                        hour=EQUITY_CLOSE.hour,
                        minute=EQUITY_CLOSE.minute,
                        second=0,
                        microsecond=0,
                    )
                )
        else:
            next_market_close = dt.replace(
                hour=EQUITY_CLOSE.hour,
                minute=EQUITY_CLOSE.minute,
                second=0,
                microsecond=0,
            )
            if time >= EQUITY_CLOSE:
                next_market_close += datetime.timedelta(days=1)

        # while next_market_close.date() is in NYSE_HOLIDAYS or weekend, add 1 day
        while (
            next_market_close.date() in NYSE_HOLIDAYS
            or next_market_close.weekday() >= 5
        ):
            next_market_close += datetime.timedelta(days=1)

    elif asset_type in ["fx", "metal"]:
        next_market_close = dt.replace(
            hour=FX_METAL_OPEN_CLOSE_TIME.hour,
            minute=FX_METAL_OPEN_CLOSE_TIME.minute,
            second=0,
            microsecond=0,
        )
        while not is_market_open(asset_type, next_market_close):
            next_market_close += datetime.timedelta(days=1)
        while is_market_open(asset_type, next_market_close):
            next_market_close += datetime.timedelta(days=1)
    elif asset_type == "rates":
        if dt.date() in NYSE_EARLY_HOLIDAYS:
            if time < NYSE_EARLY_CLOSE:
                next_market_close = dt.replace(
                    hour=NYSE_EARLY_CLOSE.hour,
                    minute=NYSE_EARLY_CLOSE.minute,
                    second=0,
                    microsecond=0,
                )
            else:
                next_market_close = dt.replace(
                    hour=RATES_CLOSE.hour,
                    minute=RATES_CLOSE.minute,
                    second=0,
                    microsecond=0,
                )
                next_market_close += datetime.timedelta(days=1)
        elif dt.date() in NYSE_HOLIDAYS:
            next_market_open = get_next_market_open(asset_type, dt)
            next_market_open_date = (
                datetime.datetime.fromtimestamp(next_market_open)
                .astimezone(NY_TZ)
                .date()
            )
            if next_market_open_date in NYSE_EARLY_HOLIDAYS:
                next_market_close = (
                    datetime.datetime.fromtimestamp(next_market_open)
                    .astimezone(NY_TZ)
                    .replace(
                        hour=NYSE_EARLY_CLOSE.hour,
                        minute=NYSE_EARLY_CLOSE.minute,
                        second=0,
                        microsecond=0,
                    )
                )
            else:
                next_market_close = (
                    datetime.datetime.fromtimestamp(next_market_open)
                    .astimezone(NY_TZ)
                    .replace(
                        hour=RATES_CLOSE.hour,
                        minute=RATES_CLOSE.minute,
                        second=0,
                        microsecond=0,
                    )
                )
        else:
            next_market_close = dt.replace(
                hour=RATES_CLOSE.hour,
                minute=RATES_CLOSE.minute,
                second=0,
                microsecond=0,
            )
            if time >= RATES_CLOSE:
                next_market_close += datetime.timedelta(days=1)

        # while next_market_close.date() is in NYSE_HOLIDAYS or weekend, add 1 day
        while (
            next_market_close.date() in NYSE_HOLIDAYS
            or next_market_close.weekday() >= 5
        ):
            next_market_close += datetime.timedelta(days=1)
    else:  # crypto markets never close
        return None

    return int(next_market_close.timestamp())


def get_market_hours_clause(time_column_name):
    us_equity_start_minute = EQUITY_OPEN.hour * 60 + EQUITY_OPEN.minute
    us_equity_end_minute = EQUITY_CLOSE.hour * 60 + EQUITY_CLOSE.minute
    nyse_early_end_minute = NYSE_EARLY_CLOSE.hour * 60 + NYSE_EARLY_CLOSE.minute
    # for all equity, only include data from monday to friday (9:30am ET to 4pm ET) and exclude holidays
    us_equity_clause = f"""
        toDayOfWeek({time_column_name}) <= 5
        AND dateDiff('minute', date_trunc('day', {time_column_name}, '{NY_TZ}'), {time_column_name}, '{NY_TZ}') >= {us_equity_start_minute}
        AND dateDiff('minute', date_trunc('day', {time_column_name}, '{NY_TZ}'), {time_column_name}, '{NY_TZ}') < {us_equity_end_minute}
        AND toDate({time_column_name}) NOT IN ({','.join([f"toDate('{h.strftime('%Y-%m-%d')}')" for h in NYSE_HOLIDAYS])})
        AND (
            toDate({time_column_name}) NOT IN ({','.join([f"toDate('{h.strftime('%Y-%m-%d')}')" for h in NYSE_EARLY_HOLIDAYS])})
            OR (
                toDate({time_column_name}) IN ({','.join([f"toDate('{h.strftime('%Y-%m-%d')}')" for h in NYSE_EARLY_HOLIDAYS])})
                AND dateDiff('minute', date_trunc('day', {time_column_name}, '{NY_TZ}'), {time_column_name}, '{NY_TZ}') < {nyse_early_end_minute}
            )
        )
    """

    fx_metal_start_end_minute = (
        FX_METAL_OPEN_CLOSE_TIME.hour * 60 + FX_METAL_OPEN_CLOSE_TIME.minute
    )

    # for all fx and metal, only include data from sunday (after 5pm ET) to friday (before 5pm ET)
    fx_metal_clause = f"""
        ((toDayOfWeek({time_column_name}) <= 4)
        OR (
            toDayOfWeek({time_column_name}) = 5
            AND dateDiff('minute', date_trunc('day', {time_column_name}, '{NY_TZ}'), {time_column_name}, '{NY_TZ}') < {fx_metal_start_end_minute}
        )
        OR (
            toDayOfWeek({time_column_name}) = 7
            AND dateDiff('minute', date_trunc('day', {time_column_name}, '{NY_TZ}'), {time_column_name}, '{NY_TZ}') >= {fx_metal_start_end_minute}
        ))
        AND toDate({time_column_name}) NOT IN ({','.join([f"toDate('{h.strftime('%Y-%m-%d')}')" for h in FX_METAL_HOLIDAYS])})
    """

    rates_start_minute = RATES_OPEN.hour * 60 + RATES_OPEN.minute
    rates_end_minute = RATES_CLOSE.hour * 60 + RATES_CLOSE.minute
    # for all rates, only include data from monday to friday (8:00am ET to 5pm ET) and exclude holidays
    rates_clause = f"""
        toDayOfWeek({time_column_name}) <= 5
        AND dateDiff('minute', date_trunc('day', {time_column_name}, '{NY_TZ}'), {time_column_name}, '{NY_TZ}') >= {rates_start_minute}
        AND dateDiff('minute', date_trunc('day', {time_column_name}, '{NY_TZ}'), {time_column_name}, '{NY_TZ}') < {rates_end_minute}
        AND toDate({time_column_name}) NOT IN ({','.join([f"toDate('{h.strftime('%Y-%m-%d')}')" for h in NYSE_HOLIDAYS])})
        AND (
            toDate({time_column_name}) NOT IN ({','.join([f"toDate('{h.strftime('%Y-%m-%d')}')" for h in NYSE_EARLY_HOLIDAYS])})
            OR (
                toDate({time_column_name}) IN ({','.join([f"toDate('{h.strftime('%Y-%m-%d')}')" for h in NYSE_EARLY_HOLIDAYS])})
                AND dateDiff('minute', date_trunc('day', {time_column_name}, '{NY_TZ}'), {time_column_name}, '{NY_TZ}') < {nyse_early_end_minute}
            )
        )
    """

    return f"""((symbol LIKE 'Equity.US.%' AND ({us_equity_clause})) OR ((symbol LIKE 'FX.%' OR symbol LIKE 'Metal.%') AND ({fx_metal_clause})) OR (symbol LIKE 'Rates.%' AND ({rates_clause})) OR symbol LIKE 'Crypto.%')"""
