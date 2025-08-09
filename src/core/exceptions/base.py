import sys
import os
import json
from ..templates import ExceptionTemplates

class ExceptionFormatter:
    # ...existing code...
    pass

class MemAppException(Exception):
    default_message = "Une erreur est survenue dans memApp."
    formats = ['plain', 'html', 'rich']
    def __init__(self, message=None, context=None, fmt='plain', **kwargs):
        self.context = context or self.detect_context()
        self.fmt = fmt if fmt in self.formats else 'plain'
        self.message = message or self.default_message
        self.extra = kwargs
        super().__init__(self.message)
    def detect_context(self):
        if 'REQUEST_METHOD' in os.environ:
            return 'api'
        if sys.stdin.isatty():
            return 'cli'
        return 'unknown'
    def format_message(self, target=None, level=None, template=None, title=None, details=None):
        # Utilise ExceptionTemplates si template fourni
        if template and ExceptionTemplates.get(template):
            return ExceptionTemplates.get(template)(self.message, level=level, target=target, title=title, details=details)
        # ... sinon fallback sur format simple ...
        return self.message
    def __str__(self):
        return self.format_message()

# Ce module doit contenir uniquement la base des exceptions et le formateur.
