import sys
import os
import traceback
import json

class ExceptionFormatter:
    """
    Formateur universel pour exceptions, selon la cible d’affichage.
    """
    LEVEL_STYLES = {
        'info': {'ansi': '\033[94m', 'html': 'color:blue;', 'emoji': 'ℹ️'},
        'warning': {'ansi': '\033[93m', 'html': 'color:orange;', 'emoji': '⚠️'},
        'error': {'ansi': '\033[91m', 'html': 'color:red;', 'emoji': '❌'},
        'critical': {'ansi': '\033[41m', 'html': 'background:red;color:white;', 'emoji': '🔥'},
        'success': {'ansi': '\033[92m', 'html': 'color:green;', 'emoji': '✅'},
    }
    ANSI_RESET = '\033[0m'
    CUSTOM_TEMPLATES = {}

    @classmethod
    def register_template(cls, name, func):
        """Enregistre un template personnalisé (func: (message, **kwargs) -> str)."""
        cls.CUSTOM_TEMPLATES[name] = func

    @classmethod
    def format(cls, message, level='error', target='plain', template=None, title=None, details=None):
        style = cls.LEVEL_STYLES.get(level, cls.LEVEL_STYLES['error'])
        if template and template in cls.CUSTOM_TEMPLATES:
            return cls.CUSTOM_TEMPLATES[template](message, level=level, target=target, title=title, details=details)
        if target == 'plain':
            return f"{style['emoji']} {title+': ' if title else ''}{message}"
        if target == 'terminal':
            return f"{style['ansi']}{title+': ' if title else ''}{message}{cls.ANSI_RESET}"
        if target == 'html':
            return f"<div style='{style['html']}'><strong>{title if title else ''}</strong> {message}</div>"
        if target == 'markdown':
            return f"**{title if title else ''}** {message}"
        if target == 'json':
            return json.dumps({'level': level, 'title': title, 'message': message, 'details': details})
        if target == 'rich':
            return f"[bold {level}]{title+': ' if title else ''}{message}[/bold {level}]"
        return message

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

    def format_message(self, target=None, level=None, template=None, title=None, details=None):
        level = level or getattr(self, 'level', 'error')
        target = target or self.fmt
        title = title or self.__class__.__name__
        return ExceptionFormatter.format(self.message, level=level, target=target, template=template, title=title, details=details)

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

# Exemple d’enregistrement d’un template personnalisé
# def my_template(msg, **kwargs):
#     return f"*** {kwargs.get('title', '')} ***\n{msg}\n---"
# ExceptionFormatter.register_template('starred', my_template)
