def extract_commit_count(payload):
    """
    Given a GitHub contributions API response payload (a list of daily dicts with 'date' and 'count'),
    return the total commit count or the count for a specific day as needed.
    For example, summing all counts:
    """
    commits = payload.get('commits')
    if isinstance(commits, list):
        return len(commits)

    # 2) Calendar API case: payload itself is a list of {date,count}
    if isinstance(payload, list):
        return sum(day.get('count', 0) for day in payload)

    # 3) Local-contributions dict case: {'commits': <int>}
    return payload.get('commits', 0)
