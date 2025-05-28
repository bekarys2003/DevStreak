from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class HelloWorld(APIView):
    def get(self, request):
        return Response({"message": "Hello from DevStreak API!"})



class GitHubLoginAPIView(APIView):
    """
    Exchange GitHub `code` for a JWT pair.
    """
    def post(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'detail': 'Missing code'}, status=status.HTTP_400_BAD_REQUEST)

        # 1) Exchange code for GitHub access token
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

        # 2) Fetch user info
        user_resp = requests.get(
            'https://api.github.com/user',
            headers={'Authorization': f'token {access_token}'}
        )
        profile = user_resp.json()
        username = profile.get('login')
        if not username:
            return Response({'detail': 'Cannot fetch GitHub user'}, status=status.HTTP_400_BAD_REQUEST)

        # 3) Fetch verified email if not public
        email = profile.get('email')
        if not email:
            emails_resp = requests.get(
                'https://api.github.com/user/emails',
                headers={'Authorization': f'token {access_token}'}
            )
            emails = emails_resp.json()
            primary = next((e for e in emails if e.get('primary') and e.get('verified')), None)
            email = primary.get('email') if primary else None

        if not email:
            return Response({'detail': 'GitHub email not available'}, status=status.HTTP_400_BAD_REQUEST)

        # 4) Get or create Django user
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={'email': email}
        )

        # 5) Issue JWT
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        })
