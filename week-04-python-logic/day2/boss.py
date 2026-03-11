from collections import Counter


def deduplication(mobile_events, web_events):
    events = set()
    unique_events = []
    for i in mobile_events + web_events:
        if i["event_id"] not in events:
            events.add(i['event_id'])
            unique_events.append(i)
    print(events, unique_events)

    user_counts = Counter([event["user_id"] for event in unique_events])
    most_active = user_counts.most_common(1)[0][0]
    print(most_active)
    s1 = {event['user_id'] for event in mobile_events}
    s2 = {event['user_id'] for event in web_events}
    print(s1.intersection(s2))

mobile_events = [
        {"event_id": "e1", "user_id": "u1", "action": "click"},
        {"event_id": "e2", "user_id": "u2", "action": "scroll"},
        {"event_id": "e1", "user_id": "u1", "action": "click"},  # duplicate!
        {"event_id": "e3", "user_id": "u1", "action": "purchase"},
        {"event_id": "e4", "user_id": "u3", "action": "click"},
    ]

web_events = [
        {"event_id": "e5", "user_id": "u2", "action": "login"},
        {"event_id": "e6", "user_id": "u4", "action": "click"},
        {"event_id": "e5", "user_id": "u2", "action": "login"},  # duplicate!
        {"event_id": "e7", "user_id": "u1", "action": "scroll"},
    ]
deduplication(mobile_events, web_events)