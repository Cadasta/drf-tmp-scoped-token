DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

SECRET_KEY = 'fn)t*+$)ugeyip6-#txyy$5wf2ervc0d2n#h)qb)y5@ly$t*@w'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',

    'rest_framework',
    'test_app'
)

try:
    from local_settings import *
except ImportError:
    pass
