import unittest

from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIRequestFactory
from rest_framework_tmp_scoped_token import TokenAuth
from rest_framework_tmp_scoped_token import TokenManager


class TestAuth(unittest.TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user, _ = get_user_model()._default_manager.get_or_create()

    def test_str(self):
        self.assertTrue(str(TokenManager(
            user=self.user,
            endpoints=dict(GET=['/bar'], POST=['/foo']),
            max_age=10,
            recipient='my-new-microservice'
        )))

    def test_repr(self):
        self.assertTrue(repr(TokenManager(
            user=self.user,
            endpoints=dict(GET=['/bar'], POST=['/foo']),
            max_age=10,
            recipient='my-new-microservice'
        )))

    def test_valid_request(self):
        t = TokenManager(
            user=self.user,
            endpoints=dict(GET=['/bar'], POST=['/foo']),
            max_age=10,
            recipient='my-new-microservice'
        )
        request = self.factory.post(
            '/foo/some-nested-endpoint/',
            HTTP_AUTHORIZATION="TmpToken {}".format(t.generate_token())
        )
        self.assertEqual(
            TokenAuth().authenticate(request), (self.user, None)
        )

    def test_api_recipient_header(self):
        t = TokenManager(
            user=self.user,
            endpoints=dict(GET=['/bar'], POST=['/foo']),
            max_age=10,
            recipient='my-new-microservice'
        )
        request = self.factory.post(
            '/foo/some-nested-endpoint/',
            HTTP_AUTHORIZATION="TmpToken {}".format(t.generate_token())
        )
        TokenAuth().authenticate(request)
        self.assertEqual(
            request.META.get('X-API-Token-Recipient'), "my-new-microservice"
        )

    def test_custom_keyword(self):
        class MyCustomAuth(TokenAuth):
            keyword = 'FooBar'

        t = TokenManager(
            user=self.user,
            endpoints=dict(GET=['/bar'], POST=['/foo']),
            max_age=10,
            recipient='my-new-microservice'
        )
        request = self.factory.post(
            '/foo/some-nested-endpoint/',
            HTTP_AUTHORIZATION="FooBar {}".format(t.generate_token())
        )
        self.assertEqual(
            MyCustomAuth().authenticate(request), (self.user, None)
        )

    def test_valid_request_query_arg(self):
        """ Ensure that auth token can be encloded as GET parameter """
        t = TokenManager(
            user=self.user,
            endpoints=dict(GET=['/foo', '/bar'], POST=['/foo']),
            max_age=10,
            recipient='my-new-microservice'
        )
        request = self.factory.get(
            '/foo/some-nested-endpoint/',
            data={"TOKEN": t.generate_token()}
        )
        self.assertEqual(
            TokenAuth().authenticate(request), (self.user, None)
        )

    def test_custom_get_param(self):
        class MyCustomAuth(TokenAuth):
            get_param = 'FOOBAR'

        t = TokenManager(
            user=self.user,
            endpoints=dict(GET=['/foo']),
            max_age=10,
            recipient='my-new-microservice'
        )
        request = self.factory.get(
            '/foo/some-nested-endpoint/',
            data={"FOOBAR": t.generate_token()}
        )
        self.assertEqual(
            MyCustomAuth().authenticate(request), (self.user, None)
        )

    def test_invalid_path_request(self):
        """ Ensure that not-permitted paths throws exception """
        t = TokenManager(
            user=self.user,
            endpoints=dict(GET=['/foo', '/bar'], POST=['/foo']),
            max_age=10,
            recipient='my-new-microservice'
        )
        request = self.factory.get(
            '/secret',
            HTTP_AUTHORIZATION="TmpToken " + t.generate_token()
        )
        with self.assertRaises(AuthenticationFailed) as e:
            TokenAuth().authenticate(request)
            self.assertEqual(e, "Endpoint interaction not permitted by token")

    def test_expired_token_request(self):
        """ Ensure that expired tokens throws exception """
        t = TokenManager(
            user=self.user,
            endpoints=dict(GET=['/foo']),
            max_age=0  # Immediately expired
        )
        request = self.factory.get(
            '/foo/bar',
            HTTP_AUTHORIZATION="TmpToken " + t.generate_token()
        )
        with self.assertRaises(AuthenticationFailed) as e:
            TokenAuth().authenticate(request)
            self.assertEqual(e, "Token has expired")

    def test_bad_user_request(self):
        """ Ensure that expired tokens throws exception """
        self.user.id = -1
        t = TokenManager(
            user=self.user,
            endpoints=dict(GET=['/foo']),
            max_age=0  # Immediately expired
        )
        request = self.factory.get(
            '/foo/bar',
            HTTP_AUTHORIZATION="TmpToken " + t.generate_token()
        )
        with self.assertRaises(AuthenticationFailed) as e:
            TokenAuth().authenticate(request)
            self.assertEqual(e, "No such user")

    def test_different_auth_request(self):
        """
        Ensure that tokens without proper beginning string won't be caught
        """
        request = self.factory.get(
            '/foo/bar',
            HTTP_AUTHORIZATION="asdf"
        )
        self.assertIsNone(TokenAuth().authenticate(request))

    def test_bad_token_request(self):
        """ Ensure that invalid tokens throws exception """
        request = self.factory.get(
            '/foo/bar',
            HTTP_AUTHORIZATION="TmpToken badtoken"
        )
        with self.assertRaises(AuthenticationFailed) as e:
            TokenAuth().authenticate(request)
            self.assertEqual(e, "Bad API token")


if __name__ == '__main__':
    unittest.main()
