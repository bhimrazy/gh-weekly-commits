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
    assert df.map(lambda x: isinstance(x, (int, float))).all().all()

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

def test_fetch_weekly_commits_with_merge_commits(monkeypatch):
    """Test that commits where user is committer (but not author) are counted when include_committer=True."""
    
    def mock_get(*args, **kwargs):        
        # First call should be for author commits - return empty
        if "author" in kwargs["params"]:
            return MockResponse(status_code=200, json_data=[])
        # Second call should be for committer commits - return a merge commit
        elif "committer" in kwargs["params"]:
            if kwargs["params"]["page"] == 1:
                return MockResponse(status_code=200, json_data=[
                    {
                        "sha": "merge123",
                        "commit": {
                            "author": {"date": "2025-01-15T10:00:00Z"},
                            "committer": {"date": "2025-01-15T10:00:00Z"}
                        }
                    }
                ])
            else:
                # Return empty for pages > 1
                return MockResponse(status_code=200, json_data=[])
        else:
            return MockResponse(status_code=200, json_data=[])
    
    monkeypatch.setattr("requests.get", mock_get)
    df = fetch_weekly_commits("user", ["org/repo"], datetime(2025,1,1), datetime(2025,2,1), {}, include_committer=True)
    
    assert isinstance(df, pd.DataFrame)
    # Should have 1 commit counted from the merge commit
    assert df.sum().sum() == 1

def test_fetch_weekly_commits_default_author_only(monkeypatch):
    """Test that by default, only author commits are counted (not committer)."""
    
    def mock_get(*args, **kwargs):        
        # Only author calls should be made, return empty
        if "author" in kwargs["params"]:
            return MockResponse(status_code=200, json_data=[])
        # Committer calls should not be made in default mode
        elif "committer" in kwargs["params"]:
            # This should not be called in default mode
            assert False, "Committer API should not be called when include_committer=False"
        else:
            return MockResponse(status_code=200, json_data=[])
    
    monkeypatch.setattr("requests.get", mock_get)
    df = fetch_weekly_commits("user", ["org/repo"], datetime(2025,1,1), datetime(2025,2,1), {})
    
    assert isinstance(df, pd.DataFrame)
    assert (df == 0).all().all()

def test_fetch_weekly_commits_deduplication(monkeypatch):
    """Test that commits where user is both author and committer are not double-counted."""
    
    def mock_get(*args, **kwargs):
        # Return the same commit for both author and committer queries (only on page 1)
        if kwargs["params"]["page"] == 1:
            return MockResponse(status_code=200, json_data=[
                {
                    "sha": "commit123",
                    "commit": {
                        "author": {"date": "2025-01-15T10:00:00Z"},
                        "committer": {"date": "2025-01-15T10:00:00Z"}
                    }
                }
            ])
        else:
            return MockResponse(status_code=200, json_data=[])
    
    monkeypatch.setattr("requests.get", mock_get)
    df = fetch_weekly_commits("user", ["org/repo"], datetime(2025,1,1), datetime(2025,2,1), {}, include_committer=True)
    
    assert isinstance(df, pd.DataFrame)
    # Should only count the commit once, not twice
    assert df.sum().sum() == 1
