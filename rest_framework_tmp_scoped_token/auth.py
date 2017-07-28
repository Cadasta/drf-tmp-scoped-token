from django.utils.translation import ugettext_lazy as _
from rest_framework import authentication, exceptions

from .token import TokenManager


class TokenAuth(authentication.TokenAuthentication):
    """
    Authentication scheme to authenticate with a token located in the
    'Authorization' header or as a 'TOKEN' query parameter.
    """
    # http://www.django-rest-framework.org/api-guide/authentication/#custom-authentication

    keyword = 'TmpToken'
    get_param = 'TOKEN'

    def authenticate(self, request):
        self.request = request

        # Authenticate via header
        output = super(TokenAuth, self).authenticate(request)
        if output:
            return output

        # Authenticate via GET parameter
        token = request.GET.get(self.get_param)
        if token:
            return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        try:
            token = TokenManager.parse_token(key)
            if token.recipient:
                self.request.META['X-API-Token-Recipient'] = token.recipient
            return token.validate_request(self.request)
        except (AssertionError, ValueError) as e:
            raise exceptions.AuthenticationFailed(e)
        except TokenManager.SignatureExpired:
            raise exceptions.AuthenticationFailed(_("Token has expired"))
        except TokenManager.BadSignature:
            raise exceptions.AuthenticationFailed(_("Bad API token"))
