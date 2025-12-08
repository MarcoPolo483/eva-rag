"""Date and time utilities with dual format support."""
from datetime import datetime
from typing import Literal

from dateutil import tz


DateFormat = Literal["iso", "display"]


def now_utc() -> datetime:
    """Get current UTC timestamp."""
    return datetime.now(tz=tz.UTC)


def format_datetime(
    dt: datetime, 
    format_type: DateFormat = "iso"
) -> str:
    """
    Format datetime in dual format.
    
    Args:
        dt: Datetime to format
        format_type: 'iso' for ISO 8601, 'display' for human-readable
        
    Returns:
        Formatted datetime string
        
    Examples:
        >>> dt = datetime(2025, 12, 7, 14, 30, 0, tzinfo=tz.UTC)
        >>> format_datetime(dt, "iso")
        '2025-12-07T14:30:00+00:00'
        >>> format_datetime(dt, "display")
        'December 7, 2025 at 2:30 PM UTC'
    """
    if format_type == "iso":
        return dt.isoformat()
    else:  # display
        # Windows-compatible format (no %-I)
        return dt.strftime("%B %d, %Y at %I:%M %p %Z").replace(" 0", " ")


def parse_datetime(dt_str: str) -> datetime:
    """
    Parse datetime string (ISO 8601 format).
    
    Args:
        dt_str: ISO 8601 datetime string
        
    Returns:
        Parsed datetime with timezone
        
    Example:
        >>> parse_datetime('2025-12-07T14:30:00+00:00')
        datetime(2025, 12, 7, 14, 30, 0, tzinfo=tzutc())
    """
    return datetime.fromisoformat(dt_str)
