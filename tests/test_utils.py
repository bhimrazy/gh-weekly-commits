"""Tests for ghweekly.utils module."""

import logging

import pytest

from ghweekly.exceptions import ValidationError
from ghweekly.utils import get_repo_short_name, setup_logging, validate_repo_format


# Test setup_logging function
def test_setup_logging_default_level():
    """Test default logging level is INFO."""
    logger = setup_logging()
    assert logger.level == logging.INFO
    assert logger.name == "ghweekly"


def test_setup_logging_custom_level():
    """Test custom logging level."""
    logger = setup_logging("DEBUG")
    assert logger.level == logging.DEBUG


def test_setup_logging_invalid_level():
    """Test invalid logging level falls back to INFO."""
    logger = setup_logging("INVALID")
    assert logger.level == logging.INFO


def test_setup_logging_lowercase_level():
    """Test lowercase logging level."""
    logger = setup_logging("debug")
    assert logger.level == logging.DEBUG


def test_setup_logging_warning_level():
    """Test WARNING logging level."""
    logger = setup_logging("WARNING")
    assert logger.level == logging.WARNING


def test_setup_logging_error_level():
    """Test ERROR logging level."""
    logger = setup_logging("ERROR")
    assert logger.level == logging.ERROR


def test_setup_logging_handler_not_duplicated():
    """Test that handlers are not duplicated on multiple calls."""
    logger1 = setup_logging()
    initial_handler_count = len(logger1.handlers)

    logger2 = setup_logging()
    assert len(logger2.handlers) == initial_handler_count
    assert logger1 is logger2  # Should return the same logger instance


# Test validate_repo_format function
def test_validate_repo_format_valid():
    """Test valid repository formats."""
    valid_repos = [
        "owner/repo",
        "github/octocat",
        "Lightning-AI/litdata",
        "123/456",
        "user-name/repo-name",
        "org_name/repo_name",
    ]
    # Should not raise any exception
    validate_repo_format(valid_repos)


def test_validate_repo_format_invalid_no_slash():
    """Test invalid format without slash."""
    with pytest.raises(
        ValidationError, match="Invalid repository format.*Expected 'owner/repo'"
    ):
        validate_repo_format(["owner"])


def test_validate_repo_format_invalid_empty_owner():
    """Test invalid format with empty owner."""
    with pytest.raises(
        ValidationError, match="Invalid repository format.*Expected 'owner/repo'"
    ):
        validate_repo_format(["/repo"])


def test_validate_repo_format_invalid_empty_repo():
    """Test invalid format with empty repo name."""
    with pytest.raises(
        ValidationError, match="Invalid repository format.*Expected 'owner/repo'"
    ):
        validate_repo_format(["owner/"])


def test_validate_repo_format_invalid_empty_string():
    """Test invalid format with empty string."""
    with pytest.raises(
        ValidationError, match="Invalid repository format.*Expected 'owner/repo'"
    ):
        validate_repo_format([""])


def test_validate_repo_format_invalid_too_many_parts():
    """Test invalid format with too many parts."""
    with pytest.raises(
        ValidationError, match="Invalid repository format.*Expected 'owner/repo'"
    ):
        validate_repo_format(["owner/repo/extra"])


def test_validate_repo_format_invalid_whitespace_only():
    """Test invalid format with only whitespace."""
    with pytest.raises(
        ValidationError, match="Invalid repository format.*Expected 'owner/repo'"
    ):
        validate_repo_format([" / "])


def test_validate_repo_format_empty_list():
    """Test empty repository list."""
    # Should not raise any exception
    validate_repo_format([])


def test_validate_repo_format_mixed_valid_invalid():
    """Test list with mix of valid and invalid repos."""
    mixed_repos = ["valid/repo", "invalid"]
    with pytest.raises(ValidationError):
        validate_repo_format(mixed_repos)


def test_validate_repo_format_none_in_list():
    """Test list containing None values."""
    with pytest.raises(ValidationError):
        validate_repo_format([None])


def test_validate_repo_format_whitespace_in_parts():
    """Test repo format with whitespace in parts."""
    with pytest.raises(ValidationError):
        validate_repo_format(["owner /repo"])

    with pytest.raises(ValidationError):
        validate_repo_format(["owner/ repo"])


# Test get_repo_short_name function
def test_get_repo_short_name_simple():
    """Test simple repository name extraction."""
    assert get_repo_short_name("owner/repo") == "repo"


def test_get_repo_short_name_complex():
    """Test complex repository name extraction."""
    assert get_repo_short_name("Lightning-AI/pytorch-lightning") == "pytorch-lightning"


def test_get_repo_short_name_nested_path_like():
    """Test repo name that looks like a nested path."""
    assert get_repo_short_name("org/very/deep/repo") == "repo"


def test_get_repo_short_name_numeric():
    """Test numeric owner and repo names."""
    assert get_repo_short_name("123/456") == "456"


def test_get_repo_short_name_single_character():
    """Test single character names."""
    assert get_repo_short_name("a/b") == "b"


def test_get_repo_short_name_with_dashes():
    """Test repo names with dashes."""
    assert get_repo_short_name("some-org/some-repo-name") == "some-repo-name"


def test_get_repo_short_name_with_underscores():
    """Test repo names with underscores."""
    assert get_repo_short_name("some_org/some_repo_name") == "some_repo_name"


def test_get_repo_short_name_with_dots():
    """Test repo names with dots."""
    assert get_repo_short_name("owner/repo.name") == "repo.name"


def test_get_repo_short_name_long_path():
    """Test with very long path-like repo name."""
    long_repo = "org/path/to/very/deep/nested/repository"
    assert get_repo_short_name(long_repo) == "repository"
