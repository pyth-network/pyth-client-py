import pytest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pythclient.market_schedule import MarketSchedule

# This fixtures are based on the schedule from the metadata of the assets taken at 2024-12-20
FIXTURES = {
    "amazonusd": "America/New_York;0930-1600,0930-1600,0930-1600,0930-1600,0930-1600,C,C;1224/0930-1300,1225/C,0101/C,0120/C,0217/C,0418/C,0526/C,0619/C",
    "brent1musd": "America/New_York;0000-1800&2000-2400,0000-1800&2000-2400,0000-1800&2000-2400,0000-1800&2000-2400,0000-1800,C,1800-2400;1224/0000-1400&2000-2400,1225/C,0101/C,0418/C",
    "btcusd": "America/New_York;O,O,O,O,O,O,O;",
    "eurusd": "America/New_York;O,O,O,O,0000-1700,C,1700-2400;1224/0000-1700,1225/1700-2400,1231/0000-1700,0101/1700-2400",
}

def test_market_open():
    # Test Amazon trading hours (regular NYSE hours)
    schedule = MarketSchedule(FIXTURES["amazonusd"])

    # Close at 9:29 ET
    assert not schedule.is_market_open(datetime(2024, 3, 1, 9, 29, tzinfo=ZoneInfo("UTC"))) # 9:29 ET
    # Open at 9:30 ET
    assert schedule.is_market_open(datetime(2024, 3, 1, 14, 30, tzinfo=ZoneInfo("UTC"))) # 9:30 ET

    # Regular trading day
    assert schedule.is_market_open(datetime(2024, 3, 1, 19, 30, tzinfo=ZoneInfo("UTC"))) # 14:30 ET

    # Open at 15:59 ET
    assert schedule.is_market_open(datetime(2024, 3, 1, 20, 59, tzinfo=ZoneInfo("UTC"))) # 15:59 ET
    # Close at 16:00 ET
    assert not schedule.is_market_open(datetime(2024, 3, 1, 21, 0, tzinfo=ZoneInfo("UTC"))) # 16:00 ET
    
    # Weekend
    assert not schedule.is_market_open(datetime(2024, 3, 2, 14, 30, tzinfo=ZoneInfo("UTC"))) # Saturday 9:30 ET
    
    # Holiday (Christmas) - market is closed
    assert not schedule.is_market_open(datetime(2024, 12, 25, 14, 30, tzinfo=ZoneInfo("UTC"))) # Christmas 25/12/2024 9:30 ET

    # Holiday (Christmas Eve) - market has early close
    assert not schedule.is_market_open(datetime(2024, 12, 24, 14, 29, tzinfo=ZoneInfo("UTC"))) # Christmas Eve 24/12/2024 9:29 ET
    assert schedule.is_market_open(datetime(2024, 12, 24, 14, 30, tzinfo=ZoneInfo("UTC"))) # Christmas Eve 24/12/2024 9:30 ET
    assert schedule.is_market_open(datetime(2024, 12, 24, 17, 59, tzinfo=ZoneInfo("UTC"))) # Christmas Eve 24/12/2024 12:59 ET
    assert not schedule.is_market_open(datetime(2024, 12, 24, 18, 0, tzinfo=ZoneInfo("UTC"))) # Christmas Eve 24/12/2024 13:00 ET

def test_next_market_open():
    schedule = MarketSchedule(FIXTURES["amazonusd"])
    
    # Test next open from weekend
    dt = datetime(2024, 3, 2, 12, 0, tzinfo=ZoneInfo("UTC")) # Saturday
    next_open = schedule.get_next_market_open(dt)
    assert next_open.strftime("%Y-%m-%d %H:%M") == "2024-03-04 14:30" # Monday 9:30 ET
    
    # Test next open from current open trading session (right at the start of the session)
    dt = datetime(2024, 3, 1, 14, 30, tzinfo=ZoneInfo("UTC")) # Friday 9:30 ET
    next_open = schedule.get_next_market_open(dt)
    assert next_open.strftime("%Y-%m-%d %H:%M") == "2024-03-04 14:30" # Monday 9:30 ET

def test_next_market_close():
    schedule = MarketSchedule(FIXTURES["amazonusd"])
    
    # Test next close during trading hours
    dt = datetime(2024, 3, 1, 14, 30, tzinfo=ZoneInfo("UTC")) # Friday 9:30 ET
    next_close = schedule.get_next_market_close(dt)
    assert next_close == datetime(2024, 3, 1, 21, 0, tzinfo=ZoneInfo("UTC"))

    # Test next close from the end of the trading session
    dt = datetime(2024, 3, 1, 21, 0, tzinfo=ZoneInfo("UTC")) # Friday 16:00 ET
    next_close = schedule.get_next_market_close(dt)
    assert next_close == datetime(2024, 3, 4, 21, 0, tzinfo=ZoneInfo("UTC"))
    
    # Test next close from weekend
    dt = datetime(2024, 3, 2, 12, 0, tzinfo=ZoneInfo("UTC")) # Saturday 8:00 ET
    next_close = schedule.get_next_market_close(dt)
    assert next_close == datetime(2024, 3, 4, 21, 0, tzinfo=ZoneInfo("UTC"))

def test_complex_schedule_brent1musd():
    """Test Brent oil futures with multiple sessions per day"""

    schedule = MarketSchedule(FIXTURES["brent1musd"])
    
    # Test during first session, 4 Dec 2024 (Wednesday)
    assert schedule.is_market_open(datetime(2024, 12, 4, 0, 0, tzinfo=ZoneInfo("America/New_York")))
    assert schedule.is_market_open(datetime(2024, 12, 4, 12, 0, tzinfo=ZoneInfo("America/New_York")))
    
    # Test during gap between sessions
    assert not schedule.is_market_open(datetime(2024, 12, 4, 18, 0, tzinfo=ZoneInfo("America/New_York")))
    assert not schedule.is_market_open(datetime(2024, 12, 4, 19, 0, tzinfo=ZoneInfo("America/New_York")))
    
    # Test during second session
    assert schedule.is_market_open(datetime(2024, 12, 4, 20, 0, tzinfo=ZoneInfo("America/New_York")))
    assert schedule.is_market_open(datetime(2024, 12, 4, 23, 59, tzinfo=ZoneInfo("America/New_York")))

    # Test next market close
    next_close = schedule.get_next_market_close(datetime(2024, 12, 4, 23, 59, tzinfo=ZoneInfo("America/New_York")))
    assert next_close == datetime(2024, 12, 5, 18, 0, tzinfo=ZoneInfo("America/New_York"))

    # Test next market open
    next_open = schedule.get_next_market_open(datetime(2024, 12, 4, 23, 59, tzinfo=ZoneInfo("America/New_York")))
    assert next_open == datetime(2024, 12, 5, 20, 0, tzinfo=ZoneInfo("America/New_York"))

def test_always_open_schedule():
    """Test a schedule that is always open"""

    schedule = MarketSchedule(FIXTURES["btcusd"])
    assert schedule.is_market_open(datetime(2024, 12, 3, 23, 59, tzinfo=ZoneInfo("America/New_York")))

    # Make sure next market open and next market close are None
    assert schedule.get_next_market_open(datetime(2024, 12, 3, 23, 59, tzinfo=ZoneInfo("America/New_York"))) is None
    assert schedule.get_next_market_close(datetime(2024, 12, 3, 23, 59, tzinfo=ZoneInfo("America/New_York"))) is None

def test_invalid_schedules():
    # Test invalid timezone
    with pytest.raises(ValueError):
        MarketSchedule("Invalid/Timezone;0930-1600,0930-1600,0930-1600,0930-1600,0930-1600,C,C")
    
    # Test invalid number of days
    with pytest.raises(ValueError):
        MarketSchedule("America/New_York;0930-1600,0930-1600,0930-1600,0930-1600,0930-1600,C")
    
    # Test invalid time format
    with pytest.raises(ValueError):
        MarketSchedule("America/New_York;1600-2500,0930-1600,0930-1600,0930-1600,0930-1600,C,C")
    
    # Test invalid schedule format
    with pytest.raises(ValueError):
        MarketSchedule("America/New_York;0930-1600-1700,0930-1600,0930-1600,0930-1600,0930-1600,C,C")
    
    # Test invalid holiday schedule
    with pytest.raises(ValueError):
        MarketSchedule("America/New_York;0930-1600,0930-1600,0930-1600,0930-1600,0930-1600,C,C;1224/0930-2500")

@pytest.mark.parametrize("asset", ["amazonusd", "brent1musd", "eurusd"])
def test_walk_backwards_through_schedule(asset):
    """Test walking backwards through the schedule to test the next market open and next market close"""
    schedule = MarketSchedule(FIXTURES[asset])

    current_time = datetime(2025, 6, 6, 0, 0, tzinfo=ZoneInfo("America/New_York"))
    expected_next_market_open = None
    expected_next_market_close = None

    while datetime(2024, 6, 6, 0, 0, tzinfo=ZoneInfo("America/New_York")) < current_time:
        # update the expected next market open and next market close
        if not schedule.is_market_open(current_time) and schedule.is_market_open(current_time + timedelta(minutes=1)):
            expected_next_market_open = current_time + timedelta(minutes=1)
        if schedule.is_market_open(current_time) and not schedule.is_market_open(current_time + timedelta(minutes=1)):
            expected_next_market_close = current_time + timedelta(minutes=1)

        next_market_open = schedule.get_next_market_open(current_time)
        next_market_close = schedule.get_next_market_close(current_time)

        assert not expected_next_market_open or next_market_open == expected_next_market_open
        assert not expected_next_market_close or next_market_close == expected_next_market_close

        current_time -= timedelta(minutes=1)
