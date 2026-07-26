class ServiceError(Exception):
    """Base exception for service-layer failures."""


class CapacityFullError(ServiceError):
    """Raised when challenge registration capacity is full."""


class UserBlockedError(ServiceError):
    """Raised when a blocked user tries to use the system."""


class NotRegisteredError(ServiceError):
    """Raised when an unregistered user tries to submit an answer."""


class NoActiveChallengeError(ServiceError):
    """Raised when no challenge is available for submissions."""


class ValidationError(ServiceError):
    """Raised when submitted business data is invalid."""
