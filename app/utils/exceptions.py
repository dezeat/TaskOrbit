"""Custom exceptions for TaskOrbit application."""


class TaskOrbitError(Exception):
    """Base class for general exceptions in TaskOrbit app."""

    def __init__(self, msg: str = "") -> None:
        """Inits a TaskOrbitException.

        Args:
            msg (str, optional): Exception message. Defaults to "".
        """
        self.msg = msg

    def __str__(self) -> str:
        """Return the stored exception message for display.

        Keeps the string representation simple so exceptions are readable
        in logs and traces.
        """
        return self.msg


class DBConfigError(TaskOrbitError):
    """Exception raised when parsing of config fails."""


class DBSetupError(TaskOrbitError):
    """Exception raised when setup of DB."""
