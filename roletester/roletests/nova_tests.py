from base import Base as BaseTestCase
from roletester.actions.glance import image_create
from roletester.actions.glance import image_delete
from roletester.actions.glance import image_wait_for_status
from roletester.actions.nova import interface_attach
from roletester.actions.nova import interface_detach
from roletester.actions.nova import server_create
from roletester.actions.nova import server_update
from roletester.actions.nova import server_delete
from roletester.actions.nova import server_show
from roletester.actions.nova import server_create_image
from roletester.actions.nova import server_wait_for_status
from roletester.actions.neutron import network_create
from roletester.actions.neutron import port_create
from roletester.actions.neutron import subnet_create
from roletester.exc import KeystoneUnauthorized
from roletester.exc import NeutronNotFound
from roletester.exc import NovaForbidden
from roletester.scenario import ScenarioFactory as Factory
from roletester.utils import randomname

from roletester.log import logging

logger = logging.getLogger("roletester.nova")


class SampleFactory(Factory):

    _ACTIONS = [
        network_create,
        subnet_create,
        server_create,
        port_create,
        server_wait_for_status,
        server_show,
        interface_attach,
        interface_detach,
        server_update,
        server_create_image,
        image_wait_for_status,
        image_delete,
        server_delete
    ]

    NETWORK_CREATE = 0
    SUBNET_CREATE = 1
    PORT_CREATE = 2
    SERVER_CREATE = 3
    SERVER_WAIT = 4
    SERVER_SHOW = 5
    INTERFACE_ATTACH = 6
    INTERFACE_DETACH = 7
    SERVER_UPDATE = 8
    SERVER_CREATE_IMAGE = 9
    SERVER_IMAGE_WAIT = 10
    SERVER_IMAGE_DELETE = 11
    SERVER_DELETE = 12


class SnapFactory(Factory):

    _ACTIONS = [
        network_create,
        subnet_create,
        server_create,
        server_wait_for_status,
        server_show,
        server_update,
        server_create_image,
    ]

    NETWORK_CREATE = 0
    SUBNET_CREATE = 1
    SERVER_CREATE = 2
    SERVER_WAIT = 3
    SERVER_SHOW = 4
    SERVER_UPDATE = 5
    SERVER_CREATE_IMAGE = 6


class NetworkPortFactory(Factory):

    _ACTIONS = [
        network_create,
        subnet_create,
        server_create,
        server_wait_for_status,
        port_create,
    ]

    NETWORK_CREATE = 0
    SUBNET_CREATE = 1
    SERVER_CREATE = 2
    SERVER_WAIT = 3
    PORT_CREATE = 4
    INTERFACE_ATTACH = 5
    INTERFACE_DETACH = 6
    SERVER_DELETE = 7


class NetworkAttachInterfaceFactory(Factory):

    _ACTIONS = [
        network_create,
        subnet_create,
        server_create,
        server_wait_for_status,
        port_create,
        interface_attach,
    ]

    NETWORK_CREATE = 0
    SUBNET_CREATE = 1
    SERVER_CREATE = 2
    SERVER_WAIT = 3
    PORT_CREATE = 4
    INTERFACE_ATTACH = 5


class NetworkDetachInterfaceFactory(Factory):

    _ACTIONS = [
        network_create,
        subnet_create,
        port_create,
        server_create,
        server_wait_for_status,
        interface_attach,
        interface_detach,
        server_delete
    ]

    NETWORK_CREATE = 0
    SUBNET_CREATE = 1
    PORT_CREATE = 2
    SERVER_CREATE = 3
    SERVER_WAIT = 4
    INTERFACE_ATTACH = 5
    INTERFACE_DETACH = 6
    SERVER_DELETE = 7


class TestSample(BaseTestCase):

    name = 'scratch'
    flavor = '1'
    image_file = '/Users/egle/Downloads/cirros-0.3.4-x86_64-disk.img'
    project = randomname()

    def setUp(self):
        super(TestSample, self).setUp()

        kwargs = {
            'name': "glance test image",
            'disk_format': 'qcow2',
            'container_format': 'bare',
            'is_public': 'public'
        }
        try:
            n = self.km.admin_client_manager.get_neutron()
            networks = n.list_networks()['networks']
            public_network = [x['id']
                              for x in networks
                              if x['router:external'] is True][0]
        except IndexError:
            err_str = "No public network found to create floating ips from."
            raise NeutronNotFound(message=err_str)
        self.context["external_network_id"] = public_network

        try:
            image_id = self.context['image_id']
        except Exception:
            logger.info("No image_id found, creating image")

            glance = self.km.admin_client_manager.get_glance()
            images = glance.images.list()
            for img in images:
                if img.name == "glance test image" and img.status == "active" and img.visibility == 'public':
                    logger.info("found image with image id: %s" %img.id)
                    self.context.update(image_id=img.id)
            if 'image_id' in self.context:
                logger.info("image_id in context: %s" %self.context['image_id'])
            else:
                image_create(self.km.admin_client_manager, self.context, self.image_file)
                image_id = self.context['image_id']

    def test_cloud_admin_all_cloud_admin_user(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )

        server_image_kwargs = {'image_key': 'server_image_id'}
        SampleFactory(cloud_admin) \
            .set(SampleFactory.NETWORK_CREATE, clients=creator) \
            .set(SampleFactory.SUBNET_CREATE, clients=creator) \
            .set(SampleFactory.SERVER_IMAGE_DELETE,
                 kwargs=server_image_kwargs) \
            .produce() \
            .run(context=self.context)

    def test_cloud_admin_same_domain_different_user(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        user1 = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )

        server_image_kwargs = {'image_key': 'server_image_id'}
        SampleFactory(cloud_admin) \
            .set(SampleFactory.SERVER_CREATE, clients=user1) \
            .set(SampleFactory.SERVER_WAIT, clients=user1) \
            .set(SampleFactory.SERVER_IMAGE_DELETE,
                 clients=creator,
                 kwargs=server_image_kwargs) \
            .set(SampleFactory.NETWORK_CREATE, clients=creator) \
            .set(SampleFactory.SUBNET_CREATE, clients=creator) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_all_cloud_admin_user(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        bu_admin = self.km.find_user_credentials(
            'Default', self.project, 'bu-admin'
        )

        server_image_kwargs = {'image_key': 'server_image_id'}
        SampleFactory(bu_admin) \
            .set(SampleFactory.NETWORK_CREATE, clients=creator) \
            .set(SampleFactory.SUBNET_CREATE, clients=creator) \
            .set(SampleFactory.SERVER_IMAGE_WAIT,
                 clients=creator,
                 kwargs=server_image_kwargs) \
            .set(SampleFactory.SERVER_IMAGE_DELETE,
                 kwargs=server_image_kwargs) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_same_domain_different_user(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        user1 = self.km.find_user_credentials(
            'Default', self.project, 'bu-admin'
        )
        bu_admin = self.km.find_user_credentials(
            'Default', self.project, 'bu-admin'
        )

        server_image_kwargs = {'image_key': 'server_image_id'}
        SampleFactory(creator) \
            .set(SampleFactory.NETWORK_CREATE, clients=creator) \
            .set(SampleFactory.SUBNET_CREATE, clients=creator) \
            .set(SampleFactory.SERVER_CREATE, clients=user1) \
            .set(SampleFactory.SERVER_WAIT, clients=user1) \
            .set(SampleFactory.SERVER_SHOW, clients=bu_admin) \
            .set(SampleFactory.SERVER_IMAGE_WAIT,
                 kwargs=server_image_kwargs) \
            .set(SampleFactory.SERVER_IMAGE_DELETE,
                 clients=creator,
                 kwargs=server_image_kwargs) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_different_domain_different_user_server_and_snapshot(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        user1 = self.km.find_user_credentials(
            'Default', self.project, '_member_'
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-admin'
        )

        SnapFactory(bu_admin) \
            .set(SnapFactory.NETWORK_CREATE, clients=user1) \
            .set(SampleFactory.SUBNET_CREATE, clients=user1) \
            .set(SnapFactory.SERVER_CREATE, clients=user1) \
            .set(SnapFactory.SERVER_WAIT, clients=user1) \
            .set(SnapFactory.SERVER_SHOW,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .set(SnapFactory.SERVER_UPDATE,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .set(SnapFactory.SERVER_CREATE_IMAGE,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_different_domain_different_user_network(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        user1 = self.km.find_user_credentials(
            'Default', self.project, '_member_'
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-admin'
        )

        NetworkPortFactory(bu_admin) \
            .set(NetworkPortFactory.SERVER_CREATE, clients=user1) \
            .set(NetworkPortFactory.SERVER_WAIT, clients=user1) \
            .set(NetworkPortFactory.NETWORK_CREATE, clients=creator) \
            .set(NetworkPortFactory.SUBNET_CREATE, clients=creator) \
            .set(NetworkPortFactory.PORT_CREATE,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_different_domain_different_user_attach_interface(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        user1 = self.km.find_user_credentials(
            'Default', self.project, 'bu-admin'
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-admin'
        )

        NetworkAttachInterfaceFactory(bu_admin) \
            .set(NetworkAttachInterfaceFactory.NETWORK_CREATE, clients=creator) \
            .set(NetworkAttachInterfaceFactory.SUBNET_CREATE, clients=creator) \
            .set(NetworkAttachInterfaceFactory.PORT_CREATE,
                 clients=creator) \
            .set(NetworkAttachInterfaceFactory.SERVER_CREATE, clients=user1) \
            .set(NetworkAttachInterfaceFactory.SERVER_WAIT, clients=user1) \
            .set(NetworkAttachInterfaceFactory.INTERFACE_ATTACH,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_different_domain_different_user_detach_interface(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        user1 = self.km.find_user_credentials(
            'Default', self.project, 'bu-admin'
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-admin'
        )

        NetworkDetachInterfaceFactory(bu_admin) \
            .set(NetworkDetachInterfaceFactory.NETWORK_CREATE, clients=creator) \
            .set(NetworkDetachInterfaceFactory.SUBNET_CREATE, clients=creator) \
            .set(NetworkDetachInterfaceFactory.PORT_CREATE,
                 clients=creator) \
            .set(NetworkDetachInterfaceFactory.SERVER_CREATE, clients=user1) \
            .set(NetworkDetachInterfaceFactory.SERVER_WAIT, clients=user1) \
            .set(NetworkDetachInterfaceFactory.INTERFACE_ATTACH,
                 clients=creator) \
            .set(NetworkDetachInterfaceFactory.INTERFACE_DETACH,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .set(NetworkDetachInterfaceFactory.SERVER_DELETE,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

        ######
        # bu_user

    def test_bu_user_all_allowed(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        bu_user = self.km.find_user_credentials(
            'Default', self.project, 'bu-user'
        )

        server_image_kwargs = {'image_key': 'server_image_id'}
        SampleFactory(creator) \
            .set(SampleFactory.SERVER_WAIT, clients=bu_user) \
            .set(SampleFactory.SERVER_IMAGE_WAIT,
                 kwargs=server_image_kwargs) \
            .set(SampleFactory.SERVER_SHOW, clients=bu_user) \
            .produce() \
            .run(context=self.context)

#todo: retest
    def test_bu_user_image_delete(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        bu_user = self.km.find_user_credentials(
            'Default', self.project, 'bu-user'
        )

        server_image_kwargs = {'image_key': 'server_image_id'}
        SampleFactory(creator) \
            .set(SampleFactory.SERVER_IMAGE_WAIT,
                 clients=bu_user,
                 kwargs=server_image_kwargs) \
            .set(SampleFactory.SERVER_SHOW, clients=bu_user) \
            .set(SampleFactory.SERVER_IMAGE_WAIT, clients=bu_user) \
            .set(SampleFactory.SERVER_IMAGE_DELETE, clients=bu_user,
                 kwargs=server_image_kwargs, expected_exceptions=[NovaForbidden]) \
            .produce() \
            .run(context=self.context)

    def test_bu_user_different_domain_different_user_server_and_snapshot(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        user1 = self.km.find_user_credentials(
            'Default', self.project, 'bu-user'
        )
        bu_user = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-user'
        )

        SnapFactory(creator) \
            .set(SnapFactory.SERVER_WAIT, clients=user1) \
            .set(SnapFactory.SERVER_SHOW, clients=bu_user,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .set(SnapFactory.SERVER_UPDATE, clients=user1,
                 expected_exceptions=[NovaForbidden]) \
            .set(SnapFactory.SERVER_CREATE_IMAGE, clients=bu_user,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_user_different_domain_different_user_network(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        user1 = self.km.find_user_credentials(
            'Default', self.project, 'bu-user'
        )
        bu_user = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-user'
        )

        NetworkPortFactory(creator) \
            .set(NetworkPortFactory.SERVER_WAIT, clients=user1) \
            .set(NetworkPortFactory.PORT_CREATE, clients=bu_user,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_user_different_domain_different_user_attach_interface(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        bu_user = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-user'
        )

        NetworkAttachInterfaceFactory(creator) \
            .set(NetworkAttachInterfaceFactory.INTERFACE_ATTACH, clients=bu_user,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_user_different_domain_different_user_detach_interface(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        user1 = self.km.find_user_credentials(
            'Default', self.project, 'bu-user'
        )
        bu_user = self.km.find_user_credentials(
            'Default', self.project, 'bu-user'
        )

        NetworkDetachInterfaceFactory(bu_user) \
            .set(NetworkDetachInterfaceFactory.NETWORK_CREATE, clients=creator) \
            .set(NetworkDetachInterfaceFactory.SUBNET_CREATE, clients=creator) \
            .set(NetworkDetachInterfaceFactory.SERVER_CREATE, clients=creator) \
            .set(NetworkDetachInterfaceFactory.SERVER_WAIT, clients=user1) \
            .set(NetworkDetachInterfaceFactory.PORT_CREATE,
                 clients=creator) \
            .set(NetworkDetachInterfaceFactory.INTERFACE_ATTACH,
                 clients=creator) \
            .set(NetworkDetachInterfaceFactory.INTERFACE_DETACH,
                 expected_exceptions=[NovaForbidden]) \
            .set(NetworkDetachInterfaceFactory.SERVER_DELETE,
                 expected_exceptions=[NovaForbidden]) \
            .produce() \
            .run(context=self.context)

