import os
import yaml
from typing import Dict, Any
from core.exceptions import ConfigException

CONFIG_DIR = os.path.join(os.path.dirname(__file__), '../../config')

class ConfigMerge:
    """
    Module de fusion profonde et extraction des configurations.
    - Recherche tous les fichiers config.yml individuels
    - Fusionne récursivement les dictionnaires
    """
    @staticmethod
    def find_config_files() -> list:
        """
        Retourne la liste des fichiers de configuration individuels.
        Returns:
            list: chemins des fichiers config.yml
        """
        files = []
        for root, dirs, filenames in os.walk(CONFIG_DIR):
            for filename in filenames:
                if filename == 'config.yml' and root != CONFIG_DIR:
                    files.append(os.path.join(root, filename))
        return files

    @staticmethod
    def deep_merge_dicts(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fusion profonde de deux dictionnaires.
        Args:
            a (dict): Dictionnaire source.
            b (dict): Dictionnaire à fusionner.
        Returns:
            dict: Dictionnaire fusionné.
        """
        result = dict(a)
        for k, v in b.items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = ConfigMerge.deep_merge_dicts(result[k], v)
            else:
                result[k] = v
        return result

    @staticmethod
    def merge_configs() -> Dict[str, Any]:
        """
        Fusionne toutes les configurations individuelles.
        Returns:
            dict: Configuration globale fusionnée.
        Raises:
            ConfigException: en cas d’erreur de lecture.
        """
        merged = {}
        for file in ConfigMerge.find_config_files():
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                    merged = ConfigMerge.deep_merge_dicts(merged, data)
            except Exception as e:
                raise ConfigException(f"Error reading {file}: {e}")
        return merged
