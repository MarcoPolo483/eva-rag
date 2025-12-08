"""Tests for datetime utilities."""
from datetime import datetime

from dateutil import tz

from eva_rag.utils.datetime_utils import format_datetime, now_utc, parse_datetime


def test_now_utc_returns_utc_timezone() -> None:
    """Test now_utc returns datetime with UTC timezone."""
    result = now_utc()
    
    assert result.tzinfo is not None
    assert result.tzinfo == tz.UTC


def test_format_datetime_iso() -> None:
    """Test format_datetime returns ISO 8601 format."""
    dt = datetime(2025, 12, 7, 14, 30, 0, tzinfo=tz.UTC)
    
    result = format_datetime(dt, "iso")
    
    assert result == "2025-12-07T14:30:00+00:00"


def test_format_datetime_display() -> None:
    """Test format_datetime returns human-readable format."""
    dt = datetime(2025, 12, 7, 14, 30, 0, tzinfo=tz.UTC)
    
    result = format_datetime(dt, "display")
    
    assert "December" in result
    assert "2025" in result
    assert "UTC" in result


def test_parse_datetime_iso() -> None:
    """Test parse_datetime parses ISO 8601 string."""
    dt_str = "2025-12-07T14:30:00+00:00"
    
    result = parse_datetime(dt_str)
    
    assert result.year == 2025
    assert result.month == 12
    assert result.day == 7
    assert result.hour == 14
    assert result.minute == 30
    assert result.tzinfo is not None


def test_format_and_parse_roundtrip() -> None:
    """Test datetime can be formatted and parsed back."""
    original = datetime(2025, 12, 7, 14, 30, 0, tzinfo=tz.UTC)
    
    formatted = format_datetime(original, "iso")
    parsed = parse_datetime(formatted)
    
    assert parsed == original
