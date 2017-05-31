from rest_framework import authentication
from rest_framework import exceptions

from .token import TemporaryApiToken


class TmpTokenAuth(authentication.BaseAuthentication):
    """
    Authentication scheme to authenticate with a token located in the
    'Authorization' header or as a 'TOKEN' query parameter.
    """
    # http://www.django-rest-framework.org/api-guide/authentication/#custom-authentication

    keyword = 'TmpToken'
    get_param = 'TOKEN'

    def authenticate(self, request):
        signed_token = request.META.get('Authorization')
        if signed_token:
            try:
                _, signed_token = signed_token.split(self.keyword + ' ')
            except (IndexError, ValueError):
                return
        signed_token = signed_token or request.GET.get(self.get_param, '')
        if signed_token:
            try:
                token = TemporaryApiToken.from_signed_token(signed_token)
                if token.recipient:
                    request.META['X-API-Token-Recipient'] = token.recipient
                return token.authenticate(request)
            except (AssertionError, ValueError) as e:
                raise exceptions.AuthenticationFailed(e)
            except TemporaryApiToken.SignatureExpired:
                raise exceptions.AuthenticationFailed("Token has expired")
            except TemporaryApiToken.BadSignature:
                raise exceptions.AuthenticationFailed("Bad API token")
