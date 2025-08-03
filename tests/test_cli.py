"""Comprehensive tests for ghweekly.cli module."""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ghweekly.cli import create_parser, main, run, validate_date
from ghweekly.exceptions import ValidationError


# Parser tests
def test_parser_creation():
    """Test parser is created with correct configuration."""
    parser = create_parser()
    assert isinstance(parser, argparse.ArgumentParser)
    assert parser.prog == "ghweekly"


def test_parser_required_args():
    """Test required arguments are configured correctly."""
    parser = create_parser()
    
    # Test help without raising SystemExit
    with pytest.raises(SystemExit):
        parser.parse_args(["--help"])


def test_parser_with_minimal_args():
    """Test parser with minimal required arguments."""
    parser = create_parser()
    args = parser.parse_args([
        "--username", "testuser",
        "--repos", "org/repo1", "org/repo2"
    ])
    
    assert args.username == "testuser"
    assert args.repos == ["org/repo1", "org/repo2"]
    assert args.plot is False
    assert args.verbose is False


def test_parser_with_all_args():
    """Test parser with all arguments."""
    parser = create_parser()
    args = parser.parse_args([
        "--username", "testuser",
        "--repos", "org/repo1",
        "--start", "2025-01-01",
        "--end", "2025-12-31",
        "--token", "secret",
        "--plot",
        "--output", "custom.png",
        "--verbose"
    ])
    
    assert args.username == "testuser"
    assert args.repos == ["org/repo1"]
    assert args.start == "2025-01-01"
    assert args.end == "2025-12-31"
    assert args.token == "secret"
    assert args.plot is True
    assert args.output == "custom.png"
    assert args.verbose is True


# Date validation tests
def test_valid_date_formats():
    """Test valid date formats."""
    valid_dates = [
        "2025-01-01",
        "2025-12-31",
        "2024-02-29",  # Leap year
    ]
    
    for date_str in valid_dates:
        result = validate_date(date_str)
        assert isinstance(result, datetime)


def test_invalid_date_formats():
    """Test invalid date formats."""
    invalid_dates = [
        "2025-13-01",  # Invalid month
        "2025-02-30",  # Invalid day
        "not-a-date",
        "2025/01/01",  # Wrong separator
        "",
    ]
    
    for date_str in invalid_dates:
        with pytest.raises(ValidationError):
            validate_date(date_str)


# Run function tests (mocked)
@patch('ghweekly.cli.fetch_weekly_commits')
@patch('ghweekly.cli.setup_logging')
def test_run_basic(mock_setup_logging, mock_fetch):
    """Test basic run functionality."""
    mock_logger = MagicMock()
    mock_setup_logging.return_value = mock_logger
    
    # Mock DataFrame
    mock_df = MagicMock()
    mock_fetch.return_value = mock_df
    
    run(
        username="testuser",
        repos=["org/repo1"],
        start="2025-01-01",
        end="2025-01-31",
    )
    
    mock_setup_logging.assert_called_once_with("INFO")
    mock_fetch.assert_called_once()


@patch('ghweekly.cli.fetch_weekly_commits')
@patch('ghweekly.cli.setup_logging')
@patch('ghweekly.cli.create_weekly_commits_plot')
@patch('matplotlib.use')
def test_run_with_plot(mock_mpl_use, mock_plot, mock_setup_logging, mock_fetch):
    """Test run with plotting enabled."""
    mock_logger = MagicMock()
    mock_setup_logging.return_value = mock_logger
    
    mock_df = MagicMock()
    mock_fetch.return_value = mock_df
    
    run(
        username="testuser",
        repos=["org/repo1"],
        start="2025-01-01",
        plot=True,
        output="test.png"
    )
    
    mock_mpl_use.assert_called_once_with('Agg')
    mock_plot.assert_called_once()


@patch('ghweekly.cli.setup_logging')
def test_run_with_verbose(mock_setup_logging):
    """Test run with verbose logging."""
    mock_logger = MagicMock()
    mock_setup_logging.return_value = mock_logger
    
    with patch('ghweekly.cli.fetch_weekly_commits') as mock_fetch:
        mock_fetch.return_value = MagicMock()
        
        run(
            username="testuser",
            repos=["org/repo1"],
            start="2025-01-01",
            verbose=True
        )
        
        mock_setup_logging.assert_called_once_with("DEBUG")


@patch('ghweekly.cli.setup_logging')
@patch('ghweekly.cli.fetch_weekly_commits')
@patch('sys.exit')
def test_run_with_validation_error(mock_exit, mock_fetch, mock_setup_logging):
    """Test run with validation error."""
    mock_logger = MagicMock()
    mock_setup_logging.return_value = mock_logger
    
    mock_fetch.side_effect = ValidationError("Invalid input")
    
    run(
        username="testuser",
        repos=["org/repo1"],
        start="2025-01-01"
    )
    
    mock_exit.assert_called_once_with(1)


@patch('ghweekly.cli.setup_logging')
@patch('ghweekly.cli.validate_date')
@patch('sys.exit')
def test_run_with_date_validation_error(mock_exit, mock_validate, mock_setup_logging):
    """Test run with date validation error."""
    mock_logger = MagicMock()
    mock_setup_logging.return_value = mock_logger
    
    mock_validate.side_effect = ValidationError("Invalid date")
    
    run(
        username="testuser",
        repos=["org/repo1"],
        start="invalid-date"
    )
    
    mock_exit.assert_called_once_with(1)


@patch('ghweekly.cli.setup_logging')
@patch('ghweekly.cli.fetch_weekly_commits')
@patch('sys.exit')
def test_run_with_unexpected_error(mock_exit, mock_fetch, mock_setup_logging):
    """Test run with unexpected error."""
    mock_logger = MagicMock()
    mock_setup_logging.return_value = mock_logger
    
    mock_fetch.side_effect = Exception("Unexpected error")
    
    run(
        username="testuser",
        repos=["org/repo1"],
        start="2025-01-01"
    )
    
    mock_exit.assert_called_once_with(1)


@patch('ghweekly.cli.run')
@patch('sys.argv')
def test_main_function(mock_argv, mock_run):
    """Test main function calls run with parsed arguments."""
    mock_argv.__getitem__.return_value = [
        "ghweekly",
        "--username", "testuser",
        "--repos", "org/repo1"
    ]
    
    with patch('ghweekly.cli.create_parser') as mock_create_parser:
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_args.username = "testuser"
        mock_args.repos = ["org/repo1"]
        mock_args.start = "2025-01-01"
        mock_args.end = None
        mock_args.token = None
        mock_args.plot = False
        mock_args.output = None
        mock_args.verbose = False
        
        mock_parser.parse_args.return_value = mock_args
        mock_create_parser.return_value = mock_parser
        
        main()
        
        mock_run.assert_called_once_with(
            username="testuser",
            repos=["org/repo1"],
            start="2025-01-01",
            end=None,
            token=None,
            plot=False,
            output=None,
            verbose=False
        )


# Integration tests (subprocess calls)
def test_cli_help():
    """Test CLI help command."""
    result = subprocess.run(
        [sys.executable, "-m", "ghweekly.cli", "--help"], 
        capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "usage:" in result.stdout
    assert "--username" in result.stdout


def test_cli_runs(monkeypatch):
    """Test CLI execution with basic arguments."""
    # Patch environment to avoid real API calls
    monkeypatch.setenv("GH_TOKEN", "dummy")
    result = subprocess.run(
        [
            sys.executable,
            "-m", "ghweekly.cli",
            "--username",
            "testuser",
            "--repos",
            "org/repo1",
            "--start",
            "2025-01-01",
            "--end",
            "2025-05-01",
        ],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    assert result.returncode == 0
    assert "repo1" in result.stdout


def test_cli_plot(monkeypatch):
    """Test CLI execution with plotting enabled."""
    # Use a non-interactive backend for matplotlib
    monkeypatch.setenv("MPLBACKEND", "Agg")
    monkeypatch.setenv("GH_TOKEN", "dummy")
    
    result = subprocess.run(
        [
            sys.executable,
            "-m", "ghweekly.cli",
            "--username",
            "testuser",
            "--repos",
            "org/repo1",
            "--start",
            "2025-01-01",
            "--end",
            "2025-05-01",
            "--plot",
        ],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    assert result.returncode == 0
    assert "repo1" in result.stdout or "repo1" in result.stderr
    assert os.path.exists("weekly_commits.png")
    
    # Clean up
    if os.path.exists("weekly_commits.png"):
        os.remove("weekly_commits.png")


def test_cli_default_start(monkeypatch):
    """Test CLI with default start date."""
    monkeypatch.setenv("GH_TOKEN", "dummy")
    
    result = subprocess.run(
        [
            sys.executable,
            "-m", "ghweekly.cli",
            "--username", "testuser",
            "--repos", "org/repo1",
            "--end", "2025-05-01"
        ],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    assert result.returncode == 0
    assert "repo1" in result.stdout


def test_cli_missing_args():
    """Test CLI with missing required arguments."""
    result = subprocess.run(
        [sys.executable, "-m", "ghweekly.cli", "--username", "testuser"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "usage:" in result.stderr.lower() or "error" in result.stderr.lower()
