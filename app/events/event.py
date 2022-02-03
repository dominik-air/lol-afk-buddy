"""Observer design pattern based event system. Reference: https://youtu.be/oNalXg67XEE."""

subscribers = dict()


def subscribe(event_type: str, function):
    if event_type not in subscribers:
        subscribers[event_type] = []
    subscribers[event_type].append(function)


def post_event(event_type: str, data):
    if event_type not in subscribers:
        return
    for function in subscribers[event_type]:
        function(data)
