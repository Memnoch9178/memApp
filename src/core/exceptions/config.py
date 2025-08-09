from .base import MemAppException


class ConfigException(MemAppException):
    """Exception spécifique à la configuration."""

    default_message = "Erreur de configuration."
