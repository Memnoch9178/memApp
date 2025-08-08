import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

CONFIG_DIR = os.path.join(os.path.dirname(__file__), '../config')

class ConfigReload:
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
        observer = Observer()
        observer.schedule(ConfigReload.Handler(callback), CONFIG_DIR, recursive=True)
        observer.start()
        print("Config file change monitoring enabled.")
