from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# A time is a string of the form HHMM and 2400 is used to represent midnight
Time = str

# A time range is a tuple of two times, representing the start and end of a trading session. This
# range is *inclusive of the start time and exclusive of the end time*.
TimeRange = Tuple[Time, Time]

# A daily schedule is a list of time ranges, representing the trading sessions for a given day
DailySchedule = List[TimeRange]

class MarketSchedule:
    def __init__(self, schedule_str: str):
        """
        Parse a schedule string in Pyth format: "Timezone;WeeklySchedule;Holidays"
        """

        parts = schedule_str.split(';')
        if len(parts) < 2:
            raise ValueError("Schedule must contain at least timezone and weekly schedule")
        
        self.timezone = self._validate_timezone(parts[0])
        # Parse and validate weekly schedule - now returns parsed time ranges
        self.weekly_schedule = self._parse_weekly_schedule(parts[1])
        self.holiday_schedule = self._parse_holidays(parts[2] if len(parts) > 2 else "")

    def _validate_timezone(self, timezone_str: str) -> ZoneInfo:
        try:
            return ZoneInfo(timezone_str)
        except ZoneInfoNotFoundError:
            raise ValueError(f"Invalid timezone: {timezone_str}")

    def _parse_weekly_schedule(self, schedule: str) -> List[DailySchedule]:
        """Parse the weekly schedule (Mon-Sun) into daily schedules"""
        days = schedule.split(',')
        if len(days) != 7:
            raise ValueError("Weekly schedule must contain exactly 7 days")
        
        weekly_schedule = []
        for day_schedule in days:
            try:
                weekly_schedule.append(self._parse_daily_schedule(day_schedule))
            except ValueError as e:
                raise ValueError(f"Invalid schedule format: {day_schedule}") from e
                
        return weekly_schedule

    def _parse_holidays(self, holidays: str) -> Dict[str, DailySchedule]:
        """Parse holiday overrides in format MMDD/Schedule"""
        if not holidays:
            return {}
        
        holiday_dict = {}
        for holiday in holidays.split(','):
            if not holiday:
                continue
            date_str, schedule = holiday.split('/')
            holiday_dict[date_str] = self._parse_daily_schedule(schedule)
        return holiday_dict

    def _parse_daily_schedule(self, schedule: str) -> DailySchedule:
        """Parse time ranges in format HHMM-HHMM or HHMM-HHMM&HHMM-HHMM"""
        if schedule == 'O':
            return [('0000', '2400')]
        elif schedule == 'C':
            return []
        
        ranges = []
        for time_range in schedule.split('&'):
            start, end = time_range.split('-')

            
            # Validate time format (HHMM)
            if not (len(start) == 4 and len(end) == 4 and
                   start.isdigit() and end.isdigit() and
                   0 <= int(start[:2]) <= 23 and 0 <= int(start[2:]) <= 59 and
                   ((0 <= int(end[:2]) <= 23 and 0 <= int(end[2:]) <= 59) or end == "2400")):
                raise ValueError(f"Invalid time format in schedule: {start}-{end}")
                
            ranges.append((start, end))
        
        # Sort ranges by start time
        ranges.sort(key=lambda x: x[0])

        return ranges

    def _get_time_ranges_for_date(self, dt: datetime) -> List[TimeRange]:
        """Helper function to get time ranges for a specific date, checking holiday schedule first"""
        date_str = dt.strftime("%m%d")
        if date_str in self.holiday_schedule:
            return self.holiday_schedule[date_str]
        return self.weekly_schedule[dt.weekday()]

    def is_market_open(self, dt: datetime) -> bool:
        """Check if the market is open at the given datetime"""
        # Convert to market timezone
        local_dt = dt.astimezone(self.timezone)
        time_ranges = self._get_time_ranges_for_date(local_dt)
        
        if not time_ranges:
            return False

        # Check current time against ranges
        current_time = local_dt.strftime("%H%M")
        return any(start <= current_time < end for start, end in time_ranges)

    def get_next_market_open(self, dt: datetime) -> Optional[datetime]:
        """Get the next market open datetime after the given datetime. If the market
        is open at the given datetime (even if just opens at the given time),
        returns the next open datetime.
        
        If the market is always open, returns None. The returned datetime is in
        the timezone of the input datetime."""
        input_tz = dt.tzinfo
        current = dt.astimezone(self.timezone)

        # This flag is a invariant that indicates whether we're in the initial
        # trading session of the given datetime as we move forward in time.
        in_initial_trading_session = True
        
        # Look ahead up to 14 days
        for _ in range(14):
            time_ranges = self._get_time_ranges_for_date(current)
            
            current_time = current.strftime("%H%M")
            
            # Find the next open time after current_time
            next_open = None
            for start, end in time_ranges:
                # If the end time is before the current time, skip
                if end < current_time:
                    continue

                # If we're in the middle of a trading session, look for next session
                # the complicated logic is to handle the distinction between
                # a trading session that continues past midnight and one that doesn't
                if start < current_time < end or (in_initial_trading_session and start <= current_time < end):
                    continue

                # Reaching here means we're no longer in a trading session
                in_initial_trading_session = False

                # If this start time is after current time, this is the next open
                if current_time < start:
                    next_open = start
                    break
            
            if next_open is not None:
                # Found next opening time today
                hour, minute = int(next_open[:2]), int(next_open[2:])
                result = current.replace(hour=hour, minute=minute, second=0, microsecond=0)
                return result.astimezone(input_tz)  # Convert back to input timezone
            
            # Move to next day at midnight
            current = (current + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

            # There is a potential edge case where the market immediately opens at midnight (when rolling over to the next day)
            # In this case, the new current time is the open time.
            if self.is_market_open(current) and not self.is_market_open(current - timedelta(minutes=1)):
                return current.astimezone(input_tz)
        
        return None

    def get_next_market_close(self, dt: datetime) -> Optional[datetime]:
        """Get the next market close datetime after the given datetime. If the
        market just closes at the given datetime, returns the next close datetime.
        
        If the market is always open, returns None. The returned datetime is in
        the timezone of the input datetime."""
        input_tz = dt.tzinfo
        current = dt.astimezone(self.timezone)
        
        # Look ahead up to 14 days
        for _ in range(14):
            time_ranges = self._get_time_ranges_for_date(current)
            
            current_time = current.strftime("%H%M")
            
            # Find the next close time after current_time
            next_close = None
            for _, end in time_ranges:
                # If the end time is before (or equal to) the current time, skip
                if end <= current_time:
                    continue

                # If we're in a trading session or a new one starts and the end time
                # doesn't roll over to the next day, this is the next close
                if current_time < end and end < "2400":
                    next_close = end
                    break

            if next_close is not None:
                # Found next closing time
                hour, minute = int(next_close[:2]), int(next_close[2:])
                result = current.replace(hour=hour, minute=minute, second=0, microsecond=0)
                return result.astimezone(input_tz)  # Convert back to input timezone
            
            # Move to next day at midnight
            current = (current + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

            # There is a potential edge case where the market is not open at midnight (when rolling over to the next day)
            # In this case, the new current time is the close time.
            if not self.is_market_open(current) and self.is_market_open(current - timedelta(minutes=1)):
                return current.astimezone(input_tz)
        
        return None
