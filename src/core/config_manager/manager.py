import os
import yaml
from .validation import ConfigValidation
from .merge import ConfigMerge
from .reload import ConfigReload
from ..defaults import get_defaults
from ..schemas import get_schema
from src.core.exceptions import ConfigException
from typing import Dict, Any
from pydantic import BaseModel, ValidationError
from rich import print as rprint
from dotenv import load_dotenv
import glob

# Chargement automatique des variables d'environnement
load_dotenv()

CONFIG_DIR = os.path.join(os.path.dirname(__file__), '../../config')
CONFIG_FULL_PATH = os.path.join(CONFIG_DIR, 'config_full.yml')

def _find_schema_files():
    return glob.glob(os.path.join(CONFIG_DIR, "**/schema.yml"), recursive=True)

def _find_defaults_files():
    return glob.glob(os.path.join(CONFIG_DIR, "**/defaults.yml"), recursive=True)

class ServiceConfigModel(BaseModel):
    # Exemple de modèle Pydantic pour une section de config
    enabled: bool = True
    interval: int = 10
    log_path: str = '/var/log/memapp/service.log'

class ConfigManager:
    """
    Gestionnaire centralisé des configurations.
    - Fusionne tous les fichiers config.yml de src/config/*/
    - Exclut config_full.yml
    - Met à jour et lit le fichier fusionné
    - Permet la gestion fine des arguments et sections
    """
    @staticmethod
    def validate_config(config: dict, schema: dict) -> bool:
        """
        Valide la configuration selon le schéma Cerberus.
        Args:
            config (dict): Configuration à valider.
            schema (dict): Schéma Cerberus.
        Returns:
            bool: True si valide, False sinon.
        """
        return ConfigValidation.validate_config(config, schema)

    @staticmethod
    def get_config(service: str = None, section: str = None, keys: list = None, multi_sections: list = None, with_section: bool = True, defaults: dict = None) -> dict:
        """
        Restitue la configuration selon les options.
        Args:
            service (str): Nom du service/module.
            section (str): Section à extraire.
            keys (list): Liste d'arguments à extraire.
            multi_sections (list): Liste de sections à extraire.
            with_section (bool): Inclure la section racine ou non.
            defaults (dict): Valeurs par défaut à appliquer si manquantes.
        Returns:
            dict: Configuration extraite.
        """
        config = {}
        if service:
            config = ConfigManager.get_service_config(service)
        else:
            config = ConfigManager.get_full_config()
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
        if defaults:
            config = ConfigMerge.deep_merge_dicts(defaults, config)
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
        """
        Active la surveillance dynamique des fichiers de configuration.
        Args:
            callback (callable): Fonction à appeler en cas de modification.
        """
        ConfigReload.reload_on_change(callback)

    @staticmethod
    def get_service_config(service: str) -> Dict[str, Any]:
        """
        Retourne la configuration d'un service/module spécifique.
        Args:
            service (str): Nom du service/module.
        Returns:
            dict: Configuration du service.
        """
        path = os.path.join(CONFIG_DIR, service, 'config.yml')
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            # Exemple d'utilisation de Pydantic pour valider une section 'watchdog'
            if 'watchdog' in config:
                try:
                    validated = ServiceConfigModel(**config['watchdog'])
                    rprint(f"[green]Config Watchdog validée :[/green] {validated}")
                except ValidationError as ve:
                    rprint(f"[red]Erreur validation Pydantic :[/red] {ve}")
            return config
        except Exception as e:
            raise ConfigException(f"Erreur lecture config {service}: {e}")

    @staticmethod
    def set_service_config_arg(service: str, section: str, key: str, value: Any) -> bool:
        """
        Ajoute ou modifie un argument dans une section du fichier config individuel, avec validation et valeurs par défaut.
        Args:
            service (str): Nom du service/module.
            section (str): Section concernée.
            key (str): Clé à modifier.
            value (Any): Valeur à affecter.
        Returns:
            bool: True si succès, False sinon.
        """
        path = os.path.join(CONFIG_DIR, service, 'config.yml')
        config = ConfigManager.get_service_config(service)
        defaults = get_defaults(service)
        schema = get_schema(service)
        if section not in config:
            config[section] = defaults.get(section, {})
        config[section][key] = value
        valid = True
        if section in schema:
            valid = ConfigValidation.validate_config({key: value}, {key: schema[section].get(key, {})})
        if not valid:
            raise ConfigException(f"Validation échouée pour {service}.{section}.{key}: {value}")
        try:
            with open(path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(config, f)
            return True
        except Exception as e:
            raise ConfigException(f"Erreur écriture config {service}: {e}")

    @staticmethod
    def delete_service_config_arg(service: str, section: str, key: str) -> bool:
        """
        Supprime un argument d'une section du fichier config individuel.
        Args:
            service (str): Nom du service/module.
            section (str): Section concernée.
            key (str): Clé à supprimer.
        Returns:
            bool: True si succès, False sinon.
        """
        path = os.path.join(CONFIG_DIR, service, 'config.yml')
        config = ConfigManager.get_service_config(service)
        if section in config and key in config[section]:
            del config[section][key]
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(config, f)
                return True
            except Exception as e:
                raise ConfigException(f"Erreur écriture config {service}: {e}")
        return False

    @staticmethod
    def delete_service_config_section(service: str, section: str) -> bool:
        """
        Supprime une section entière du fichier config individuel.
        Args:
            service (str): Nom du service/module.
            section (str): Section à supprimer.
        Returns:
            bool: True si succès, False sinon.
        """
        path = os.path.join(CONFIG_DIR, service, 'config.yml')
        config = ConfigManager.get_service_config(service)
        if section in config:
            del config[section]
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(config, f)
                return True
            except Exception as e:
                raise ConfigException(f"Erreur écriture config {service}: {e}")
        return False

    @staticmethod
    def _find_config_files() -> list:
        """Retourne la liste des fichiers de configuration individuels."""
        return ConfigMerge.find_config_files()

    @staticmethod
    def _deep_merge_dicts(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        """Fusion profonde de deux dictionnaires."""
        return ConfigMerge.deep_merge_dicts(a, b)

    @staticmethod
    def merge_configs() -> Dict[str, Any]:
        """Fusionne toutes les configurations individuelles."""
        return ConfigMerge.merge_configs()

    @staticmethod
    def update_full_config() -> bool:
        """
        Écrit le fichier de configuration fusionné sur le disque.
        Returns:
            bool: True si succès, False sinon.
        """
        merged = ConfigManager.merge_configs()
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(CONFIG_FULL_PATH, 'w', encoding='utf-8') as f:
                yaml.safe_dump(merged, f)
            return True
        except FileNotFoundError:
            raise ConfigException(f"File not found: {CONFIG_FULL_PATH}")
        except PermissionError:
            raise ConfigException(f"Permission denied: {CONFIG_FULL_PATH}")
        except yaml.YAMLError as e:
            raise ConfigException(f"YAML error while writing {CONFIG_FULL_PATH}: {e}")
        except OSError as e:
            raise ConfigException(f"Error writing {CONFIG_FULL_PATH}: {e}")
        return False

    @staticmethod
    def get_full_config() -> Dict[str, Any]:
        """
        Retourne la configuration fusionnée globale.
        Returns:
            dict: Configuration globale.
        """
        if not os.path.exists(CONFIG_FULL_PATH):
            ConfigManager.update_full_config()
        try:
            with open(CONFIG_FULL_PATH, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            raise ConfigException(f"File not found: {CONFIG_FULL_PATH}")
        except PermissionError:
            raise ConfigException(f"Permission denied: {CONFIG_FULL_PATH}")
        except yaml.YAMLError as e:
            raise ConfigException(f"YAML error in {CONFIG_FULL_PATH}: {e}")

    @staticmethod
    def merge_schemas() -> Dict[str, Any]:
        """
        Fusionne tous les schémas individuels en un schéma global.
        Returns:
            dict: Schéma global Cerberus.
        """
        merged = {}
        for file in _find_schema_files():
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                    merged = ConfigMerge.deep_merge_dicts(merged, data)
            except Exception as e:
                raise ConfigException(f"Error reading schema {file}: {e}")
        return merged

    @staticmethod
    def merge_defaults() -> Dict[str, Any]:
        """
        Fusionne tous les fichiers de valeurs par défaut en un global.
        Returns:
            dict: Defaults global.
        """
        merged = {}
        for file in _find_defaults_files():
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                    merged = ConfigMerge.deep_merge_dicts(merged, data)
            except Exception as e:
                raise ConfigException(f"Error reading defaults {file}: {e}")
        return merged

    @staticmethod
    def update_global_schema_and_defaults() -> bool:
        """
        Génère les fichiers globaux de validation et de valeurs par défaut au format JSON.
        Returns:
            bool: True si succès, False sinon.
        """
        import json
        try:
            # Fusion des schémas
            schema_dict = {}
            for file in _find_schema_files():
                with open(file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                    schema_dict.update(data)
            with open(os.path.join(CONFIG_DIR, 'schemas_globale.json'), 'w', encoding='utf-8') as f:
                json.dump(schema_dict, f, indent=2, ensure_ascii=False)

            # Fusion des valeurs par défaut
            defaults_dict = {}
            for file in _find_defaults_files():
                with open(file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                    defaults_dict.update(data)
            with open(os.path.join(CONFIG_DIR, 'defaults_globale.json'), 'w', encoding='utf-8') as f:
                json.dump(defaults_dict, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            raise ConfigException(f"Erreur écriture fichiers globaux: {e}")

    @staticmethod
    def load_global_schema_as_yaml() -> dict:
        """
        Charge le fichier schemas_globale.json et le convertit en dict (format YAML utilisable).
        """
        import json
        path = os.path.join(CONFIG_DIR, 'schemas_globale.json')
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def load_global_defaults_as_yaml() -> dict:
        """
        Charge le fichier defaults_globale.json et le convertit en dict (format YAML utilisable).
        """
        import json
        path = os.path.join(CONFIG_DIR, 'defaults_globale.json')
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    @staticmethod
    def watch_config_changes():
        """
        Squelette pour la surveillance des changements de configuration.
        """
        pass  # To implement with watchdog or polling
