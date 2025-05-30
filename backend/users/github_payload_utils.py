def extract_commit_count(payload):
    """
    Given a GitHub contributions API response payload (a list of daily dicts with 'date' and 'count'),
    return the total commit count or the count for a specific day as needed.
    For example, summing all counts:
    """
    if isinstance(payload, list):
        return sum(day.get('count', 0) for day in payload)
    # If payload is a dict with 'commits' key:
    return payload.get('commits', 0)
