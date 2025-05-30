# users/services.py
from datetime import date
from .models import DailyContribution

def record_today_commits(user, count):
    today = date.today()
    dc, _ = DailyContribution.objects.get_or_create(user=user, date=today)
    dc.commit_count = count
    dc.save()   # <— this will fire your post_save → broadcast
