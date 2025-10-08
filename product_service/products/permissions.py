import jwt
from rest_framework.permissions import BasePermission
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError


class IsJWTAuthenticated(BasePermission):
    def has_permission(self, request, view):
        print('Hitted Yaaaaa')
        auth_header = request.headers.get('Authorization', '')

        if not auth_header.startswith('Bearer '):
            return False

        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(
                token,
                settings.SIMPLE_JWT['SIGNING_KEY'],
                algorithms=[settings.SIMPLE_JWT.get('ALGORITHM', 'HS256')]
            )
            payload['access_token'] = token
            request.token_payload = payload  
            return True

        except ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except InvalidTokenError:
            raise AuthenticationFailed("Invalid token")