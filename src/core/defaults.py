# Définitions des valeurs par défaut et héritage pour les configurations

DEFAULTS = {
    'memApp': {
        'watchdog': {
            'enabled': False,
            'interval': 30,
            'log_path': '/var/log/memapp/watchdog.log'
        },
        'database': {
            'host': 'localhost',
            'port': 5432,
            'user': 'memapp',
            'password': ''
        }
    },
    'logger': {
        'level': 'WARNING',
        'file': '/var/log/memapp/app.log',
        'rotation': 'weekly'
    }
}

def get_defaults(service=None):
    if service:
        return DEFAULTS.get(service, {})
    return DEFAULTS
