class EventManager:
    """
    Gestionnaire centralisé des événements pour memApp.
    Permet l’abonnement, la publication et la gestion des handlers.
    """
    def __init__(self):
        self.subscribers = {}
    def subscribe(self, event_type, handler):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
    def publish(self, event_type, data):
        for handler in self.subscribers.get(event_type, []):
            handler(data)
