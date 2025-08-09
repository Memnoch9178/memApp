from .base import MemAppException
class WatchdogException(MemAppException):
    """Exception spécifique à Watchdog."""
    default_message = "Erreur Watchdog."
