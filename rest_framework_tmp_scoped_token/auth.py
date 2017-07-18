from django.utils.six import text_type
from rest_framework import authentication, exceptions, HTTP_HEADER_ENCODING

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
        auth = authentication.get_authorization_header(request)
        if auth:
            try:
                split = self.keyword + ' '
                if isinstance(split, text_type):
                    # Follow DRF in making auth token byestring
                    split = split.encode(HTTP_HEADER_ENCODING)
                _, auth = auth.split()
            except (IndexError, ValueError):
                return
        auth = auth or request.GET.get(self.get_param, '')
        if auth:
            try:
                token = TemporaryApiToken.from_signed_token(auth)
                if token.recipient:
                    request.META['X-API-Token-Recipient'] = token.recipient
                return token.authenticate(request)
            except (AssertionError, ValueError) as e:
                raise exceptions.AuthenticationFailed(e)
            except TemporaryApiToken.SignatureExpired:
                raise exceptions.AuthenticationFailed("Token has expired")
            except TemporaryApiToken.BadSignature:
                raise exceptions.AuthenticationFailed("Bad API token")
