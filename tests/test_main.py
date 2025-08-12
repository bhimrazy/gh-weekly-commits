"""Comprehensive tests for ghweekly.main module."""

import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import patch, MagicMock
import requests.exceptions

from ghweekly.main import fetch_weekly_commits, fetch_commits_for_repo
from ghweekly.exceptions import APIError, NetworkError, ValidationError


@pytest.fixture
def mock_data():
    return {
        "username": "testuser",
        "repos": ["org/repo1", "org/repo2"],
        "start": datetime(2025, 1, 1),
        "end": datetime(2025, 5, 1),
        "headers": {},
    }


class MockResponse:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json_data = json_data or []

    def json(self):
        return self._json_data


def test_fetch_weekly_commits_empty_repos():
    df = fetch_weekly_commits(
        username="testuser",
        repos=[],
        start=datetime(2025, 1, 1),
        end=datetime(2025, 5, 1),
        headers={},
    )
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_fetch_weekly_commits(mock_data):
    df = fetch_weekly_commits(
        username=mock_data["username"],
        repos=mock_data["repos"],
        start=mock_data["start"],
        end=mock_data["end"],
        headers=mock_data["headers"],
    )
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["repo1", "repo2"]
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.map(lambda x: isinstance(x, (int, float))).all().all()


def test_fetch_weekly_commits_error(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse(status_code=403)

    monkeypatch.setattr("requests.get", mock_get)
    df = fetch_weekly_commits(
        "user", ["org/repo"], datetime(2025, 1, 1), datetime(2025, 2, 1), {}
    )
    assert isinstance(df, pd.DataFrame)
    assert (df == 0).all().all()


def test_fetch_weekly_commits_no_commits(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse(status_code=200, json_data=[])

    monkeypatch.setattr("requests.get", mock_get)
    df = fetch_weekly_commits(
        "user", ["org/repo"], datetime(2025, 1, 1), datetime(2025, 2, 1), {}
    )
    assert isinstance(df, pd.DataFrame)
    assert (df == 0).all().all()


# Test fetch_commits_for_repo function
@patch("time.sleep")  # Mock sleep to prevent delays
@patch("requests.get")
def test_fetch_commits_for_repo_success(mock_get, mock_sleep):
    """Test successful commit fetching for a single repo."""
    # First page with data, second page empty (proper pagination)
    mock_response_with_data = MockResponse(
        200,
        [
            {"commit": {"author": {"date": "2025-01-01T12:00:00Z"}}},
            {"commit": {"author": {"date": "2025-01-02T12:00:00Z"}}},
        ],
    )
    mock_response_empty = MockResponse(200, [])

    # Simulate proper pagination: first page has data, second page is empty
    mock_get.side_effect = [mock_response_with_data, mock_response_empty]

    commits = fetch_commits_for_repo(
        "org/repo", "testuser", datetime(2025, 1, 1), datetime(2025, 1, 31)
    )

    assert len(commits) == 2
    assert all(isinstance(commit, datetime) for commit in commits)
    assert mock_get.call_count == 2  # Should make exactly 2 requests
    # Should call sleep once for rate limiting (unauthenticated request)
    mock_sleep.assert_called_once_with(0.1)


@patch("time.sleep")
@patch("requests.get")
def test_fetch_commits_for_repo_pagination(mock_get, mock_sleep):
    """Test pagination handling with multiple pages."""
    # First page with data
    mock_response1 = MockResponse(
        200, [{"commit": {"author": {"date": "2025-01-01T12:00:00Z"}}}]
    )
    # Second page with data
    mock_response2 = MockResponse(
        200, [{"commit": {"author": {"date": "2025-01-02T12:00:00Z"}}}]
    )
    # Third page empty (end of pagination)
    mock_response3 = MockResponse(200, [])

    mock_get.side_effect = [mock_response1, mock_response2, mock_response3]

    commits = fetch_commits_for_repo(
        "org/repo", "testuser", datetime(2025, 1, 1), datetime(2025, 1, 31)
    )

    assert len(commits) == 2
    assert mock_get.call_count == 3  # Should make exactly 3 requests
    # Rate limiting sleep should be called twice (once per page) for unauthenticated requests
    assert mock_sleep.call_count == 2


@patch("time.sleep")
@patch("requests.get")
def test_fetch_commits_for_repo_404_error(mock_get, mock_sleep):
    """Test 404 repository not found error."""
    mock_get.return_value = MockResponse(404)

    commits = fetch_commits_for_repo(
        "org/repo", "testuser", datetime(2025, 1, 1), datetime(2025, 1, 31)
    )

    assert len(commits) == 0
    mock_sleep.assert_not_called()  # No retry on 404


@patch("time.sleep")
@patch("requests.get")
def test_fetch_commits_for_repo_403_error(mock_get, mock_sleep):
    """Test 403 forbidden error."""
    mock_get.return_value = MockResponse(403)

    commits = fetch_commits_for_repo(
        "org/repo", "testuser", datetime(2025, 1, 1), datetime(2025, 1, 31)
    )

    assert len(commits) == 0
    mock_sleep.assert_not_called()  # No retry on 403


@patch("time.sleep")
@patch("requests.get")
def test_fetch_commits_for_repo_api_error(mock_get, mock_sleep):
    """Test API error handling."""
    mock_get.return_value = MockResponse(500)

    with pytest.raises(APIError):
        fetch_commits_for_repo(
            "org/repo", "testuser", datetime(2025, 1, 1), datetime(2025, 1, 31)
        )

    mock_sleep.assert_not_called()  # No retry on API error


@patch("time.sleep")
@patch("requests.get")
def test_fetch_commits_for_repo_network_error(mock_get, mock_sleep):
    """Test network error handling."""
    mock_get.side_effect = requests.exceptions.RequestException("Network error")

    with pytest.raises(NetworkError):
        fetch_commits_for_repo(
            "org/repo", "testuser", datetime(2025, 1, 1), datetime(2025, 1, 31)
        )

    # Should retry max_retries times (default 3) before giving up
    assert mock_sleep.call_count == 3


@patch("time.sleep")
@patch("requests.get")
def test_fetch_commits_for_repo_retry_success(mock_get, mock_sleep):
    """Test retry logic on temporary failures."""
    # First call fails, second succeeds
    mock_get.side_effect = [
        requests.exceptions.RequestException("Temporary error"),
        MockResponse(200, [{"commit": {"author": {"date": "2025-01-01T12:00:00Z"}}}]),
        MockResponse(200, []),  # Empty page to end pagination
    ]

    commits = fetch_commits_for_repo(
        "org/repo",
        "testuser",
        datetime(2025, 1, 1),
        datetime(2025, 1, 31),
        max_retries=1,
        retry_delay=0.01,
    )

    assert len(commits) == 1
    # Should sleep once for retry + once for rate limiting
    assert mock_sleep.call_count == 2


@patch("time.sleep")
@patch("requests.get")
def test_fetch_commits_for_repo_malformed_commit_data(mock_get, mock_sleep):
    """Test handling of malformed commit data."""
    # First page with mixed valid and invalid data, second page empty
    mock_response_with_data = MockResponse(
        200,
        [
            {"commit": {"author": {"date": "invalid-date"}}},  # Invalid date
            {"invalid": "structure"},  # Missing commit structure
            {"commit": {"author": {"date": "2025-01-01T12:00:00Z"}}},  # Valid
        ],
    )
    mock_response_empty = MockResponse(200, [])
    mock_get.side_effect = [mock_response_with_data, mock_response_empty]

    commits = fetch_commits_for_repo(
        "org/repo", "testuser", datetime(2025, 1, 1), datetime(2025, 1, 31)
    )

    # Only the valid commit should be returned
    assert len(commits) == 1


@patch("time.sleep")
@patch("requests.get")
def test_fetch_commits_for_repo_invalid_json_response(mock_get, mock_sleep):
    """Test handling of invalid JSON response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_get.return_value = mock_response

    commits = fetch_commits_for_repo(
        "org/repo", "testuser", datetime(2025, 1, 1), datetime(2025, 1, 31)
    )

    assert len(commits) == 0


@patch("time.sleep")
@patch("requests.get")
def test_fetch_commits_for_repo_with_auth_headers(mock_get, mock_sleep):
    """Test that authenticated requests don't trigger rate limiting sleep."""
    mock_response_with_data = MockResponse(
        200,
        [{"commit": {"author": {"date": "2025-01-01T12:00:00Z"}}}],
    )
    mock_response_empty = MockResponse(200, [])
    mock_get.side_effect = [mock_response_with_data, mock_response_empty]

    commits = fetch_commits_for_repo(
        "org/repo",
        "testuser",
        datetime(2025, 1, 1),
        datetime(2025, 1, 31),
        headers={"Authorization": "token secret"},
    )

    assert len(commits) == 1
    # Should not call sleep for authenticated requests
    mock_sleep.assert_not_called()


# Test fetch_weekly_commits validation
def test_fetch_weekly_commits_empty_username():
    """Test validation of empty username."""
    with pytest.raises(ValidationError, match="Username cannot be empty"):
        fetch_weekly_commits(
            "", ["org/repo"], datetime(2025, 1, 1), datetime(2025, 2, 1)
        )


def test_fetch_weekly_commits_invalid_date_range():
    """Test validation of invalid date range."""
    with pytest.raises(ValidationError, match="End date must be after start date"):
        fetch_weekly_commits(
            "user", ["org/repo"], datetime(2025, 2, 1), datetime(2025, 1, 1)
        )


@patch("ghweekly.main.validate_repo_format")
def test_fetch_weekly_commits_invalid_repo_format(mock_validate):
    """Test repo format validation."""
    mock_validate.side_effect = ValidationError("Invalid repo format")

    with pytest.raises(ValidationError):
        fetch_weekly_commits(
            "user", ["invalid-repo"], datetime(2025, 1, 1), datetime(2025, 2, 1)
        )


# Test fetch_weekly_commits with mixed success and failure
@patch("ghweekly.main.fetch_commits_for_repo")
def test_fetch_weekly_commits_mixed_results(mock_fetch):
    """Test fetch_weekly_commits with some repos succeeding and others failing."""
    # repo1 succeeds, repo2 fails
    mock_fetch.side_effect = [
        [datetime(2025, 1, 5), datetime(2025, 1, 12)],  # repo1 succeeds
        APIError(403, "Forbidden"),  # repo2 fails
    ]

    df = fetch_weekly_commits(
        "user", ["org/repo1", "org/repo2"], datetime(2025, 1, 1), datetime(2025, 1, 31)
    )

    assert isinstance(df, pd.DataFrame)
    assert "repo1" in df.columns
    assert "repo2" in df.columns
    # repo2 should be all zeros due to API error
    assert df["repo2"].sum() == 0


@patch("ghweekly.main.fetch_commits_for_repo")
def test_fetch_weekly_commits_network_errors(mock_fetch):
    """Test fetch_weekly_commits with network errors."""
    # repo1 succeeds, repo2 has network error
    mock_fetch.side_effect = [
        [datetime(2025, 1, 5)],  # repo1 succeeds
        NetworkError("Connection failed"),  # repo2 fails
    ]

    df = fetch_weekly_commits(
        "user", ["org/repo1", "org/repo2"], datetime(2025, 1, 1), datetime(2025, 1, 31)
    )

    assert isinstance(df, pd.DataFrame)
    assert "repo1" in df.columns
    assert "repo2" in df.columns
    # repo2 should be all zeros due to network error
    assert df["repo2"].sum() == 0
