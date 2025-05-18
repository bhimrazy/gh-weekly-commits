import pytest
import pandas as pd
from datetime import datetime
from ghweekly.main import fetch_weekly_commits

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
    assert df.applymap(lambda x: isinstance(x, (int, float))).all().all()

def test_fetch_weekly_commits_error(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse(status_code=403)
    monkeypatch.setattr("requests.get", mock_get)
    df = fetch_weekly_commits("user", ["org/repo"], datetime(2025,1,1), datetime(2025,2,1), {})
    assert isinstance(df, pd.DataFrame)
    assert (df == 0).all().all()

def test_fetch_weekly_commits_no_commits(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse(status_code=200, json_data=[])
    monkeypatch.setattr("requests.get", mock_get)
    df = fetch_weekly_commits("user", ["org/repo"], datetime(2025,1,1), datetime(2025,2,1), {})
    assert isinstance(df, pd.DataFrame)
    assert (df == 0).all().all()
