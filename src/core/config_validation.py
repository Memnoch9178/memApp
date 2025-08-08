from cerberus import Validator

class ConfigValidation:
    @staticmethod
    def validate_config(config: dict, schema: dict) -> bool:
        v = Validator(schema)
        return v.validate(config)
