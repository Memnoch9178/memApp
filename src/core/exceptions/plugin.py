from .base import MemAppException
class PluginException(MemAppException):
    """Exception spécifique aux plugins."""
    default_message = "Erreur dans un plugin."
