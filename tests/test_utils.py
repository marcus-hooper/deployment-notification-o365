import os
import re
import pytest
import send_deployment_notification as script


class TestGetEnvVariable:
    """Tests for get_env_variable function."""

    def test_returns_value_when_set(self, monkeypatch):
        """Should return the environment variable value when it exists."""
        monkeypatch.setenv("TEST_VAR", "test_value")
        result = script.get_env_variable("TEST_VAR")
        assert result == "test_value"

    def test_raises_when_required_and_missing(self, clean_env):
        """Should raise ValueError when required variable is missing."""
        with pytest.raises(ValueError) as exc_info:
            script.get_env_variable("MISSING_VAR", required=True)
        assert "MISSING_VAR" in str(exc_info.value)

    def test_returns_none_when_optional_and_missing(self, clean_env):
        """Should return None when optional variable is missing."""
        result = script.get_env_variable("MISSING_VAR", required=False)
        assert result is None

    def test_returns_empty_string_when_set_empty(self, monkeypatch):
        """Should return empty string when variable is set but empty."""
        monkeypatch.setenv("EMPTY_VAR", "")
        # Empty string is falsy, so required=True should raise
        with pytest.raises(ValueError):
            script.get_env_variable("EMPTY_VAR", required=True)

    def test_handles_whitespace_value(self, monkeypatch):
        """Should return whitespace value as-is."""
        monkeypatch.setenv("WHITESPACE_VAR", "  value  ")
        result = script.get_env_variable("WHITESPACE_VAR")
        assert result == "  value  "


class TestGetFormattedTime:
    """Tests for get_formatted_time function."""

    def test_returns_string(self):
        """Should return a string."""
        result = script.get_formatted_time()
        assert isinstance(result, str)

    def test_matches_expected_format(self):
        """Should return time in YYYY-MM-DD HH:MM:SS format."""
        result = script.get_formatted_time()
        # Pattern: 2024-01-15 14:30:45
        pattern = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"
        assert re.match(pattern, result), f"Time '{result}' doesn't match expected format"

    def test_returns_valid_date_components(self):
        """Should return valid date/time components."""
        result = script.get_formatted_time()
        parts = result.split(" ")
        assert len(parts) == 2, "Should have date and time parts"

        date_parts = parts[0].split("-")
        assert len(date_parts) == 3, "Date should have year, month, day"
        year, month, day = map(int, date_parts)
        assert 2020 <= year <= 2100, "Year should be reasonable"
        assert 1 <= month <= 12, "Month should be 1-12"
        assert 1 <= day <= 31, "Day should be 1-31"

        time_parts = parts[1].split(":")
        assert len(time_parts) == 3, "Time should have hour, minute, second"
        hour, minute, second = map(int, time_parts)
        assert 0 <= hour <= 23, "Hour should be 0-23"
        assert 0 <= minute <= 59, "Minute should be 0-59"
        assert 0 <= second <= 59, "Second should be 0-59"

    def test_returns_consistent_length(self):
        """Should always return a string of consistent length."""
        result = script.get_formatted_time()
        # Format: YYYY-MM-DD HH:MM:SS = 19 characters
        assert len(result) == 19
