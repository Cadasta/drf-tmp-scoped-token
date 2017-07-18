
from .auth import TmpTokenAuth
from .token import TemporaryApiToken

__version__ = '0.0.2'
__license__ = 'GNU Affero General Public License v3.0'
__description__ = 'Temporary Django REST Framework permission-scoped token'
__author__ = 'Anthony Lukach'
__email__ = 'alukach@cadasta.org'
__url__ = 'https://github.com/Cadasta/drf-tmp-scoped-token'
__all__ = ('TmpTokenAuth', 'TemporaryApiToken',)
