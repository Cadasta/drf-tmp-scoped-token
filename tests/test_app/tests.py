import unittest

from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIRequestFactory
from rest_framework_tmp_scoped_token import TmpTokenAuth
from rest_framework_tmp_scoped_token import TemporaryApiToken


class TestAuth(unittest.TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user, _ = get_user_model()._default_manager.get_or_create()

    def test_valid_request(self):
        t = TemporaryApiToken(
            user=self.user,
            endpoints=dict(GET=['/bar'], POST=['/foo']),
            max_age=10,
            recipient='my-new-microservice'
        )
        request = self.factory.post(
            '/foo/some-nested-endpoint/',
            Authorization="TmpToken {}".format(t.generate_signed_token())
        )
        self.assertEqual(
            TmpTokenAuth().authenticate(request), (self.user, None)
        )

    def test_api_recipient_header(self):
        t = TemporaryApiToken(
            user=self.user,
            endpoints=dict(GET=['/bar'], POST=['/foo']),
            max_age=10,
            recipient='my-new-microservice'
        )
        request = self.factory.post(
            '/foo/some-nested-endpoint/',
            Authorization="TmpToken {}".format(t.generate_signed_token())
        )
        TmpTokenAuth().authenticate(request)
        self.assertEqual(
            request.META.get('X-API-Token-Recipient'), "my-new-microservice"
        )

    def test_custom_keyword(self):
        class MyCustomAuth(TmpTokenAuth):
            keyword = 'FooBar'

        t = TemporaryApiToken(
            user=self.user,
            endpoints=dict(GET=['/bar'], POST=['/foo']),
            max_age=10,
            recipient='my-new-microservice'
        )
        request = self.factory.post(
            '/foo/some-nested-endpoint/',
            Authorization="FooBar {}".format(t.generate_signed_token())
        )
        self.assertEqual(
            MyCustomAuth().authenticate(request), (self.user, None)
        )

    def test_valid_request_query_arg(self):
        """ Ensure that auth token can be encloded as GET parameter """
        t = TemporaryApiToken(
            user=self.user,
            endpoints=dict(GET=['/foo', '/bar'], POST=['/foo']),
            max_age=10,
            recipient='my-new-microservice'
        )
        request = self.factory.get(
            '/foo/some-nested-endpoint/',
            data={"TOKEN": t.generate_signed_token()}
        )
        self.assertEqual(
            TmpTokenAuth().authenticate(request), (self.user, None)
        )

    def test_custom_get_param(self):
        class MyCustomAuth(TmpTokenAuth):
            get_param = 'FOOBAR'

        t = TemporaryApiToken(
            user=self.user,
            endpoints=dict(GET=['/foo']),
            max_age=10,
            recipient='my-new-microservice'
        )
        request = self.factory.get(
            '/foo/some-nested-endpoint/',
            data={"FOOBAR": t.generate_signed_token()}
        )
        self.assertEqual(
            MyCustomAuth().authenticate(request), (self.user, None)
        )

    def test_invalid_path_request(self):
        """ Ensure that not-permitted paths throws exception """
        t = TemporaryApiToken(
            user=self.user,
            endpoints=dict(GET=['/foo', '/bar'], POST=['/foo']),
            max_age=10,
            recipient='my-new-microservice'
        )
        request = self.factory.get(
            '/secret',
            Authorization="TmpToken " + t.generate_signed_token()
        )
        with self.assertRaises(AuthenticationFailed) as e:
            TmpTokenAuth().authenticate(request)
            self.assertEqual(e, "Endpoint interaction not permitted by token")

    def test_expired_token_request(self):
        """ Ensure that expired tokens throws exception """
        t = TemporaryApiToken(
            user=self.user,
            endpoints=dict(GET=['/foo']),
            max_age=0  # Immediately expired
        )
        request = self.factory.get(
            '/foo/bar',
            Authorization="TmpToken " + t.generate_signed_token()
        )
        with self.assertRaises(AuthenticationFailed) as e:
            TmpTokenAuth().authenticate(request)
            self.assertEqual(e, "Token has expired")

    def test_bad_user_request(self):
        """ Ensure that expired tokens throws exception """
        self.user.id = -1
        t = TemporaryApiToken(
            user=self.user,
            endpoints=dict(GET=['/foo']),
            max_age=0  # Immediately expired
        )
        request = self.factory.get(
            '/foo/bar',
            Authorization="TmpToken " + t.generate_signed_token()
        )
        with self.assertRaises(AuthenticationFailed) as e:
            TmpTokenAuth().authenticate(request)
            self.assertEqual(e, "No such user")

    def test_different_auth_request(self):
        """
        Ensure that tokens without proper beginning string won't be caught
        """
        request = self.factory.get(
            '/foo/bar',
            Authorization="asdf"
        )
        self.assertIsNone(TmpTokenAuth().authenticate(request))

    def test_bad_token_request(self):
        """ Ensure that invalid tokens throws exception """
        request = self.factory.get(
            '/foo/bar',
            Authorization="TmpToken badtoken"
        )
        with self.assertRaises(AuthenticationFailed) as e:
            TmpTokenAuth().authenticate(request)
            self.assertEqual(e, "Bad API token")


if __name__ == '__main__':
    unittest.main()
