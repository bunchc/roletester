from cinderclient.exceptions import NotFound as CinderNotFound
from cinderclient.exceptions import Forbidden as CinderForbidden
from glanceclient.exc import HTTPNotFound as GlanceNotFound
from glanceclient.exc import Unauthorized as GlanceUnauthorized
from glanceclient.exc import HTTPForbidden as GlanceForbidden
from keystoneauth1.exceptions.http import Unauthorized as KeystoneUnauthorized
from keystoneauth1.exceptions.http import Forbidden as KeystoneForbidden
from keystoneauth1.exceptions.http import NotFound as KeystoneNotFound
from neutronclient.common.exceptions import NotFound as NeutronNotFound
from novaclient.exceptions import NotFound as NovaNotFound
from novaclient.exceptions import Forbidden as NovaForbidden
from swiftclient.client import ClientException as SwiftClientException
from neutronclient.common.exceptions import Forbidden as NeutronForbidden
from swift_exceptions import SwiftNotAuthorized as SwiftNotAuthorized
from swift_exceptions import SwiftNotFoundException as SwiftNotFoundException
from swift_exceptions import SwiftForbidden as SwiftForbidden

__all__ = [
    'CinderNotFound',
    'CinderForbidden',
    'GlanceNotFound',
    'GlanceUnauthorized',
    'GlanceForbidden',
    'NeutronForbidden',
    'NeutronNotFound',
    'KeystoneNotFound',
    'KeystoneUnauthorized',
    'KeystoneForbidden'
    'NovaNotFound',
    'SwiftClientException',
    'SwiftNotAuthorized',
    'SwiftNotFoundException',
    'SwiftForbidden'
]
