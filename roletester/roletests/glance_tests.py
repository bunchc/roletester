from base import Base as BaseTestCase
from roletester.actions.glance import image_create
from roletester.actions.glance import image_show
from roletester.actions.glance import image_update
from roletester.actions.glance import image_delete
from roletester.actions.glance import image_wait_for_status
from roletester.actions.glance import image_list
from roletester.actions.glance import image_download
from roletester.exc import GlanceForbidden
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


class ImageCreateFactory(Factory):
    _ACTIONS = [
        image_create,
    ]

    IMAGE_CREATE = 0


class TestSample(BaseTestCase):
    name = 'scratch'
    flavor = '1'
    image_file = '/Users/egle/Downloads/cirros-0.3.4-x86_64-disk.img'
    project = randomname()

    def test_cloud_admin_all(self):
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin', False
        )

        SampleFactory(cloud_admin) \
            .set(SampleFactory.IMAGE_CREATE,
                 args=(self.image_file,),
                 kwargs={'visibility': 'public'}) \
            .produce() \
            .run(context=self.context)

    def test_cloud_admin_download(self):
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin', False
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
            'Default', self.project, 'cloud-admin', False
        )
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin', False
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
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin', False
        )
        SampleFactory(bu_admin) \
            .set(SampleFactory.IMAGE_CREATE,
                 args=(self.image_file,), clients=creator) \
            .set(SampleFactory.IMAGE_UPDATE, clients=creator) \
            .set(SampleFactory.IMAGE_DOWNLOAD, clients=creator) \
            .set(SampleFactory.IMAGE_DELETE, clients=creator) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_same_domain_different_user(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin', False
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
            .set(SampleFactory.IMAGE_UPDATE, clients=creator) \
            .set(SampleFactory.IMAGE_DOWNLOAD, clients=creator) \
            .set(SampleFactory.IMAGE_DELETE, clients=creator) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_different_domain_different_user(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin', False
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
            .set(SampleFactory.IMAGE_LIST, expected_exceptions=[KeystoneUnauthorized]) \
            .set(SampleFactory.IMAGE_DOWNLOAD, expected_exceptions=[KeystoneUnauthorized]) \
            .set(SampleFactory.IMAGE_DELETE, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    ## bu-user
    def test_cloud_admin_bu_user(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'bu-user'
        )
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin', False
        )

        SampleFactory(cloud_admin) \
            .set(SampleFactory.IMAGE_CREATE,
                 args=(self.image_file,)) \
            .set(SampleFactory.IMAGE_SHOW, clients=creator) \
            .set(SampleFactory.IMAGE_LIST, clients=creator) \
            .set(SampleFactory.IMAGE_UPDATE, clients=creator, expected_exceptions=[GlanceForbidden]) \
            .set(SampleFactory.IMAGE_DELETE, clients=creator, expected_exceptions=[GlanceForbidden]) \
            .produce() \
            .run(context=self.context)

    def test_bu_user_create(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'bu-user'
        )

        ImageCreateFactory(creator) \
            .set(ImageCreateFactory.IMAGE_CREATE,
                 args=(self.image_file,), expected_exceptions=[GlanceForbidden]) \
            .produce() \
            .run(context=self.context)

    def test_bu_user_download(self):
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin', False
        )
        creator = self.km.find_user_credentials(
            'Default', self.project, 'bu-user'
        )
        SampleFactory(cloud_admin) \
            .set(SampleFactory.IMAGE_CREATE,
                 args=(self.image_file,),
                 kwargs={'visibility': 'public'}) \
            .set(SampleFactory.IMAGE_DOWNLOAD, clients=creator, expected_exceptions=[GlanceForbidden]) \
            .produce() \
            .run(context=self.context)

    # bu-brt

    def test_cloud_admin_bu_brt(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'bu-brt'
        )
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin', False
        )

        SampleFactory(cloud_admin) \
            .set(SampleFactory.IMAGE_CREATE,
                 args=(self.image_file,)) \
            .set(SampleFactory.IMAGE_SHOW, clients=creator) \
            .set(SampleFactory.IMAGE_LIST, clients=creator) \
            .set(SampleFactory.IMAGE_UPDATE, clients=creator, expected_exceptions=[GlanceForbidden]) \
            .set(SampleFactory.IMAGE_DELETE, clients=creator, expected_exceptions=[GlanceForbidden]) \
            .produce() \
            .run(context=self.context)

    def test_bu_brt_create(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'bu-brt'
        )

        ImageCreateFactory(creator) \
            .set(ImageCreateFactory.IMAGE_CREATE,
                 args=(self.image_file,), expected_exceptions=[GlanceForbidden]) \
            .produce() \
            .run(context=self.context)

    def test_bu_brt_download(self):
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin', False
        )
        creator = self.km.find_user_credentials(
            'Default', self.project, 'bu-brt'
        )
        SampleFactory(cloud_admin) \
            .set(SampleFactory.IMAGE_CREATE,
                 args=(self.image_file,),
                 kwargs={'visibility': 'public'}) \
            .set(SampleFactory.IMAGE_DOWNLOAD, clients=creator, expected_exceptions=[GlanceForbidden]) \
            .produce() \
            .run(context=self.context)

    #bu-poweruser
    def test_cloud_admin_bu_poweruser(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'bu-poweruser', False
        )
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin', False
        )

        SampleFactory(cloud_admin) \
            .set(SampleFactory.IMAGE_CREATE,
                 args=(self.image_file,)) \
            .set(SampleFactory.IMAGE_SHOW, clients=creator) \
            .set(SampleFactory.IMAGE_LIST, clients=creator) \
            .set(SampleFactory.IMAGE_UPDATE, clients=creator, expected_exceptions=[GlanceForbidden]) \
            .set(SampleFactory.IMAGE_DELETE, clients=creator, expected_exceptions=[GlanceForbidden]) \
            .produce() \
            .run(context=self.context)

    def test_bu_poweruser_create(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'bu-poweruser', False
        )

        ImageCreateFactory(creator) \
            .set(ImageCreateFactory.IMAGE_CREATE,
                 args=(self.image_file,), expected_exceptions=[GlanceForbidden]) \
            .produce() \
            .run(context=self.context)

    def test_bu_poweruser_download(self):
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin', False
        )
        creator = self.km.find_user_credentials(
            'Default', self.project, 'bu-poweruser', False
        )
        SampleFactory(cloud_admin) \
            .set(SampleFactory.IMAGE_CREATE,
                 args=(self.image_file,),
                 kwargs={'visibility': 'public'}) \
            .set(SampleFactory.IMAGE_DOWNLOAD, clients=creator, expected_exceptions=[GlanceForbidden]) \
            .produce() \
            .run(context=self.context)

    #cirt
    def test_cloud_admin_cirt(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cirt', False
        )
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin', False
        )

        SampleFactory(cloud_admin) \
            .set(SampleFactory.IMAGE_CREATE,
                 args=(self.image_file,)) \
            .set(SampleFactory.IMAGE_SHOW, clients=creator) \
            .set(SampleFactory.IMAGE_LIST, clients=creator) \
            .set(SampleFactory.IMAGE_UPDATE, clients=creator, expected_exceptions=[GlanceForbidden]) \
            .set(SampleFactory.IMAGE_DELETE, clients=creator, expected_exceptions=[GlanceForbidden]) \
            .produce() \
            .run(context=self.context)

    def test_cirt_create(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cirt', False
        )

        ImageCreateFactory(creator) \
            .set(ImageCreateFactory.IMAGE_CREATE,
                 args=(self.image_file,), expected_exceptions=[GlanceForbidden]) \
            .produce() \
            .run(context=self.context)

    def test_cirt_download(self):
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin', False
        )
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cirt', False
        )
        SampleFactory(cloud_admin) \
            .set(SampleFactory.IMAGE_CREATE,
                 args=(self.image_file,),
                 kwargs={'visibility': 'public'}) \
            .set(SampleFactory.IMAGE_DOWNLOAD, clients=creator, expected_exceptions=[GlanceForbidden]) \
            .produce() \
            .run(context=self.context)

    #cloud-support

    def test_cloud_support_all(self):
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-support'
        )

        SampleFactory(cloud_admin) \
            .set(SampleFactory.IMAGE_CREATE,
                 args=(self.image_file,),
                 kwargs={'visibility': 'public'}) \
            .produce() \
            .run(context=self.context)

    def test_cloud_support_download(self):
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-support'
        )

        SampleFactory(cloud_admin) \
            .set(SampleFactory.IMAGE_CREATE,
                 args=(self.image_file,),
                 kwargs={'visibility': 'public'}) \
            .set(SampleFactory.IMAGE_DOWNLOAD) \
            .produce() \
            .run(context=self.context)

    def test_cloud_support_same_domain_different_user(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-support'
        )
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-support'
        )

        SampleFactory(cloud_admin) \
            .set(SampleFactory.IMAGE_CREATE,
                 clients=creator,
                 args=(self.image_file,)) \
            .set(SampleFactory.IMAGE_WAIT) \
            .set(SampleFactory.IMAGE_LIST) \
            .produce() \
            .run(context=self.context)