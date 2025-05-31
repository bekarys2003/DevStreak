# users/services.py
from .models import DailyContribution
from django.utils import timezone
import spacy



def record_today_xp(user, xp_delta, commit_delta=0):
    """
    Increment today’s xp by xp_delta, and optionally track raw commit_count.
    """
    today = timezone.localdate()
    dc, created = DailyContribution.objects.get_or_create(
        user=user,
        date=today,
        defaults={'commit_count': 0, 'xp': 0}
    )

    dc.xp += xp_delta
    dc.commit_count += commit_delta
    dc.save()



def record_today_commits(user, count):
    """
    Legacy stub so signals/tasks that import record_today_commits still work.
    Treat each commit as 2 XP and still bump raw commit_count.
    """
    # Reuse the new XP logic:
    record_today_xp(user, xp_delta=count * 2, commit_delta=count)



nlp = spacy.load("en_core_web_sm")

def analyze_commit_message_spacy(message: str) -> int:
    """
    Uses spaCy to count the number of action verbs in the commit message,
    then scales that count to a 0–3 impact score.
    """
    if not message:
        return 0

    doc = nlp(message)
    # count non-auxiliary verbs
    verbs = [tok for tok in doc if tok.pos_ == "VERB" and tok.tag_ != "MD"]
    count = len(verbs)

    # map verb count to 0–3:
    # 0 verbs     → 0
    # 1 verb      → 1
    # 2 verbs     → 2
    # 3 or more   → 3
    return min(3, count)
