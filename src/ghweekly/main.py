"""Main module for fetching GitHub commit data."""

import time
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
import requests
import requests.exceptions

from .exceptions import APIError, NetworkError, ValidationError
from .utils import get_repo_short_name, setup_logging, validate_repo_format

logger = setup_logging()


def fetch_commits_for_repo(
    full_repo: str,
    username: str,
    start: datetime,
    end: datetime,
    headers: Optional[Dict[str, str]] = None,
    max_retries: int = 3,
    retry_delay: float = 1.0,
) -> List[datetime]:
    """Fetch commit dates for a single repository.
    
    Args:
        full_repo: Repository name in 'owner/repo' format
        username: GitHub username to filter commits by
        start: Start date for commit search
        end: End date for commit search
        headers: HTTP headers for API requests
        max_retries: Maximum number of retries for failed requests
        retry_delay: Delay between retries in seconds
        
    Returns:
        List of commit dates
        
    Raises:
        APIError: If GitHub API returns an error
        NetworkError: If network request fails
    """
    commit_dates: List[datetime] = []
    page = 1
    max_pages = 100  # Safety limit to prevent infinite loops
    
    while page <= max_pages:
        logger.debug(f"Fetching page {page} for {full_repo}")
        resp = None
        for attempt in range(max_retries + 1):
            try:
                resp = requests.get(
                    f"https://api.github.com/repos/{full_repo}/commits",
                    headers=headers or {},
                    params={
                        "author": username,
                        "since": start.isoformat() + "Z",
                        "until": end.isoformat() + "Z",
                        "per_page": 100,
                        "page": page,
                    },
                    timeout=30,
                )
                break
            except requests.exceptions.RequestException as e:
                if attempt == max_retries:
                    logger.error(f"Network error fetching {full_repo} after {max_retries} retries: {e}")
                    raise NetworkError(f"Failed to fetch data for {full_repo}: {e}")
                logger.warning(f"Retry {attempt + 1}/{max_retries} for {full_repo}: {e}")
                time.sleep(retry_delay)
        
        # If resp is still None after all retries, something went wrong
        if resp is None:
            logger.error(f"Failed to get response for {full_repo}")
            break
        
        if resp.status_code == 404:
            logger.warning(f"Repository not found or not accessible: {full_repo}")
            break
        elif resp.status_code == 403:
            logger.warning(f"Rate limit or access denied for {full_repo}: {resp.status_code}")
            break
        elif resp.status_code != 200:
            logger.error(f"API error fetching {full_repo}: HTTP {resp.status_code}")
            raise APIError(resp.status_code, f"Failed to fetch {full_repo}")

        try:
            data = resp.json()
            logger.debug(f"Page {page} returned {len(data)} commits for {full_repo}")
        except ValueError as e:
            logger.error(f"Invalid JSON response for {full_repo}: {e}")
            break
            
        if not data:
            logger.debug(f"No more data on page {page}, ending pagination for {full_repo}")
            break

        for commit in data:
            try:
                commit_date_str = commit["commit"]["author"]["date"]
                dt = datetime.fromisoformat(
                    commit_date_str.replace("Z", "+00:00")
                ).replace(tzinfo=None)
                commit_dates.append(dt)
            except (KeyError, ValueError) as e:
                logger.warning(f"Malformed commit data in {full_repo}: {e}")
                continue

        page += 1
        
        # Respect rate limits
        if not headers or "Authorization" not in headers:
            time.sleep(0.1)  # Small delay for unauthenticated requests

    logger.info(f"Fetched {len(commit_dates)} commits for {full_repo}")
    return commit_dates


def fetch_weekly_commits(
    username: str,
    repos: List[str],
    start: datetime,
    end: datetime,
    headers: Optional[Dict[str, str]] = None,
) -> pd.DataFrame:
    """Fetch weekly commit data for multiple repositories.
    
    Args:
        username: GitHub username to filter commits by
        repos: List of repository names in 'owner/repo' format
        start: Start date for commit search
        end: End date for commit search
        headers: HTTP headers for API requests (e.g., for authentication)
        
    Returns:
        DataFrame with weekly commit counts, indexed by week start date
        
    Raises:
        ValidationError: If input parameters are invalid
    """
    # Validate inputs
    if not username or not username.strip():
        raise ValidationError("Username cannot be empty")
    
    if end < start:
        raise ValidationError("End date must be after start date")
    
    validate_repo_format(repos)
    
    # Calculate week boundaries
    offset_start = (0 - start.weekday()) % 7
    first_monday = pd.Timestamp(start) + pd.Timedelta(days=offset_start)

    offset_end = (0 - end.weekday()) % 7
    last_monday = pd.Timestamp(end) + pd.Timedelta(days=offset_end)

    weeks = pd.date_range(start=first_monday, end=last_monday, freq="7D")
    
    # Initialize DataFrame
    repo_short_names = [get_repo_short_name(repo) for repo in repos]
    df = pd.DataFrame(0, index=weeks, columns=repo_short_names)

    logger.info(f"Fetching commits for {len(repos)} repositories from {start.date()} to {end.date()}")

    for full_repo in repos:
        short_name = get_repo_short_name(full_repo)
        
        try:
            commit_dates = fetch_commits_for_repo(
                full_repo, username, start, end, headers
            )
            
            if commit_dates:
                # Create series and resample to weekly
                s = pd.Series(1, index=pd.to_datetime(commit_dates))
                weekly = s.resample("W-MON", label="left", closed="left").sum()
                weekly = weekly.reindex(weeks, fill_value=0)
                df[short_name] = weekly
            else:
                logger.info(f"No commits found for {full_repo}")
                
        except (APIError, NetworkError) as e:
            logger.error(f"Failed to fetch data for {full_repo}: {e}")
            # Continue with other repositories
            continue

    return df
