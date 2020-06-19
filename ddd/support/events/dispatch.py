from collections import defaultdict

event_dispatch = defaultdict(list)

def raise_event(event, env=None, safe=False):
    if not getattr(event, '_is_raised', False):
        if env is None:
            env = {}
        event._is_raised = True
        for event_cls, event_callbacks in event_dispatch.items():
            if issubclass(type(event), event_cls):
                for event_callback in event_callbacks:
                    try:
                        event_callback(event, env=env)
                    except Exception as e:
                        if safe:
                            pass
                        else:
                            raise e


def raise_events(events):
    for event in events:
        raise_event(event)
