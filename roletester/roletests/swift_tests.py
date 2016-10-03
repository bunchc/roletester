from base import Base as BaseTestCase
from roletester.actions.swift import swift_container_create
from roletester.actions.swift import swift_container_delete
from roletester.actions.swift import swift_container_add_metadata
from roletester.actions.swift import swift_object_put
from roletester.actions.swift import swift_object_delete
from roletester.actions.swift import swift_object_get
from roletester.exc import SwiftClientException
from roletester.scenario import ScenarioFactory as Factory
from roletester.utils import randomname
from roletester.exc import SwiftForbidden


from roletester.log import logging

logger = logging.getLogger("roletester.glance")


class SampleFactory(Factory):

    _ACTIONS = [
        swift_container_create,
        swift_container_add_metadata,
        swift_object_put,
        swift_object_get,
        swift_object_delete,
        swift_container_delete
    ]

    SWIFT_CONTAINER_CREATE = 0
    SWIFT_CONTAINER_ADD_METADATA = 1
    SWIFT_OBJECT_PUT = 2
    SWIFT_OBJECT_GET = 3
    SWIFT_OBJECT_DELETE = 4
    SWIFT_CONTAINER_DELETE = 5


class SwiftCreateFactory(Factory):

    _ACTIONS = [
        swift_container_create,
        swift_container_add_metadata,
        swift_object_put,
        swift_object_get,
    ]

    SWIFT_CONTAINER_CREATE = 0
    SWIFT_CONTAINER_ADD_METADATA = 1
    SWIFT_OBJECT_PUT = 2
    SWIFT_OBJECT_GET = 3


class SwiftContainerFactory(Factory):

    _ACTIONS = [
        swift_container_create,
    ]

    SWIFT_CONTAINER_CREATE = 0


class SwiftObjectCreateFactory(Factory):

    _ACTIONS = [
        swift_container_create,
        swift_object_put,
    ]

    SWIFT_CONTAINER_CREATE = 0
    SWIFT_OBJECT_PUT = 1


class TestSample(BaseTestCase):

    project = randomname()

    def test_cloud_admin_all(self):
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        SampleFactory(cloud_admin) \
            .produce() \
            .run(context=self.context)

    def test_cloud_admin_create_all(self):
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        SwiftCreateFactory(cloud_admin) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_all(self):
        bu_admin = self.km.find_user_credentials(
            'Default', self.project, 'bu-admin'
        )
        SampleFactory(bu_admin) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_different_domain(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'bu-admin'
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-admin'
        )
        SampleFactory(bu_admin) \
            .set(SampleFactory.SWIFT_CONTAINER_CREATE,
                 clients=creator) \
            .set(SampleFactory.SWIFT_CONTAINER_ADD_METADATA,
                 expected_exceptions=[SwiftClientException]) \
            .set(SampleFactory.SWIFT_OBJECT_PUT,
                 clients=creator) \
            .set(SampleFactory.SWIFT_OBJECT_GET,
                 expected_exceptions=[SwiftClientException]) \
            .set(SampleFactory.SWIFT_OBJECT_DELETE,
                 expected_exceptions=[SwiftClientException]) \
            .set(SampleFactory.SWIFT_CONTAINER_DELETE,
                 expected_exceptions=[SwiftClientException]) \
            .produce() \
            .run(context=self.context)

    def test_bu_poweruser_all(self):
        bu_admin = self.km.find_user_credentials(
            'Default', self.project, 'bu-poweruser'
        )
        SampleFactory(bu_admin) \
            .produce() \
            .run(context=self.context)

    def test_bu_poweruser_different_domain(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'bu-poweruser'
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-poweruser'
        )
        SampleFactory(bu_admin) \
            .set(SampleFactory.SWIFT_CONTAINER_CREATE,
                 clients=creator) \
            .set(SampleFactory.SWIFT_CONTAINER_ADD_METADATA,
                 expected_exceptions=[SwiftClientException]) \
            .set(SampleFactory.SWIFT_OBJECT_PUT,
                 clients=creator) \
            .set(SampleFactory.SWIFT_OBJECT_GET,
                 expected_exceptions=[SwiftClientException]) \
            .set(SampleFactory.SWIFT_OBJECT_DELETE,
                 expected_exceptions=[SwiftClientException]) \
            .set(SampleFactory.SWIFT_CONTAINER_DELETE,
                 expected_exceptions=[SwiftClientException]) \
            .produce() \
            .run(context=self.context)

    def test_cloud_support_all(self):
        bu_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-support'
        )
        SampleFactory(bu_admin) \
            .produce() \
            .run(context=self.context)

    def test_cloud_support_different_domain(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-support'
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'cloud-support'
        )
        SampleFactory(bu_admin) \
            .set(SampleFactory.SWIFT_CONTAINER_CREATE,
                 clients=creator) \
            .set(SampleFactory.SWIFT_CONTAINER_ADD_METADATA,
                 expected_exceptions=[SwiftClientException]) \
            .set(SampleFactory.SWIFT_OBJECT_PUT,
                 clients=creator) \
            .set(SampleFactory.SWIFT_OBJECT_GET,
                 expected_exceptions=[SwiftClientException]) \
            .set(SampleFactory.SWIFT_OBJECT_DELETE,
                 expected_exceptions=[SwiftClientException]) \
            .set(SampleFactory.SWIFT_CONTAINER_DELETE,
                 expected_exceptions=[SwiftClientException]) \
            .produce() \
            .run(context=self.context)

    def test_bu_brt_all(self):
        bu_admin = self.km.find_user_credentials(
            'Default', self.project, 'bu-brt'
        )
        SampleFactory(bu_admin) \
            .produce() \
            .run(context=self.context)

    def test_bu_brt_different_domain(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'bu-brt'
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-brt'
        )
        SampleFactory(bu_admin) \
            .set(SampleFactory.SWIFT_CONTAINER_CREATE,
                 clients=creator) \
            .set(SampleFactory.SWIFT_CONTAINER_ADD_METADATA,
                 expected_exceptions=[SwiftClientException]) \
            .set(SampleFactory.SWIFT_OBJECT_PUT,
                 clients=creator) \
            .set(SampleFactory.SWIFT_OBJECT_GET,
                 expected_exceptions=[SwiftClientException]) \
            .set(SampleFactory.SWIFT_OBJECT_DELETE,
                 expected_exceptions=[SwiftClientException]) \
            .set(SampleFactory.SWIFT_CONTAINER_DELETE,
                 expected_exceptions=[SwiftClientException]) \
            .produce() \
            .run(context=self.context)

    def test_cirt_create(self):
        bu_admin = self.km.find_user_credentials(
            'Default', self.project, 'cirt'
        )
        SwiftContainerFactory(bu_admin) \
            .set(SwiftContainerFactory.SWIFT_CONTAINER_CREATE, expected_exceptions=[SwiftForbidden]) \
            .produce() \
            .run(context=self.context)

    def test_cirt_add_metadata(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        bu_admin = self.km.find_user_credentials(
            'Default', self.project, 'cirt'
        )
        SwiftCreateFactory(creator) \
            .set(SwiftCreateFactory.SWIFT_CONTAINER_ADD_METADATA, clients=bu_admin,
                 expected_exceptions=[SwiftClientException]) \
            .produce() \
            .run(context=self.context)

    def test_cirt_add_object(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        bu_admin = self.km.find_user_credentials(
            'Default', self.project, 'cirt'
        )
        SwiftObjectCreateFactory(creator) \
            .set(SwiftObjectCreateFactory.SWIFT_OBJECT_PUT, clients=bu_admin,
                 expected_exceptions=[SwiftClientException]) \
            .produce() \
            .run(context=self.context)

    def test_cirt_get_object(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        bu_admin = self.km.find_user_credentials(
            'Default', self.project, 'cirt'
        )
        SampleFactory(creator) \
            .set(SampleFactory.SWIFT_OBJECT_GET, clients=bu_admin,
                 expected_exceptions=[SwiftClientException]) \
            .produce() \
            .run(context=self.context)

    def test_cirt_delete_container(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        bu_admin = self.km.find_user_credentials(
            'Default', self.project, 'cirt'
        )
        SampleFactory(creator) \
            .set(SampleFactory.SWIFT_CONTAINER_DELETE, clients=bu_admin,
                 expected_exceptions=[SwiftClientException]) \
            .set(SampleFactory.SWIFT_OBJECT_DELETE, clients=bu_admin,
                 expected_exceptions=[SwiftClientException]) \
            .produce() \
            .run(context=self.context)

    def test_bu_user_create(self):
        bu_admin = self.km.find_user_credentials(
            'Default', self.project, 'bu-user'
        )
        SwiftContainerFactory(bu_admin) \
            .set(SwiftContainerFactory.SWIFT_CONTAINER_CREATE, expected_exceptions=[SwiftForbidden]) \
            .produce() \
            .run(context=self.context)

    def test_bu_user_add_metadata(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        bu_admin = self.km.find_user_credentials(
            'Default', self.project, 'bu-user'
        )
        SwiftCreateFactory(creator) \
            .set(SwiftCreateFactory.SWIFT_CONTAINER_ADD_METADATA, clients=bu_admin,
                 expected_exceptions=[SwiftClientException]) \
            .produce() \
            .run(context=self.context)

    def test_bu_user_add_object(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        bu_admin = self.km.find_user_credentials(
            'Default', self.project, 'bu-user'
        )
        SwiftObjectCreateFactory(creator) \
            .set(SwiftObjectCreateFactory.SWIFT_OBJECT_PUT, clients=bu_admin,
                 expected_exceptions=[SwiftClientException]) \
            .produce() \
            .run(context=self.context)

    def test_bu_user_get_object(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        bu_admin = self.km.find_user_credentials(
            'Default', self.project, 'bu-user'
        )
        SampleFactory(creator) \
            .set(SampleFactory.SWIFT_OBJECT_GET, clients=bu_admin,
                 expected_exceptions=[SwiftClientException]) \
            .produce() \
            .run(context=self.context)

    def test_bu_user_delete_container(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        bu_admin = self.km.find_user_credentials(
            'Default', self.project, 'bu-user'
        )
        SampleFactory(creator) \
            .set(SampleFactory.SWIFT_CONTAINER_DELETE, clients=bu_admin,
                 expected_exceptions=[SwiftClientException]) \
            .set(SampleFactory.SWIFT_OBJECT_DELETE, clients=bu_admin,
                 expected_exceptions=[SwiftClientException]) \
            .produce() \
            .run(context=self.context)

