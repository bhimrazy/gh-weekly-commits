"""Utilities for the ghweekly package."""

import logging
from typing import List


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Set up logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("ghweekly")
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger


def validate_repo_format(repos: List[str]) -> None:
    """Validate that repository names are in correct format.
    
    Args:
        repos: List of repository names in 'owner/repo' format
        
    Raises:
        ValidationError: If any repo name is invalid
    """
    from .exceptions import ValidationError
    
    for repo in repos:
        if not repo or "/" not in repo:
            raise ValidationError(f"Invalid repository format: '{repo}'. Expected 'owner/repo'.")
        
        parts = repo.split("/")
        if len(parts) != 2 or not all(part.strip() for part in parts) or any(part != part.strip() for part in parts):
            raise ValidationError(f"Invalid repository format: '{repo}'. Expected 'owner/repo'.")


def get_repo_short_name(repo: str) -> str:
    """Extract short name from repository string.
    
    Args:
        repo: Repository name in 'owner/repo' format
        
    Returns:
        Short repository name (everything after the last '/')
    """
    return repo.split("/")[-1]
