from base import Base as BaseTestCase
from roletester.actions.glance import image_create
from roletester.actions.glance import image_show
from roletester.actions.glance import image_update
from roletester.actions.glance import image_delete
from roletester.actions.glance import image_wait_for_status
from roletester.actions.glance import image_list
from roletester.actions.glance import image_download
from roletester.exc import KeystoneUnauthorized
from roletester.scenario import ScenarioFactory as Factory
from roletester.utils import randomname

from roletester.log import logging

logger = logging.getLogger("roletester.glance")


class SampleFactory(Factory):
    _ACTIONS = [
        image_create,
        image_wait_for_status,
        image_show,
        image_list,
        image_download,
        image_update,
        image_delete
    ]

    IMAGE_CREATE = 0
    IMAGE_WAIT = 1
    IMAGE_SHOW = 2
    IMAGE_LIST = 3
    IMAGE_DOWNLOAD = 4
    IMAGE_UPDATE = 5
    IMAGE_DELETE = 6


class TestSample(BaseTestCase):
    name = 'scratch'
    flavor = '1'
    image_file = '/Users/egle/Downloads/cirros-0.3.4-x86_64-disk.img'
    project = randomname()

    def test_cloud_admin_all(self):
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )

        SampleFactory(cloud_admin) \
            .set(SampleFactory.IMAGE_CREATE,
                 args=(self.image_file,),
                 kwargs={'visibility': 'public'}) \
            .produce() \
            .run(context=self.context)

    def test_cloud_admin_download(self):
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )

        SampleFactory(cloud_admin) \
            .set(SampleFactory.IMAGE_CREATE,
                 args=(self.image_file,),
                 kwargs={'visibility': 'public'}) \
            .set(SampleFactory.IMAGE_DOWNLOAD) \
            .produce() \
            .run(context=self.context)

    def test_cloud_admin_same_domain_different_user(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, '_member_'
        )
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )

        SampleFactory(cloud_admin) \
            .set(SampleFactory.IMAGE_CREATE,
                 clients=creator,
                 args=(self.image_file,)) \
            .set(SampleFactory.IMAGE_WAIT) \
            .set(SampleFactory.IMAGE_LIST) \
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

    def test_bu_admin_same_domain_different_user(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, '_member_'
        )
        bu_admin = self.km.find_user_credentials(
            'Default', self.project, 'bu-admin'
        )

        SampleFactory(bu_admin) \
            .set(SampleFactory.IMAGE_CREATE,
                 clients=creator,
                 args=(self.image_file,)) \
            .set(SampleFactory.IMAGE_WAIT) \
            .set(SampleFactory.IMAGE_LIST, clients=creator) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_different_domain_different_user(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, '_member_'
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-admin'
        )

        SampleFactory(bu_admin) \
            .set(SampleFactory.IMAGE_CREATE,
                 clients=creator,
                 args=self.image_file) \
            .set(SampleFactory.IMAGE_WAIT, clients=creator) \
            .set(SampleFactory.IMAGE_SHOW, expected_exceptions=[KeystoneUnauthorized]) \
            .set(SampleFactory.IMAGE_UPDATE, expected_exceptions=[KeystoneUnauthorized]) \
            .set(SampleFactory.IMAGE_LIST, expected_exceptions=[KeystoneUnauthorized]) \
            .set(SampleFactory.IMAGE_DELETE, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    ## TODO: test these once the policies are written
    ## bu-user
    def test_cloud_admin_bu_user(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'bu-user'
        )
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )

        SampleFactory(cloud_admin) \
            .set(SampleFactory.IMAGE_CREATE,
                 args=self.image_file) \
            .set(SampleFactory.IMAGE_SHOW, clients=creator) \
            .set(SampleFactory.IMAGE_LIST, clients=creator) \
            .set(SampleFactory.IMAGE_UPDATE, clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .set(SampleFactory.IMAGE_DELETE, clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_user_create(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'bu-user'
        )

        SampleFactory(creator) \
            .set(SampleFactory.IMAGE_CREATE,
                 args=(self.image_file,), expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_user_download(self):
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        creator = self.km.find_user_credentials(
            'Default', self.project, 'bu-user'
        )
        SampleFactory(cloud_admin) \
            .set(SampleFactory.IMAGE_CREATE,
                 args=(self.image_file,),
                 kwargs={'visibility': 'public'}) \
            .set(SampleFactory.IMAGE_DOWNLOAD, clients=creator) \
            .produce() \
            .run(context=self.context)