from .dispatch import event_dispatch

def on_event(*args):
    def decorator(callback):
        for event_cls in args:
            event_dispatch[event_cls].append(callback)
        return callback
    return decorator
