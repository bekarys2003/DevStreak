# users/services.py
from datetime import date
from .models import DailyContribution


def record_today_xp(user, xp_delta, commit_delta=0):
    """
    Increment today’s XP by xp_delta, and optionally track raw commit_count.
    """
    today = date.today()
    dc, _ = DailyContribution.objects.get_or_create(
        user=user, date=today,
        defaults={'commit_count': 0, 'xp': 0}
    )
    dc.xp           += xp_delta
    dc.commit_count += commit_delta
    dc.save()


# users/services.py (after your record_today_xp definition)

def record_today_commits(user, count):
    """
    Legacy stub so signals/tasks that import record_today_commits still work.
    Treat each commit as 2 XP and still bump raw commit_count.
    """
    # Reuse the new XP logic:
    record_today_xp(user, xp_delta=count * 2, commit_delta=count)
