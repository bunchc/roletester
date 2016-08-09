from base import Base as BaseTestCase
from roletester.actions.glance import image_create
from roletester.actions.glance import image_wait_for_status
from roletester.actions.nova import server_create
from roletester.actions.nova import server_delete
from roletester.actions.nova import server_wait_for_status
from roletester.actions.neutron import network_create
from roletester.actions.neutron import network_show
from roletester.actions.neutron import network_delete
from roletester.actions.neutron import subnet_create
from roletester.actions.neutron import subnet_show
from roletester.actions.neutron import subnet_delete
from roletester.actions.neutron import router_create
from roletester.actions.neutron import router_show
from roletester.actions.neutron import router_add_interface
from roletester.actions.neutron import router_remove_interface
from roletester.actions.neutron import router_delete
from roletester.actions.neutron import security_group_create
from roletester.actions.neutron import security_group_show
from roletester.actions.neutron import security_group_add_to_server
from roletester.actions.neutron import security_group_remove_from_server
from roletester.actions.neutron import security_group_rule_create
from roletester.actions.neutron import security_group_delete
from roletester.actions.neutron import security_group_rule_delete
from roletester.actions.neutron import floatingip_associate
from roletester.actions.neutron import floatingip_create
from roletester.actions.neutron import floatingip_delete
from roletester.actions.neutron import floatingip_disassociate
from roletester.actions.neutron import floatingip_show
from roletester.actions.neutron import port_create
from roletester.exc import KeystoneUnauthorized
from neutronclient.common.exceptions import NetworkNotFoundClient
from roletester.scenario import ScenarioFactory as Factory
from roletester.utils import randomname

from roletester.log import logging

logger = logging.getLogger("roletester.neutron")


class SampleFactory(Factory):

    _ACTIONS = [
        image_create,
        image_wait_for_status,
        network_create,
        network_show,
        subnet_create,
        subnet_show,
        server_create,
        server_wait_for_status,
        security_group_create,
        security_group_show,
        security_group_rule_create,
        security_group_add_to_server,
        security_group_remove_from_server,
        security_group_rule_delete,
        security_group_delete,
        server_delete,
        router_create,
        router_show,
        router_add_interface,
        router_remove_interface,
        router_delete,
        subnet_delete,
        network_delete
    ]

    IMAGE_CREATE = 0
    IMAGE_WAIT = 1
    NETWORK_CREATE = 2
    NETWORK_SHOW = 3
    SUBNET_CREATE = 4
    SUBNET_SHOW = 5
    SERVER_CREATE = 6
    SERVER_WAIT = 7
    SECURITY_GROUP_CREATE = 8
    SECURITY_GROUP_SHOW = 9
    SECURITY_GROUP_RULE_CREATE = 10
    SECURITY_GROUP_ADD_TO_SERVER = 11
    SECURITY_GROUP_REMOVE_FROM_SERVER = 12
    SECURITY_GROUP_RULE_DELETE = 13
    SECURITY_GROUP_DELETE = 14
    SERVER_DELETE = 15
    ROUTER_CREATE = 16
    ROUTER_SHOW = 17
    ROUTER_ADD_INTERFACE = 18
    ROUTER_REMOVE_INTERFACE = 19
    ROUTER_DELETE = 20
    SUBNET_DELETE = 21
    NETWORK_DELETE = 22


class SecgroupAddFactory(Factory):

    _ACTIONS = [
        image_create,
        image_wait_for_status,
        network_create,
        network_show,
        subnet_create,
        subnet_show,
        server_create,
        server_wait_for_status,
        security_group_create,
        security_group_show,
        security_group_rule_create,
        security_group_add_to_server,
    ]

    IMAGE_CREATE = 0
    IMAGE_WAIT = 1
    NETWORK_CREATE = 2
    NETWORK_SHOW = 3
    SUBNET_CREATE = 4
    SUBNET_SHOW = 5
    SERVER_CREATE = 6
    SERVER_WAIT = 7
    SECURITY_GROUP_CREATE = 8
    SECURITY_GROUP_SHOW = 9
    SECURITY_GROUP_RULE_CREATE = 10
    SECURITY_GROUP_ADD_TO_SERVER = 11


class AddInterfaceFactory(Factory):

    _ACTIONS = [
        image_create,
        image_wait_for_status,
        network_create,
        subnet_create,
        server_create,
        server_wait_for_status,
        security_group_create,
        security_group_rule_create,
        security_group_add_to_server,
        security_group_remove_from_server,
        security_group_rule_delete,
        security_group_delete,
        server_delete,
        router_create,
        router_show,
        router_add_interface,

    ]

    IMAGE_CREATE = 0
    IMAGE_WAIT = 1
    NETWORK_CREATE = 2
    SUBNET_CREATE = 3
    SERVER_CREATE = 4
    SERVER_WAIT = 5
    SECURITY_GROUP_CREATE = 6
    SECURITY_GROUP_RULE_CREATE = 7
    SECURITY_GROUP_ADD_TO_SERVER = 8
    SECURITY_GROUP_REMOVE_FROM_SERVER = 9
    SECURITY_GROUP_RULE_DELETE = 10
    SECURITY_GROUP_DELETE = 11
    SERVER_DELETE = 12
    ROUTER_CREATE = 13
    ROUTER_SHOW = 14
    ROUTER_ADD_INTERFACE = 15


class RouterDeleteFactory(Factory):

    _ACTIONS = [
        router_create,
        router_delete
    ]

    ROUTER_CREATE = 0
    ROUTER_DELETE = 1


class SubnetDeleteFactory(Factory):

    _ACTIONS = [
        network_create,
        subnet_create,
        subnet_delete
    ]

    NETWORK_CREATE = 0
    SUBNET_CREATE = 1
    SUBNET_DELETE = 2


class NetworkDeleteFactory(Factory):

    _ACTIONS = [
        network_create,
        network_delete
    ]

    NETWORK_CREATE = 0
    NETWORK_DELETE = 1


class FloatingIPFactory(Factory):

    _ACTIONS = [
        network_create,
        subnet_create,
        port_create,
        router_create,
        router_add_interface,
        floatingip_create,
        floatingip_show,
        floatingip_associate,
        floatingip_disassociate,
        floatingip_delete,
    ]

    NETWORK_CREATE = 0
    SUBNET_CREATE = 1
    PORT_CREATE = 2
    ROUTER_CREATE = 3
    ROUTER_ADD_INTERFACE = 4
    FLOATINGIP_CREATE = 5
    FLOATINGIP_SHOW = 6
    FLOATINGIP_ASSOCIATE = 7
    FLOATINGIP_DISASSOCIATE = 8
    FLOATINGIP_DELETE = 9


class TestSample(BaseTestCase):

    name = 'scratch'
    flavor = '1'
    image_file = '/home/chalupaul/cirros-0.3.4-x86_64-disk.img'
    project = randomname()

    def setUp(self):
        super(TestSample, self).setUp()
        try:
            n = self.km.admin_client_manager.get_neutron()
            networks = n.list_networks()['networks']
            public_network = [x['id']
                              for x in networks
                              if x['router:external'] is True][0]
        except IndexError:
            err_str = "No public network found to create floating ips from."
            raise NetworkNotFoundClient(message=err_str)
        self.context["external_network_id"] = public_network

    def test_cloud_admin_all(self):
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )

        SampleFactory(cloud_admin) \
            .set(SampleFactory.IMAGE_CREATE,
                 args=(self.image_file,)) \
            .produce() \
            .run(context=self.context)

    def test_cloud_admin_floatingip(self):
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        FloatingIPFactory(cloud_admin) \
            .produce() \
            .run(context=self.context)

    def test_cloud_admin_same_domain_different_user(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'admin'
        )
        user1 = self.km.find_user_credentials(
            'Default', self.project, '_member_'
        )
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )

        SampleFactory(cloud_admin) \
            .set(SampleFactory.IMAGE_CREATE,
                 clients=creator,
                 args=(self.image_file,)) \
            .set(SampleFactory.IMAGE_WAIT,
                 clients=creator) \
            .set(SampleFactory.NETWORK_CREATE,
                 clients=user1) \
            .set(SampleFactory.SUBNET_CREATE,
                 clients=user1) \
            .set(SampleFactory.SERVER_CREATE,
                 clients=user1) \
            .set(SampleFactory.SERVER_WAIT,
                 clients=user1) \
            .set(SampleFactory.SECURITY_GROUP_CREATE,
                 clients=user1) \
            .set(SampleFactory.SECURITY_GROUP_RULE_CREATE,
                 clients=user1) \
            .set(SampleFactory.SERVER_DELETE,
                 clients=user1) \
            .set(SampleFactory.ROUTER_CREATE,
                 clients=user1) \
            .set(SampleFactory.ROUTER_ADD_INTERFACE,
                 clients=user1) \
            .produce() \
            .run(context=self.context)

    def test_cloud_admin_same_domain_different_user_floatingip(self):
        user1 = self.km.find_user_credentials(
            'Default', self.project, '_member_'
        )
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )

        FloatingIPFactory(cloud_admin) \
            .set(FloatingIPFactory.NETWORK_CREATE,
                 clients=user1) \
            .set(FloatingIPFactory.SUBNET_CREATE,
                 clients=user1) \
            .set(FloatingIPFactory.PORT_CREATE,
                 clients=user1) \
            .set(FloatingIPFactory.ROUTER_CREATE,
                 clients=user1) \
            .set(FloatingIPFactory.ROUTER_ADD_INTERFACE,
                 clients=user1) \
            .set(FloatingIPFactory.FLOATINGIP_CREATE,
                 clients=user1) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_all(self):
        bu_admin = self.km.find_user_credentials(
            'Default', self.project, 'bu-admin'
        )

        SampleFactory(bu_admin) \
            .set(SampleFactory.IMAGE_CREATE,
                 args=(self.image_file,)) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_floatingip(self):
        bu_admin = self.km.find_user_credentials(
            'Default', self.project, 'bu-admin'
        )
        FloatingIPFactory(bu_admin) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_same_domain_different_user(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'admin'
        )
        user1 = self.km.find_user_credentials(
            'Default', self.project, '_member_'
        )
        bu_admin = self.km.find_user_credentials(
            'Default', self.project, 'bu-admin'
        )

        SampleFactory(bu_admin) \
            .set(SampleFactory.IMAGE_CREATE,
                 clients=creator,
                 args=(self.image_file,)) \
            .set(SampleFactory.IMAGE_WAIT,
                 clients=creator) \
            .set(SampleFactory.NETWORK_CREATE,
                 clients=user1) \
            .set(SampleFactory.SUBNET_CREATE,
                 clients=user1) \
            .set(SampleFactory.SERVER_CREATE,
                 clients=user1) \
            .set(SampleFactory.SERVER_WAIT,
                 clients=user1) \
            .set(SampleFactory.SECURITY_GROUP_CREATE,
                 clients=user1) \
            .set(SampleFactory.SECURITY_GROUP_RULE_CREATE,
                 clients=user1) \
            .set(SampleFactory.SERVER_DELETE,
                 clients=user1) \
            .set(SampleFactory.ROUTER_CREATE,
                 clients=user1) \
            .set(SampleFactory.ROUTER_ADD_INTERFACE,
                 clients=user1) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_same_domain_different_user_floatingip(self):
        user1 = self.km.find_user_credentials(
            'Default', self.project, '_member_'
        )
        bu_admin = self.km.find_user_credentials(
            'Default', self.project, 'bu-admin'
        )

        FloatingIPFactory(bu_admin) \
            .set(FloatingIPFactory.NETWORK_CREATE,
                 clients=user1) \
            .set(FloatingIPFactory.SUBNET_CREATE,
                 clients=user1) \
            .set(FloatingIPFactory.PORT_CREATE,
                 clients=user1) \
            .set(FloatingIPFactory.ROUTER_CREATE,
                 clients=user1) \
            .set(FloatingIPFactory.ROUTER_ADD_INTERFACE,
                 clients=user1) \
            .set(FloatingIPFactory.FLOATINGIP_CREATE,
                 clients=user1) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_different_domain_different_user_floatingip(self):
        user1 = self.km.find_user_credentials(
            'Default', self.project, '_member_'
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-admin'
        )

        FloatingIPFactory(bu_admin) \
            .set(FloatingIPFactory.NETWORK_CREATE,
                 clients=user1) \
            .set(FloatingIPFactory.SUBNET_CREATE,
                 clients=user1) \
            .set(FloatingIPFactory.PORT_CREATE,
                 clients=user1) \
            .set(FloatingIPFactory.ROUTER_CREATE,
                 clients=user1) \
            .set(FloatingIPFactory.ROUTER_ADD_INTERFACE,
                 clients=user1) \
            .set(FloatingIPFactory.FLOATINGIP_CREATE,
                 clients=user1) \
            .set(FloatingIPFactory.FLOATINGIP_SHOW,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .set(FloatingIPFactory.FLOATINGIP_ASSOCIATE,
                 clients=user1) \
            .set(FloatingIPFactory.FLOATINGIP_DISASSOCIATE,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .set(FloatingIPFactory.FLOATINGIP_DELETE,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_different_domain_different_user_secgroup_add_to_server(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'admin'
        )
        user1 = self.km.find_user_credentials(
            'Default', self.project, '_member_'
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-admin'
        )

        SecgroupAddFactory(bu_admin) \
            .set(SecgroupAddFactory.IMAGE_CREATE,
                 clients=creator,
                 args=(self.image_file,)) \
            .set(SecgroupAddFactory.IMAGE_WAIT,
                 clients=creator) \
            .set(SecgroupAddFactory.NETWORK_CREATE,
                 clients=user1) \
            .set(SecgroupAddFactory.NETWORK_SHOW,
                 expected_exceptions = [KeystoneUnauthorized]) \
            .set(SecgroupAddFactory.SUBNET_CREATE,
                 clients=user1) \
            .set(SecgroupAddFactory.SUBNET_SHOW,
                 expected_exceptions = [KeystoneUnauthorized]) \
            .set(SecgroupAddFactory.SERVER_CREATE,
                 clients=user1) \
            .set(SecgroupAddFactory.SERVER_WAIT,
                 clients=user1) \
            .set(SecgroupAddFactory.SECURITY_GROUP_CREATE,
                 clients=user1) \
            .set(SecgroupAddFactory.SECURITY_GROUP_SHOW,
                 expected_exceptions = [KeystoneUnauthorized]) \
            .set(SecgroupAddFactory.SECURITY_GROUP_RULE_CREATE,
                 clients=user1) \
            .set(SecgroupAddFactory.SECURITY_GROUP_ADD_TO_SERVER,
                 expected_exceptions = [KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_different_domain_different_user_add_interface_to_server(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'admin'
        )
        user1 = self.km.find_user_credentials(
            'Default', self.project, '_member_'
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-admin'
        )

        AddInterfaceFactory(bu_admin) \
            .set(AddInterfaceFactory.IMAGE_CREATE,
                 clients=creator,
                 args=(self.image_file,)) \
            .set(AddInterfaceFactory.IMAGE_WAIT,
                 clients=creator) \
            .set(AddInterfaceFactory.NETWORK_CREATE,
                 clients=user1) \
            .set(AddInterfaceFactory.SUBNET_CREATE,
                 clients=user1) \
            .set(AddInterfaceFactory.SERVER_CREATE,
                 clients=user1) \
            .set(AddInterfaceFactory.SERVER_WAIT,
                 clients=user1) \
            .set(AddInterfaceFactory.SECURITY_GROUP_CREATE,
                 clients=user1) \
            .set(AddInterfaceFactory.SECURITY_GROUP_RULE_CREATE,
                 clients=user1) \
            .set(AddInterfaceFactory.SECURITY_GROUP_ADD_TO_SERVER,
                 clients=user1) \
            .set(AddInterfaceFactory.SECURITY_GROUP_REMOVE_FROM_SERVER,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .set(AddInterfaceFactory.SECURITY_GROUP_RULE_DELETE,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .set(AddInterfaceFactory.SECURITY_GROUP_DELETE,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .set(AddInterfaceFactory.SERVER_DELETE,
                 clients=user1) \
            .set(AddInterfaceFactory.ROUTER_CREATE,
                 clients=user1) \
            .set(AddInterfaceFactory.ROUTER_SHOW,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .set(AddInterfaceFactory.ROUTER_ADD_INTERFACE,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_different_domain_different_user_router_delete(self):
        user1 = self.km.find_user_credentials(
            'Default', self.project, '_member_'
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-admin'
        )

        RouterDeleteFactory(bu_admin) \
            .set(RouterDeleteFactory.ROUTER_CREATE,
                 clients=user1) \
            .set(RouterDeleteFactory.ROUTER_DELETE,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_different_domain_different_user_subnet_delete(self):
        user1 = self.km.find_user_credentials(
            'Default', self.project, '_member_'
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-admin'
        )

        SubnetDeleteFactory(bu_admin) \
            .set(SubnetDeleteFactory.NETWORK_CREATE,
                 clients=user1) \
            .set(SubnetDeleteFactory.SUBNET_CREATE,
                 clients=user1) \
            .set(SubnetDeleteFactory.SUBNET_DELETE,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_different_domain_different_user_network_delete(self):
        user1 = self.km.find_user_credentials(
            'Default', self.project, '_member_'
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-admin'
        )

        NetworkDeleteFactory(bu_admin) \
            .set(NetworkDeleteFactory.NETWORK_CREATE,
                 clients=user1) \
            .set(NetworkDeleteFactory.NETWORK_DELETE,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)
