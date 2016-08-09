from base import Base as BaseTestCase
from roletester.actions.glance import image_create
from roletester.actions.glance import image_show
from roletester.actions.glance import image_update
from roletester.actions.glance import image_delete
from roletester.actions.glance import image_wait_for_status
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
        image_update,
        image_delete
    ]

    IMAGE_CREATE = 0
    IMAGE_WAIT = 1
    IMAGE_SHOW = 2
    IMAGE_UPDATE = 3
    IMAGE_DELETE = 4


class TestSample(BaseTestCase):

    name = 'scratch'
    flavor = '1'
    image_file = '/home/chalupaul/cirros-0.3.4-x86_64-disk.img'
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

    def test_cloud_admin_same_domain_different_user(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, '_member_'
        )
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'admin'
        )

        SampleFactory(cloud_admin) \
            .set(SampleFactory.IMAGE_CREATE,
                 clients=creator,
                 args=(self.image_file,)) \
            .set(SampleFactory.IMAGE_WAIT, clients=creator) \
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
            .set(SampleFactory.IMAGE_WAIT, clients=creator) \
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
                 args=(self.image_file,)) \
            .set(SampleFactory.IMAGE_WAIT, clients=creator) \
            .set(SampleFactory.IMAGE_SHOW, expected_exceptions=[KeystoneUnauthorized]) \
            .set(SampleFactory.IMAGE_UPDATE, expected_exceptions=[KeystoneUnauthorized]) \
            .set(SampleFactory.IMAGE_DELETE, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)
