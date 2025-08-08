# Validation avancée (Cerberus)
# (à déplacer le contenu de l'ancien config_validation.py ici)

from cerberus import Validator
from core.exceptions import ConfigException

class ConfigValidation:
    """
    Module de validation avancée des configurations (Cerberus).
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
        Raises:
            ConfigException: en cas d’erreur de validation.
        """
        try:
            v = Validator(schema)
            return v.validate(config)
        except Exception as e:
            raise ConfigException(f"Erreur validation Cerberus: {e}")
