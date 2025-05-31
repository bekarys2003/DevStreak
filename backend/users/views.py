# users/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny

from .github_payload_utils import extract_commit_count  # your helper
import requests
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import GitHubProfile
from .serializers import UserSerializer
from core.github_api import GitHubAPIClient
# from datetime import datetime, timezone, timedelta
from datetime import datetime, timedelta
from django.core.cache import cache
from .models import DailyContribution
from .services import record_today_xp, analyze_commit_message_spacy
import logging
from django.utils import timezone


logger = logging.getLogger(__name__)
CACHE_KEY_COMMITS = 'daily_commits_leaderboard'
CACHE_KEY_STREAK = "streak_leaderboard"


User = get_user_model()


class HelloWorld(APIView):
    def get(self, request):
        return Response({"message": "Hello from DevStreak API!"})


class GitHubLoginAPIView(APIView):
    """
    Exchange GitHub `code` for a JWT pair, create/fetch the Django User,
    and persist the GitHub access token.
    """
    def post(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'detail': 'Missing code'}, status=status.HTTP_400_BAD_REQUEST)

        ## 1) Exchange code for GitHub access token
        token_resp = requests.post(
            'https://github.com/login/oauth/access_token',
            data={
                'client_id': settings.GITHUB_CLIENT_ID,
                'client_secret': settings.GITHUB_CLIENT_SECRET,
                'code': code
            },
            headers={'Accept': 'application/json'}
        )
        token_data = token_resp.json()
        access_token = token_data.get('access_token')
        if not access_token:
            return Response({'detail': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)

        ## 2) Fetch user info JSON
        user_data = requests.get(
            'https://api.github.com/user',
            headers={'Authorization': f'token {access_token}'}
        ).json()

        username = user_data.get('login')
        if not username:
            return Response({'detail': 'Cannot fetch GitHub login'}, status=status.HTTP_400_BAD_REQUEST)

        ## 3) Fetch email (public or primary verified)
        email = user_data.get('email')
        if not email:
            emails = requests.get(
                'https://api.github.com/user/emails',
                headers={'Authorization': f'token {access_token}'}
            ).json()
            primary = next((e for e in emails if e.get('primary') and e.get('verified')), None)
            email = primary.get('email') if primary else None

        if not email:
            return Response({'detail': 'GitHub email not available'}, status=status.HTTP_400_BAD_REQUEST)

        ## 4) Get or create the Django User
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={'email': email}
        )

        ## 5) Save or update the GitHubProfile with the raw token
        GitHubProfile.objects.update_or_create(
            user=user,
            defaults={'access_token': access_token}
        )

        ## 6) Issue JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_contributions(request):
    # pull the GitHub token we stored
    try:
        token = GitHubProfile.objects.get(user=request.user).access_token
    except GitHubProfile.DoesNotExist:
        return Response(
            {'detail': 'GitHub token missing; please log in again.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    client = GitHubAPIClient(token)
    data = client.fetch_user_daily_contributions(request.user.username)
    return Response(data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_streak(request):
    # 1) Get the stored GitHub token
    try:
        token = GitHubProfile.objects.get(user=request.user).access_token
    except GitHubProfile.DoesNotExist:
        return Response(
            {'detail': 'GitHub token missing; please log in again.'},
            status=400
        )

    # 2) Fetch the last 365 days of contributions
    client = GitHubAPIClient(token)
    cal = client.fetch_user_contribution_calendar(request.user.username, days=365)

    # 3) Compute consecutive days ending today with count > 0
    today_str = timezone.localdate().isoformat()
    streak = 0
    # build a lookup by date
    lookup = {d["date"]: d["count"] for d in cal}
    # walk backwards from today
    current_date = timezone.localdate()
    while True:
        date_str = current_date.isoformat()
        if lookup.get(date_str, 0) > 0:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break

    return Response({'streak': streak})







@api_view(["GET"])
@permission_classes([IsAuthenticated])
def leaderboard(request):
    """
    REST-fallback for clients who can’t do WebSockets.
    """
    data = cache.get(CACHE_KEY_COMMITS)
    if data is None:
        # cold cache: compute & prime
        data = compute_daily_xp_leaderboard()
        cache.set(CACHE_KEY_COMMITS, data, timeout=15 * 60)
        # return Response([], status=status.HTTP_204_NO_CONTENT)

    return Response(data)



def compute_daily_xp_leaderboard():
    today =  timezone.localdate()
    qs = DailyContribution.objects.filter(date=today).select_related('user')
    entries = [
        {'username': dc.user.username, 'xp': dc.xp}
        for dc in qs
    ]
    entries.sort(key=lambda e: e['xp'], reverse=True)
    return entries


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def streak_leaderboard(request):
    data = cache.get(CACHE_KEY_STREAK)
    if data is None:
        # pristine cache on cold start
        data = compute_streak_leaderboard()
        cache.set(CACHE_KEY_STREAK, data, timeout=15*60)
    return Response(data)


def compute_streak_leaderboard():
    entries = []
    for profile in GitHubProfile.objects.select_related("user"):
        client = GitHubAPIClient(profile.access_token)
        cal    = client.fetch_user_contribution_calendar(
                     profile.user.username, days=365
                 )
        # map and filter
        lookup   = {d["date"]: d["count"] for d in cal}
        non_zero = [d["date"] for d in cal if d["count"] > 0]

        # start from your last commit date (not a zero-count today)
        if non_zero:
            latest_iso = max(non_zero)
            cur = datetime.fromisoformat(latest_iso).date()
        else:
            cur = timezone.localdate()

        # walk backwards counting days with >0 commits
        streak = 0
        while lookup.get(cur.isoformat(), 0) > 0:
            streak += 1
            cur -= timedelta(days=1)

        entries.append({
            "username": profile.user.username,
            "streak":   streak,
        })

    entries.sort(key=lambda e: e["streak"], reverse=True)
    return entries






# users/views.py

# users/views.py (excerpt)

@api_view(['POST'])
@permission_classes([AllowAny])
def github_push_webhook(request):
    # Identify which GitHub event we received:
    event_type = request.META.get("HTTP_X_GITHUB_EVENT")
    logger.info("🔔 [Webhook] Got event: %s", event_type)

    # All webhook payloads will at least have repository.owner.login
    try:
        gh_username = request.data['repository']['owner']['login']
        profile = GitHubProfile.objects.get(user__username=gh_username)
    except (KeyError, GitHubProfile.DoesNotExist):
        # If we can't find a matching user, just 404
        return Response(status=404)

    # ─── 1) Handle a normal “push” ─────────────────────────────────────────────────
    if event_type == "push":
        commits = request.data.get("commits", [])
        count   = len(commits)
        if count > 0:
            base_xp = count * 2
            logger.info("[XP SYNC] %s: +%d XP, +%d commits",
                        profile.user.username, base_xp, count)
            # Award base XP for each commit:
            record_today_xp(profile.user, xp_delta=base_xp, commit_delta=count)

            # Bonus XP via spaCy (0–3 per commit):
            for c in commits:
                msg = c.get("message", "") or ""
                from .services import analyze_commit_message_spacy
                bonus = analyze_commit_message_spacy(msg)
                if bonus > 0:
                    logger.info("[MSG IMPACT] %s: +%d bonus XP for “%s”",
                                profile.user.username, bonus, msg[:50])
                    record_today_xp(profile.user, xp_delta=bonus)

        return Response(status=204)

    # ─── 2) Handle a Pull Request event ──────────────────────────────────────────────
    if event_type == "pull_request":
        pr_data = request.data.get("pull_request", {})
        action = request.data.get("action", "")

        # 2.1) PR opened → +3 XP
        if action == "opened":
            logger.info("[PR OPENED] %s: +3 XP for opening a PR", profile.user.username)
            record_today_xp(profile.user, xp_delta=3)

        # 2.2) PR merged → +3 XP
        # Note: GitHub sends “action”: "closed" even if someone just closed without merging.
        # To detect an actual merge, we check `pull_request["merged"] == True`
        elif action == "closed" and pr_data.get("merged", False):
            logger.info("[PR MERGED] %s: +3 XP for merging a PR", profile.user.username)
            record_today_xp(profile.user, xp_delta=3)

        return Response(status=204)

    # ─── 3) Ignore any other GitHub event types ────────────────────────────────────
    return Response(status=204)