from django.core import signing
from django.contrib.auth import get_user_model
import six


class TokenManager():
    """
    Class to manage temporary limited-access API tokens. Manages serialization
    and deserialization of API permission payload to/from signed token.

        user: User that will be authenticated by token.
        endpoints: key:value pairs of HTTP methods and endpoint roots that
            token is authorized to access. The following values would authorize
            the token to make GET requests to any endpoints that begin with
            '/api/v1/foo':
                {'GET': ['/api/v1/foo']}
            NOTE: This this token will not override any existing permissions
            for its associatted User within the system. It only adds further
            restrictions to the endpoints that can be accessed.
        max_age: How long, in seconds, the token will be valid. By default,
            tokens will be valid for 1 hour. Non-expiring tokens are not
            supported.
        recipient: (Optional) A textual description of the recipient for which
            this token was intended. No validation is done with this data,
            however it is appended to the request as a 'X-API-Token-Recipient'
            header by the accompanying DRF authentication scheme. This is for
            tracking purposes.

    """
    SignatureExpired = signing.SignatureExpired
    BadSignature = signing.BadSignature

    def __str__(self):
        return (
            '<Token '
            'user={0.user.username} '
            'endpoints={0.endpoints} '
            'max_age={0.max_age} '
            '>'.format(self)
        )

    def __repr__(self):
        return str(self)

    def __init__(self, user, endpoints, max_age=360, recipient=None):
        self.user = user
        self.endpoints = endpoints
        self.max_age = max_age
        self.recipient = recipient
        self._validate()

    def generate_token(self):
        """ Return signed token representing object's configuration """
        unsigned_token = {
            'user': self.user.id,
            'max_age': self.max_age,
            'endpoints': self.endpoints,
        }
        if self.recipient is not None:
            unsigned_token['recipient'] = self.recipient
        return signing.dumps(unsigned_token)  # TODO: Salt

    def authenticate(self, request):
        """
        Given a request object, validate that interaction is permitted by
        token.
        """
        for endpoint in self.endpoints.get(request.method, []):
            if request.path.startswith(endpoint):
                return (self.user, None)
        raise ValueError(
            'Endpoint interaction not permitted by token')

    @classmethod
    def parse_token(cls, signed_token):
        """ Return instance from signed token """
        unsigned_token = cls._parse_token(signed_token)
        unsigned_token['user'] = cls._get_user(unsigned_token['user'])
        cls._parse_token(signed_token, max_age=unsigned_token['max_age'])
        return cls(**unsigned_token)

    def _validate(self):
        """ Ensure token has properly formatted attributes """
        assert getattr(self.user, 'id', None), "user must have id attribute"
        assert isinstance(self.max_age, int), "max_age must be an int"
        assert isinstance(self.endpoints, dict), "endpoints must be a dict"

        valid_methods = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD',
                         'OPTIONS')
        for method, endpoints in self.endpoints.items():
            assert method in valid_methods, \
                "Unsupported method type: {}".format(method)
            assert isinstance(endpoints, (list, tuple)), \
                ("Endpoints must be a list or tuple,"
                 " got {}".format(type(endpoints).__name__))
            for endpoint in endpoints:
                assert isinstance(endpoint, six.string_types), \
                    "Endpoints must be strings"
                assert endpoint.startswith('/'), \
                    "Endpoints must begin with a slash"

    @staticmethod
    def _get_user(user_id):
        User = get_user_model()
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValueError("No such user")

    @staticmethod
    def _parse_token(signed_token, max_age=None):
        return signing.loads(signed_token, max_age=max_age)
