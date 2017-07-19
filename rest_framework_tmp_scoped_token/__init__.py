
from .auth import TokenAuth
from .token import TokenManager

__version__ = '0.1.0'
__license__ = 'GNU Affero General Public License v3.0'
__description__ = 'Temporary Django REST Framework permission-scoped token'
__author__ = 'Anthony Lukach'
__email__ = 'alukach@cadasta.org'
__url__ = 'https://github.com/Cadasta/drf-tmp-scoped-token'
__all__ = ('TokenAuth', 'TokenManager',)
