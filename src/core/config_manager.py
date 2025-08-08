import os
import yaml
from typing import Dict, Any

CONFIG_DIR = os.path.join(os.path.dirname(__file__), '../config')
CONFIG_FULL_PATH = os.path.join(CONFIG_DIR, 'config_full.yml')

class ConfigManager:
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
            with open(file, 'r') as f:
                data = yaml.safe_load(f) or {}
                merged = ConfigManager._deep_merge_dicts(merged, data)
        return merged

    @staticmethod
    def update_full_config():
        merged = ConfigManager.merge_configs()
        with open(CONFIG_FULL_PATH, 'w') as f:
            yaml.safe_dump(merged, f)

    @staticmethod
    def get_full_config() -> Dict[str, Any]:
        if not os.path.exists(CONFIG_FULL_PATH):
            ConfigManager.update_full_config()
        with open(CONFIG_FULL_PATH, 'r') as f:
            return yaml.safe_load(f) or {}

    # Squelette de surveillance (à compléter)
    @staticmethod
    def watch_config_changes():
        pass  # À implémenter avec watchdog ou polling
