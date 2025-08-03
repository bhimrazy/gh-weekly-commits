"""Tests for ghweekly.exceptions module."""

from ghweekly.exceptions import GHWeeklyError, APIError, ValidationError, NetworkError


def test_base_exception():
    """Test base exception creation and inheritance."""
    error = GHWeeklyError("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)


def test_api_error_with_message():
    """Test API error with status code and message."""
    error = APIError(404, "Not found")
    assert error.status_code == 404
    assert error.message == "Not found"
    assert str(error) == "GitHub API error 404: Not found"


def test_api_error_without_message():
    """Test API error with only status code."""
    error = APIError(500)
    assert error.status_code == 500
    assert error.message == ""
    assert str(error) == "GitHub API error 500: "


def test_api_error_inheritance():
    """Test API error inheritance."""
    error = APIError(403, "Forbidden")
    assert isinstance(error, GHWeeklyError)
    assert isinstance(error, Exception)


def test_validation_error():
    """Test validation error creation."""
    error = ValidationError("Invalid input")
    assert str(error) == "Invalid input"
    assert isinstance(error, GHWeeklyError)


def test_network_error():
    """Test network error creation."""
    error = NetworkError("Connection failed")
    assert str(error) == "Connection failed"
    assert isinstance(error, GHWeeklyError)
