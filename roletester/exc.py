from cinderclient.exceptions import NotFound as CinderNotFound
from glanceclient.exc import HTTPNotFound as GlanceNotFound
from glanceclient.exc import Unauthorized as GlanceUnauthorized
from keystoneauth1.exceptions.http import Unauthorized as KeystoneUnauthorized
from keystoneauth1.exceptions.http import Forbidden as KeystoneForbidden
from keystoneauth1.exceptions.http import NotFound as KeystoneNotFound
from neutronclient.common.exceptions import NotFound as NeutronNotFound
from novaclient.exceptions import NotFound as NovaNotFound
from swiftclient.client import ClientException as SwiftClientException

__all__ = [
    'CinderNotFound',
    'GlanceNotFound',
    'GlanceUnauthorized',
    'NeutronNotFound',
    'KeystoneNotFound',
    'KeystoneUnauthorized',
    'KeystoneForbidden'
    'NovaNotFound',
    'SwiftClientException'
]
