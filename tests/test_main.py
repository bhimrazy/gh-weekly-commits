import pytest
from ghweekly.main import fetch_weekly_commits
from datetime import datetime
import pandas as pd


@pytest.fixture
def mock_data():
    return {
        "username": "testuser",
        "repos": ["org/repo1", "org/repo2"],
        "start": datetime(2025, 1, 1),
        "end": datetime(2025, 5, 1),
        "headers": {},
    }


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
    # Check index is a DatetimeIndex
    assert isinstance(df.index, pd.DatetimeIndex)
    # Check all values are integers (or 0)
    assert df.applymap(lambda x: isinstance(x, (int, float))).all().all()
