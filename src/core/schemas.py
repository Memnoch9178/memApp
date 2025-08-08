# Schémas de validation Cerberus par service/module

SCHEMAS = {
    'memApp': {
        'watchdog': {
            'enabled': {'type': 'boolean', 'required': True},
            'interval': {'type': 'integer', 'min': 1, 'required': True},
            'log_path': {'type': 'string', 'required': True}
        },
        'database': {
            'host': {'type': 'string', 'required': True},
            'port': {'type': 'integer', 'min': 1, 'required': True},
            'user': {'type': 'string', 'required': True},
            'password': {'type': 'string', 'required': False}
        }
    },
    'logger': {
        'level': {'type': 'string', 'allowed': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], 'required': True},
        'file': {'type': 'string', 'required': True},
        'rotation': {'type': 'string', 'allowed': ['daily', 'weekly'], 'required': True}
    }
}

def get_schema(service=None):
    if service:
        return SCHEMAS.get(service, {})
    return SCHEMAS
