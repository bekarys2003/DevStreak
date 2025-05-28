# users/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

import requests
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import GitHubProfile
from .serializers import UserSerializer
from core.github_api import GitHubAPIClient

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
