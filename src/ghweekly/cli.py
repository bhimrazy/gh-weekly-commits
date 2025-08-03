"""Command-line interface for ghweekly."""

import argparse
import sys
from datetime import datetime
from typing import Optional

try:
    from .main import fetch_weekly_commits
    from .plotting import create_weekly_commits_plot
    from .exceptions import GHWeeklyError, ValidationError
    from .utils import setup_logging
except ImportError:
    # Handle direct execution
    import os

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ghweekly.main import fetch_weekly_commits
    from ghweekly.plotting import create_weekly_commits_plot
    from ghweekly.exceptions import GHWeeklyError, ValidationError
    from ghweekly.utils import setup_logging


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="Fetch weekly GitHub commits for a user across multiple repos.",
        prog="ghweekly",
    )

    parser.add_argument("--username", required=True, help="GitHub username")

    parser.add_argument(
        "--repos",
        nargs="+",
        required=True,
        help="List of GitHub repositories (org/repo)",
    )

    current_year_start = f"{datetime.now().year}-01-01"
    parser.add_argument(
        "--start",
        required=False,
        default=current_year_start,
        help=f"Start date (YYYY-MM-DD), default: {current_year_start}",
    )

    parser.add_argument(
        "--end",
        default=None,
        help="End date (YYYY-MM-DD), default: today",
    )

    parser.add_argument(
        "--token", help="GitHub token (optional, for higher rate limits)"
    )

    parser.add_argument("--plot", action="store_true", help="Show plot")

    parser.add_argument(
        "--output", help="Output file for plot (default: weekly_commits.png)"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    return parser


def validate_date(date_string: str) -> datetime:
    """Validate and parse date string.

    Args:
        date_string: Date string in YYYY-MM-DD format

    Returns:
        Parsed datetime object

    Raises:
        ValidationError: If date format is invalid
    """
    try:
        return datetime.fromisoformat(date_string)
    except ValueError as e:
        raise ValidationError(f"Invalid date format '{date_string}': {e}")


def run(
    username: str,
    repos: list,
    start: str,
    end: Optional[str] = None,
    token: Optional[str] = None,
    plot: bool = False,
    output: Optional[str] = None,
    verbose: bool = False,
) -> None:
    """Run the main application logic.

    Args:
        username: GitHub username
        repos: List of repository names
        start: Start date string
        end: End date string (optional)
        token: GitHub token (optional)
        plot: Whether to show/save plot
        output: Output file for plot
        verbose: Enable verbose logging
    """
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    logger = setup_logging(log_level)

    try:
        # Validate and parse dates
        start_date = validate_date(start)
        end_date = validate_date(end) if end else datetime.now()

        # Prepare headers
        headers = {"Authorization": f"token {token}"} if token else {}

        # Fetch data
        logger.info(f"Fetching weekly commits for {username}")
        df = fetch_weekly_commits(
            username=username,
            repos=repos,
            start=start_date,
            end=end_date,
            headers=headers,
        )

        # Display data
        print(df)

        # Generate plot if requested
        if plot:
            output_file = output or "weekly_commits.png"
            logger.info(f"Creating plot: {output_file}")

            # Import matplotlib only when needed
            import matplotlib

            matplotlib.use("Agg")  # Use non-interactive backend

            create_weekly_commits_plot(
                df=df,
                username=username,
                output_file=output_file,
                show_plot=False,  # Don't show in CLI mode
            )
            logger.info(f"Plot saved to {output_file}")

    except GHWeeklyError as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    run(
        username=args.username,
        repos=args.repos,
        start=args.start,
        end=args.end,
        token=args.token,
        plot=args.plot,
        output=args.output,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
