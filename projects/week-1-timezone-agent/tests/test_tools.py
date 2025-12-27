"""Tests for timezone tools."""

from agent import get_current_time, convert_time


def test_convert_time_utc_to_utc():
    """Same timezone returns same time."""
    result = convert_time("12:00", "UTC", "UTC")
    assert result == "12:00 UTC = 12:00 UTC"


def test_invalid_timezone():
    """Invalid timezone returns error, not exception."""
    result = get_current_time("Not/Real")
    assert "Invalid" in result
