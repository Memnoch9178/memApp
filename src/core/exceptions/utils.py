from .base import MemAppException


class UtilsException(MemAppException):
    """Exception spécifique aux utilitaires."""

    default_message = "Erreur dans un utilitaire."
