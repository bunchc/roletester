from base import Base as BaseTestCase
from roletester.actions.glance import image_create
from roletester.actions.glance import image_delete
from roletester.actions.glance import image_wait_for_status
from roletester.actions.cinder import volume_create
from roletester.actions.cinder import volume_show
from roletester.actions.cinder import volume_update
from roletester.actions.cinder import volume_create_image
from roletester.actions.cinder import volume_attach
from roletester.actions.cinder import volume_detach
from roletester.actions.cinder import volume_delete
from roletester.actions.cinder import volume_wait_for_status
from roletester.actions.nova import server_create
from roletester.actions.nova import server_wait_for_status
# from roletester.exc import CinderUnauthorized
from roletester.exc import KeystoneUnauthorized
from roletester.scenario import ScenarioFactory as Factory
from roletester.utils import randomname


from roletester.log import logging

logger = logging.getLogger("roletester.cinder")


class SampleFactory(Factory):

    _ACTIONS = [
        volume_create,
        volume_wait_for_status,
        volume_show,
        volume_update,
        volume_create_image,
        image_wait_for_status,
        image_create,
        image_wait_for_status,
        server_create,
        server_wait_for_status,
        volume_attach,
        volume_detach,
        volume_delete,
        image_delete
    ]

    VOLUME_CREATE = 0
    VOLUME_WAIT = 1
    VOLUME_SHOW = 2
    VOLUME_UPDATE = 3
    VOLUME_CREATE_IMAGE = 4
    VOLUME_IMAGE_WAIT = 5
    IMAGE_CREATE = 6
    IMAGE_WAIT = 7
    SERVER_CREATE = 8
    SERVER_WAIT = 9
    VOLUME_ATTACH = 10
    VOLUME_DETACH = 11
    VOLUME_DELETE = 12
    VOLUME_DELETE_IMAGE = 13


class VolumeImageFactory(Factory):

    _ACTIONS = [
        volume_create,
        volume_wait_for_status,
        volume_show,
        volume_update,
        volume_create_image,
    ]

    VOLUME_CREATE = 0
    VOLUME_WAIT = 1
    VOLUME_SHOW = 2
    VOLUME_UPDATE = 3
    VOLUME_CREATE_IMAGE = 4


class VolumeAttachFactory(Factory):

    _ACTIONS = [
        volume_create,
        volume_wait_for_status,
        image_create,
        image_wait_for_status,
        server_create,
        server_wait_for_status,
        volume_attach
    ]

    VOLUME_CREATE = 0
    VOLUME_WAIT = 1
    IMAGE_CREATE = 2
    IMAGE_WAIT = 3
    SERVER_CREATE = 4
    SERVER_WAIT = 5
    VOLUME_ATTACH = 6


class VolumeDetachFactory(Factory):

    _ACTIONS = [
        volume_create,
        volume_wait_for_status,
        image_create,
        image_wait_for_status,
        server_create,
        server_wait_for_status,
        volume_attach,
        volume_detach
    ]

    VOLUME_CREATE = 0
    VOLUME_WAIT = 1
    IMAGE_CREATE = 2
    IMAGE_WAIT = 3
    SERVER_CREATE = 4
    SERVER_WAIT = 5
    VOLUME_ATTACH = 6
    VOLUME_DETACH = 7


class VolumeDeleteFactory(Factory):

    _ACTIONS = [
        volume_create,
        volume_delete
    ]

    VOLUME_CREATE = 0
    VOLUME_DELETE = 1


class TestSample(BaseTestCase):

    name = 'scratch'
    flavor = '1'
    image_file = '/home/chalupaul/cirros-0.3.4-x86_64-disk.img'
    project = randomname()

    def test_cloud_admin_all(self):
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        volume_image_kwargs = {'image_key': 'volume_image_id'}
        SampleFactory(cloud_admin) \
            .set(SampleFactory.VOLUME_IMAGE_WAIT,
                 kwargs=volume_image_kwargs) \
            .set(SampleFactory.IMAGE_CREATE,
                 args=(self.image_file,)) \
            .set(SampleFactory.VOLUME_DELETE_IMAGE,
                 kwargs=volume_image_kwargs) \
            .produce() \
            .run(context=self.context)

    def test_cloud_admin_same_domain_different_user(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, '_member_'
        )
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        volume_image_kwargs = {'image_key': 'volume_image_id'}
        SampleFactory(cloud_admin) \
            .set(SampleFactory.VOLUME_CREATE,
                 clients=creator) \
            .set(SampleFactory.VOLUME_WAIT,
                 clients=creator) \
            .set(SampleFactory.VOLUME_IMAGE_WAIT,
                 kwargs=volume_image_kwargs) \
            .set(SampleFactory.IMAGE_CREATE,
                 clients=creator,
                 args=(self.image_file,)) \
            .set(SampleFactory.SERVER_CREATE,
                 clients=creator) \
            .set(SampleFactory.SERVER_WAIT,
                 clients=creator) \
            .set(SampleFactory.VOLUME_DELETE_IMAGE,
                 clients=creator,
                 kwargs=volume_image_kwargs) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_all(self):
        bu_admin = self.km.find_user_credentials(
            'Default', self.project, 'bu-admin'
        )
        volume_image_kwargs = {'image_key': 'volume_image_id'}
        SampleFactory(bu_admin) \
            .set(SampleFactory.VOLUME_IMAGE_WAIT,
                 kwargs=volume_image_kwargs) \
            .set(SampleFactory.IMAGE_CREATE,
                 args=(self.image_file,)) \
            .set(SampleFactory.VOLUME_DELETE_IMAGE,
                 kwargs=volume_image_kwargs) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_same_domain_different_user(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, '_member_'
        )
        bu_admin = self.km.find_user_credentials(
            'Default', self.project, 'bu-admin'
        )
        volume_image_kwargs = {'image_key': 'volume_image_id'}
        SampleFactory(bu_admin) \
            .set(SampleFactory.VOLUME_CREATE,
                 clients=creator) \
            .set(SampleFactory.VOLUME_WAIT,
                 clients=creator) \
            .set(SampleFactory.VOLUME_IMAGE_WAIT,
                 kwargs=volume_image_kwargs) \
            .set(SampleFactory.IMAGE_CREATE,
                 clients=creator,
                 args=(self.image_file,)) \
            .set(SampleFactory.SERVER_CREATE,
                 clients=creator) \
            .set(SampleFactory.SERVER_WAIT,
                 clients=creator) \
            .set(SampleFactory.VOLUME_DELETE_IMAGE,
                 kwargs=volume_image_kwargs) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_different_domain_different_user_volume_create_image(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, '_member_'
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-admin'
        )
        VolumeImageFactory(bu_admin) \
            .set(VolumeImageFactory.VOLUME_CREATE,
                 clients=creator) \
            .set(VolumeImageFactory.VOLUME_WAIT,
                 clients=creator) \
            .set(VolumeImageFactory.VOLUME_SHOW,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .set(VolumeImageFactory.VOLUME_UPDATE,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .set(VolumeImageFactory.VOLUME_CREATE_IMAGE,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_different_domain_different_user_volume_attach(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, '_member_'
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-admin'
        )

        VolumeAttachFactory(bu_admin) \
            .set(VolumeAttachFactory.VOLUME_CREATE,
                 clients=creator) \
            .set(VolumeAttachFactory.VOLUME_WAIT,
                 clients=creator) \
            .set(VolumeAttachFactory.IMAGE_CREATE,
                 clients=creator,
                 args=(self.image_file,)) \
            .set(VolumeAttachFactory.IMAGE_WAIT,
                 clients=creator) \
            .set(VolumeAttachFactory.SERVER_CREATE,
                 clients=creator) \
            .set(VolumeAttachFactory.SERVER_WAIT,
                 clients=creator) \
            .set(VolumeAttachFactory.VOLUME_ATTACH,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_different_domain_different_user_volume_detach(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, '_member_'
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-admin'
        )

        VolumeDetachFactory(bu_admin) \
            .set(VolumeDetachFactory.VOLUME_CREATE,
                 clients=creator) \
            .set(VolumeDetachFactory.VOLUME_WAIT,
                 clients=creator) \
            .set(VolumeDetachFactory.IMAGE_CREATE,
                 clients=creator,
                 args=(self.image_file,)) \
            .set(VolumeDetachFactory.IMAGE_WAIT,
                 clients=creator) \
            .set(VolumeDetachFactory.SERVER_CREATE,
                 clients=creator) \
            .set(VolumeDetachFactory.SERVER_WAIT,
                 clients=creator) \
            .set(VolumeDetachFactory.VOLUME_ATTACH,
                 clients=creator) \
            .set(VolumeDetachFactory.VOLUME_DETACH,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_different_domain_different_user_volume_delete(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, '_member_'
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-admin'
        )
        VolumeDeleteFactory(bu_admin) \
            .set(VolumeDeleteFactory.VOLUME_CREATE,
                 clients=creator) \
            .set(VolumeDeleteFactory.VOLUME_DELETE,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)
