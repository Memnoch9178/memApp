import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from core.exceptions import ConfigException

CONFIG_DIR = os.path.join(os.path.dirname(__file__), '../../config')

class ConfigReload:
    """
    Module de surveillance et reload dynamique des fichiers de configuration.
    """
    class Handler(FileSystemEventHandler):
        def __init__(self, callback):
            super().__init__()
            self.callback = callback
        def on_modified(self, event):
            if event.src_path.endswith('config.yml'):
                if self.callback:
                    self.callback()
    @staticmethod
    def reload_on_change(callback=None):
        """
        Active la surveillance des fichiers de configuration.
        Args:
            callback (callable): Fonction à appeler en cas de modification.
        Raises:
            ConfigException: en cas d’erreur d’initialisation.
        """
        try:
            observer = Observer()
            observer.schedule(ConfigReload.Handler(callback), CONFIG_DIR, recursive=True)
            observer.start()
            print("Config file change monitoring enabled.")
        except Exception as e:
            raise ConfigException(f"Erreur initialisation watchdog: {e}")
