import hmac
import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

User = get_user_model()

# "dev" is the only account allowed to see Admin Traffic Logs, so nobody can sign up as it.
RESERVED_USERNAMES = {'dev'}
USERNAME_RE = re.compile(r'^[A-Za-z0-9_.-]{3,30}$')


class AdminSignupThrottle(AnonRateThrottle):
    scope = 'admin_signup'  # rate is set in settings.py (see below)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AdminSignupThrottle])
def admin_signup(request):
    expected_code = getattr(settings, 'ADMIN_SIGNUP_CODE', '')
    if not expected_code:
        return Response({'error': 'Admin sign up is currently disabled.'}, status=403)

    username = str(request.data.get('username', '')).strip()
    password = str(request.data.get('password', ''))
    supplied_code = str(request.data.get('signup_code', ''))

    # Check the code first so wrong-code requests learn nothing about existing usernames.
    if not hmac.compare_digest(supplied_code.encode(), expected_code.encode()):
        return Response({'error': 'Invalid sign up code.'}, status=403)

    if not USERNAME_RE.match(username):
        return Response(
            {'error': 'Username must be 3-30 characters: letters, numbers, dot, dash or underscore.'},
            status=400,
        )
    if username.lower() in RESERVED_USERNAMES:
        return Response({'error': 'That username is reserved.'}, status=400)
    if User.objects.filter(username__iexact=username).exists():
        return Response({'error': 'That username is already taken.'}, status=400)

    try:
        validate_password(password, user=User(username=username))
    except ValidationError as exc:
        return Response({'error': ' '.join(exc.messages)}, status=400)

    try:
        # is_staff lets the account use admin-only API views. It is not a superuser.
        User.objects.create_user(
            username=username, password=password, is_staff=True)
    except IntegrityError:
        return Response({'error': 'That username is already taken.'}, status=400)

    return Response({'message': 'Admin account created.'}, status=201)
