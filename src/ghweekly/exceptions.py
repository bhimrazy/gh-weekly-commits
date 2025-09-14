"""Custom exceptions for ghweekly package."""


class GHWeeklyError(Exception):
    """Base exception for ghweekly package."""

    pass


class APIError(GHWeeklyError):
    """Exception raised when GitHub API returns an error."""

    def __init__(self, status_code: int, message: str = ""):
        self.status_code = status_code
        self.message = message
        super().__init__(f"GitHub API error {status_code}: {message}")


class ValidationError(GHWeeklyError):
    """Exception raised when input validation fails."""

    pass


class NetworkError(GHWeeklyError):
    """Exception raised when network request fails."""

    pass
