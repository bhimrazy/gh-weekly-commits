"""Tests for ghweekly.plotting module."""

import pytest
import pandas as pd
import matplotlib
from unittest.mock import patch
from ghweekly.plotting import create_weekly_commits_plot

# Use non-interactive backend for testing
matplotlib.use('Agg')


@pytest.fixture
def sample_dataframe():
    """Create sample DataFrame for testing."""
    dates = pd.date_range('2025-01-01', periods=4, freq='7D')
    data = {
        'repo1': [5, 3, 7, 2],
        'repo2': [2, 1, 4, 0],
    }
    return pd.DataFrame(data, index=dates)


@pytest.fixture
def empty_dataframe():
    """Create empty DataFrame for testing."""
    return pd.DataFrame()


@patch('matplotlib.pyplot.show')
@patch('matplotlib.pyplot.savefig')
def test_plot_with_data(mock_savefig, mock_show, sample_dataframe):
    """Test plot creation with valid data."""
    create_weekly_commits_plot(
        df=sample_dataframe,
        username="testuser",
        output_file="test_output.png",
        show_plot=True
    )
    
    mock_savefig.assert_called_once_with("test_output.png", dpi=300, bbox_inches="tight")
    mock_show.assert_called_once()


@patch('matplotlib.pyplot.show')
@patch('matplotlib.pyplot.savefig')
def test_plot_empty_data(mock_savefig, mock_show, empty_dataframe):
    """Test plot creation with empty data."""
    create_weekly_commits_plot(
        df=empty_dataframe,
        username="testuser",
        output_file="test_empty.png",
        show_plot=True
    )
    
    mock_savefig.assert_called_once_with("test_empty.png", dpi=300, bbox_inches="tight")
    mock_show.assert_called_once()


@patch('matplotlib.pyplot.show')
@patch('matplotlib.pyplot.savefig')
def test_plot_no_output_file(mock_savefig, mock_show, sample_dataframe):
    """Test plot creation without output file."""
    create_weekly_commits_plot(
        df=sample_dataframe,
        username="testuser",
        show_plot=True
    )
    
    mock_savefig.assert_not_called()
    mock_show.assert_called_once()


@patch('matplotlib.pyplot.show')
@patch('matplotlib.pyplot.savefig')
def test_plot_no_show(mock_savefig, mock_show, sample_dataframe):
    """Test plot creation without showing."""
    create_weekly_commits_plot(
        df=sample_dataframe,
        username="testuser",
        output_file="test_no_show.png",
        show_plot=False
    )
    
    mock_savefig.assert_called_once_with("test_no_show.png", dpi=300, bbox_inches="tight")
    mock_show.assert_not_called()


@patch('matplotlib.pyplot.show')
@patch('matplotlib.pyplot.savefig')
def test_plot_custom_parameters(mock_savefig, mock_show, sample_dataframe):
    """Test plot creation with custom parameters."""
    create_weekly_commits_plot(
        df=sample_dataframe,
        username="testuser",
        title="Custom Title",
        figsize=(10, 8),
        colormap="viridis",
        output_file="custom.png",
        show_plot=False
    )
    
    mock_savefig.assert_called_once_with("custom.png", dpi=300, bbox_inches="tight")
    mock_show.assert_not_called()


@patch('matplotlib.pyplot.figure')
def test_plot_figure_creation(mock_figure, sample_dataframe):
    """Test that figure is created correctly."""
    create_weekly_commits_plot(
        df=sample_dataframe,
        username="testuser",
        figsize=(12, 8),
        show_plot=False
    )
    
    mock_figure.assert_called_once_with(figsize=(12, 8))


def test_plot_with_single_repo_data():
    """Test plot creation with single repository data."""
    dates = pd.date_range('2025-01-01', periods=3, freq='7D')
    data = {'single_repo': [3, 5, 2]}
    df = pd.DataFrame(data, index=dates)
    
    with patch('matplotlib.pyplot.show'), patch('matplotlib.pyplot.savefig'):
        create_weekly_commits_plot(
            df=df,
            username="testuser",
            show_plot=False
        )


def test_plot_with_zero_commits():
    """Test plot creation with all zero commits."""
    dates = pd.date_range('2025-01-01', periods=3, freq='7D')
    data = {
        'repo1': [0, 0, 0],
        'repo2': [0, 0, 0],
    }
    df = pd.DataFrame(data, index=dates)
    
    with patch('matplotlib.pyplot.show'), patch('matplotlib.pyplot.savefig'):
        create_weekly_commits_plot(
            df=df,
            username="testuser",
            show_plot=False
        )
