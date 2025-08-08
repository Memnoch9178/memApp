import sys
import os
import traceback

class MemAppException(Exception):
    """
    Exception de base pour memApp, avec gestion du contexte et formatage du message.
    """
    default_message = "Une erreur est survenue dans memApp."
    formats = ['plain', 'html', 'rich']

    def __init__(self, message=None, context=None, fmt='plain', **kwargs):
        self.context = context or self.detect_context()
        self.fmt = fmt if fmt in self.formats else 'plain'
        self.message = message or self.default_message
        self.extra = kwargs
        super().__init__(self.message)

    def detect_context(self):
        # Détection simple du contexte d'exécution
        if 'REQUEST_METHOD' in os.environ:
            return 'api'
        if sys.stdin.isatty():
            return 'cli'
        return 'unknown'

    def format_message(self):
        if self.fmt == 'html':
            return f"<div class='error'>{self.message}</div>"
        elif self.fmt == 'rich':
            return f"[bold red]Erreur:[/bold red] {self.message}"
        return self.message

    def __str__(self):
        return self.format_message()

class ConfigException(MemAppException):
    default_message = "Erreur de configuration."

class PluginException(MemAppException):
    default_message = "Erreur dans un plugin."

class UtilsException(MemAppException):
    default_message = "Erreur dans un utilitaire."

class CoreException(MemAppException):
    default_message = "Erreur dans le cœur de l’application."

# Exemple d’extension pour un module spécifique
class WatchdogException(MemAppException):
    default_message = "Erreur Watchdog."

# Système pour lever l’exception du contexte automatiquement

def raise_contextual_exception(exc_class, message=None, fmt=None, **kwargs):
    exc = exc_class(message=message, fmt=fmt, **kwargs)
    raise exc

# Utilisation possible :
# raise_contextual_exception(ConfigException, "Fichier de config introuvable", fmt='html')
