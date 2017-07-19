# DRF Temporary Scoped Token

[![Build Status](https://travis-ci.org/Cadasta/drf-tmp-scoped-token.svg?branch=master)](https://travis-ci.org/Cadasta/drf-tmp-scoped-token)
[![Requirements Status](https://requires.io/github/Cadasta/drf-tmp-scoped-token/requirements.svg?branch=master)](https://requires.io/github/Cadasta/drf-tmp-scoped-token/requirements/?branch=master)

`rest_framework_tmp_scoped_token` provides a Django REST Framework-compatible
system to generate and validate signed authorization tokens. Generated tokens
contain the ID of a user on whose behalf the token bearer authenticates, a
white-list of HTTP verbs and API endpoints that the bearer is permitted to
access, an max-lifespan of the token, and a note about the intended recipient.

## Usage

### Authorization

Add `rest_framework_tmp_scoped_token.TokenAuth` to the
`DEFAULT_AUTHENTICATION_CLASSES` section of your `REST_FRAMEWORK` settings in
`settings.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # ... Your other forms of auth
        'rest_framework_tmp_scoped_token.TokenAuth',
    )
}
```

To authenticate with an temporary permissions token, make a request with the
token included in either:

- the `Authorization` HTTP header with a `TmpToken` keyword:
    ```HTTP
    Authorization: TmpToken eyJzb21ldGhpbmctc2VjcmV0IjoiaG9wZSBub2JvZHkgc2VlcyB0aGlzIn0:1d47N6:woJG0EgLNDb0OjYQmCbsjniP-2Y
    ```
- a `TOKEN` `GET` query parameter:
    ```HTTP
    /api/?TOKEN=eyJzb21ldGhpbmctc2VjcmV0IjoiaG9wZSBub2JvZHkgc2VlcyB0aGlzIn0:1d47N6:woJG0EgLNDb0OjYQmCbsjniP-2Y
    ```

If you would like to customize either the `Authorization` header keyword or the
`GET` query parameter used, you can subclass the
`rest_framework_tmp_scoped_token.TokenAuth` class and override the `keyword` or
`get_param` values.

### Token

To generate a token, use the `rest_framework_tmp_scoped_token.TokenManager`
class. The token encompasses the following information:

- **user**: User that will be authenticated by token.
- **endpoints**: key:value pairs of HTTP methods and endpoint roots that
    token is authorized to access. The following values would authorize
    the token to make GET requests to any endpoints that begin with
    '`api/v1/foo`:

    ```python
    {'GET': ['/api/v1/foo']}
    ```

    **NOTE**: This this token will not override any existing permissions
    for its associatted User within the system. It only adds further
    restrictions to the endpoints that can be accessed.
- **max_age**: How long, in seconds, the token will be valid. By default,
    tokens will be valid for 1 hour. Non-expiring tokens are not
    supported.
- **recipient**: _(Optional)_ A textual description of the recipient for which
    this token was intended. No validation is done with this data,
    however it is appended to the request as a `X-API-Token-Recipient`
    header by the accompanying DRF authentication scheme. This is for
    tracking purposes

**NOTE**: The tokens are signed via Django's
[`signing`](https://docs.djangoproject.com/en/dev/topics/signing/) facility.
It is important to know that the **tokens are not encrypted**, they are simply
signed. For this reason, you should not include any sensitive/secret
information in the tokens. For an example, notice how easy it is to view the
contents of a signed string:

```python
In [1]: from django.core import signing

In [2]: t = signing.dumps({'something-secret': 'hope nobody sees this'})

In [3]: print(t)
eyJzb21ldGhpbmctc2VjcmV0IjoiaG9wZSBub2JvZHkgc2VlcyB0aGlzIn0:1d47N6:woJG0EgLNDb0OjYQmCbsjniP-2Y

In [4]: import base64

In [5]: def b64_decode(s):
   ...:     pad = b'=' * (-len(s) % 4)
   ...:     return base64.urlsafe_b64decode(s + pad)
   ...:

In [6]: print(b64_decode(t.encode('utf8')))
b'{"something-secret":"hope nobody sees this"}5w\x8e\xcd\xeb\n\t\x1bA ,\xd0\xdb\xd0\xe8\xd8B`\x9b\xb29\xe2?\xed\x98'
```

