class ExceptionTemplates:
    TEMPLATES = {}
    @classmethod
    def register(cls, name, func):
        cls.TEMPLATES[name] = func
    @classmethod
    def get(cls, name):
        return cls.TEMPLATES.get(name)
