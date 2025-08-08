import os
import yaml
from .defaults import get_defaults
from .schemas import get_schema
from typing import Dict, Any

CONFIG_DIR = os.path.join(os.path.dirname(__file__), '../config')
CONFIG_FULL_PATH = os.path.join(CONFIG_DIR, 'config_full.yml')

class ConfigManager:
    @staticmethod
<<<<<<< HEAD
=======
    def validate_config(config: dict, schema: dict) -> bool:
        """Valide la configuration selon le schéma Cerberus."""
        from cerberus import Validator
        v = Validator(schema)
        return v.validate(config)

    @staticmethod
    def get_config(service: str = None, section: str = None, keys: list = None, multi_sections: list = None, with_section: bool = True, defaults: dict = None) -> dict:
        """
        Restitue la configuration selon les options :
        - service : nom du service/module
        - section : section à extraire
        - keys : liste d'arguments à extraire
        - multi_sections : liste de sections à extraire
        - with_section : inclure la section racine ou non
        - defaults : valeurs par défaut à appliquer si manquantes
        """
        config = {}
        if service:
            config = ConfigManager.get_service_config(service)
        else:
            config = ConfigManager.get_full_config()
        # Substitution des variables d'environnement
        def substitute_env(val):
            if isinstance(val, str) and val.startswith('$'):
                return os.environ.get(val[1:], val)
            return val
        def recursive_substitute(d):
            if isinstance(d, dict):
                return {k: recursive_substitute(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [recursive_substitute(v) for v in d]
            else:
                return substitute_env(d)
        config = recursive_substitute(config)
        # Application des valeurs par défaut
        if defaults:
            config = ConfigManager._deep_merge_dicts(defaults, config)
        # Extraction selon options
        if multi_sections:
            result = {s: config.get(s, {}) for s in multi_sections}
            if keys:
                for s in result:
                    result[s] = {k: result[s].get(k) for k in keys if k in result[s]}
            return result
        if section:
            sect = config.get(section, {})
            if keys:
                sect = {k: sect.get(k) for k in keys if k in sect}
            return {section: sect} if with_section else sect
        if keys:
            flat = {}
            for k in keys:
                for sect in config:
                    if k in config[sect]:
                        flat[k] = config[sect][k]
            return flat
        return config

    @staticmethod
    def reload_on_change(callback=None):
        """Squelette de reload dynamique sur changement de fichiers (à compléter avec watchdog)."""
        try:
            import watchdog.events
            import watchdog.observers
        except ImportError:
            print("watchdog non installé")
            return
        class Handler(watchdog.events.FileSystemEventHandler):
            def on_modified(self, event):
                if event.src_path.endswith('config.yml'):
                    if callback:
                        callback()
        observer = watchdog.observers.Observer()
        observer.schedule(Handler(), CONFIG_DIR, recursive=True)
        observer.start()
        print("Surveillance des fichiers de configuration activée.")
    @staticmethod
>>>>>>> 358b958 (	modified:   src/core/config_manager.py)
    def get_service_config(service: str) -> Dict[str, Any]:
        """Retourne la configuration d'un service/module spécifique."""
        path = os.path.join(CONFIG_DIR, service, 'config.yml')
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Erreur lecture config {service}: {e}")
            return {}

    @staticmethod
    def set_service_config_arg(service: str, section: str, key: str, value: Any) -> bool:
<<<<<<< HEAD
        """Ajoute ou modifie un argument dans une section du fichier config individuel."""
        path = os.path.join(CONFIG_DIR, service, 'config.yml')
        config = ConfigManager.get_service_config(service)
        if section not in config:
            config[section] = {}
        config[section][key] = value
=======
        """Ajoute ou modifie un argument dans une section du fichier config individuel, avec validation et valeurs par défaut."""
        path = os.path.join(CONFIG_DIR, service, 'config.yml')
        config = ConfigManager.get_service_config(service)
        defaults = get_defaults(service)
        schema = get_schema(service)
        # Appliquer valeur par défaut si section absente
        if section not in config:
            config[section] = defaults.get(section, {})
        config[section][key] = value
        # Validation
        valid = True
        if section in schema:
            from cerberus import Validator
            v = Validator({key: schema[section].get(key, {})})
            valid = v.validate({key: value})
        if not valid:
            print(f"Validation échouée pour {service}.{section}.{key}: {value}")
            return False
>>>>>>> 358b958 (	modified:   src/core/config_manager.py)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(config, f)
            return True
        except Exception as e:
            print(f"Erreur écriture config {service}: {e}")
            return False

    @staticmethod
    def delete_service_config_arg(service: str, section: str, key: str) -> bool:
        """Supprime un argument d'une section du fichier config individuel."""
        path = os.path.join(CONFIG_DIR, service, 'config.yml')
        config = ConfigManager.get_service_config(service)
        if section in config and key in config[section]:
            del config[section][key]
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(config, f)
                return True
            except Exception as e:
                print(f"Erreur écriture config {service}: {e}")
                return False
        return False

    @staticmethod
    def delete_service_config_section(service: str, section: str) -> bool:
        """Supprime une section entière du fichier config individuel."""
        path = os.path.join(CONFIG_DIR, service, 'config.yml')
        config = ConfigManager.get_service_config(service)
        if section in config:
            del config[section]
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(config, f)
                return True
            except Exception as e:
                print(f"Erreur écriture config {service}: {e}")
                return False
        return False
    """
    Gestionnaire centralisé des configurations.
    - Fusionne tous les fichiers config.yml de src/config/*/
    - Exclut config_full.yml
    - Met à jour et lit le fichier fusionné
    """
    @staticmethod
    def _find_config_files() -> list:
        files = []
        for root, dirs, filenames in os.walk(CONFIG_DIR):
            for filename in filenames:
                if filename == 'config.yml' and root != CONFIG_DIR:
                    files.append(os.path.join(root, filename))
        return files

    @staticmethod
    def _deep_merge_dicts(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        """Fusion profonde de deux dictionnaires."""
        result = dict(a)
        for k, v in b.items():
            if (
                k in result
                and isinstance(result[k], dict)
                and isinstance(v, dict)
            ):
                result[k] = ConfigManager._deep_merge_dicts(result[k], v)
            else:
                result[k] = v
        return result

    @staticmethod
    def merge_configs() -> Dict[str, Any]:
        merged = {}
        for file in ConfigManager._find_config_files():
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                    merged = ConfigManager._deep_merge_dicts(merged, data)
            except FileNotFoundError:
                print(f"File not found: {file}")
            except PermissionError:
                print(f"Permission denied when reading {file}")
            except yaml.YAMLError as e:
                print(f"YAML error in {file}: {e}")
            except OSError as e:
                print(f"Error reading {file}: {e}")
        return merged

    @staticmethod
    def update_full_config() -> bool:
        """Écrit le fichier de configuration fusionné sur le disque."""
        merged = ConfigManager.merge_configs()
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(CONFIG_FULL_PATH, 'w', encoding='utf-8') as f:
                yaml.safe_dump(merged, f)
            return True
        except FileNotFoundError:
            print(f"File not found: {CONFIG_FULL_PATH}")
        except PermissionError:
            print(f"Permission denied: {CONFIG_FULL_PATH}")
        except yaml.YAMLError as e:
            print(f"YAML error while writing {CONFIG_FULL_PATH}: {e}")
        except OSError as e:
            print(f"Error writing {CONFIG_FULL_PATH}: {e}")
        return False

    @staticmethod
    def get_full_config() -> Dict[str, Any]:
        if not os.path.exists(CONFIG_FULL_PATH):
            ConfigManager.update_full_config()
        try:
            with open(CONFIG_FULL_PATH, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(f"File not found: {CONFIG_FULL_PATH}")
            return {}
        except PermissionError:
            print(f"Permission denied: {CONFIG_FULL_PATH}")
            return {}
        except yaml.YAMLError as e:
            print(f"YAML error in {CONFIG_FULL_PATH}: {e}")
            return {}

    # Monitoring skeleton (to be completed)
    @staticmethod
    def watch_config_changes():
        pass  # To implement with watchdog or polling
