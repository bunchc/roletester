from base import Base as BaseTestCase
from roletester.actions.keystone import user_create
from roletester.actions.keystone import user_delete
from roletester.actions.keystone import project_create
from roletester.actions.keystone import project_delete
from roletester.actions.keystone import role_grant_user_project
from roletester.actions.keystone import role_revoke_user_project
from roletester.exc import KeystoneUnauthorized
from roletester.scenario import ScenarioFactory as Factory
from roletester.utils import randomname


from roletester.log import logging

logger = logging.getLogger("roletester.glance")


class SampleFactory(Factory):

    _ACTIONS = [
        project_create,
        user_create,
        role_grant_user_project,
        role_revoke_user_project,
        user_delete,
        project_delete,

    ]

    PROJECT_CREATE = 0
    USER_CREATE = 1
    ROLE_GRANT_USER_PROJECT = 2
    ROLE_REVOKE_USER_PROJECT = 3
    USER_DELETE = 4
    PROJECT_DELETE = 5


class GrantRoleFactory(Factory):

    _ACTIONS = [
        project_create,
        user_create,
        role_grant_user_project,
    ]

    PROJECT_CREATE = 0
    USER_CREATE = 1
    ROLE_GRANT_USER_PROJECT = 2


class RevokeRoleFactory(Factory):

    _ACTIONS = [
        project_create,
        user_create,
        role_grant_user_project,
        role_revoke_user_project
    ]

    PROJECT_CREATE = 0
    USER_CREATE = 1
    ROLE_GRANT_USER_PROJECT = 2
    ROLE_REVOKE_USER_PROJECT = 3


class UserDeleteFactory(Factory):

    _ACTIONS = [
        project_create,
        user_create,
        user_delete
    ]

    PROJECT_CREATE = 0
    USER_CREATE = 1
    USER_DELETE = 2


class ProjectDeleteFactory(Factory):

    _ACTIONS = [
        project_create,
        project_delete
    ]

    PROJECT_CREATE = 0
    PROJECT_DELETE = 1


class TestSample(BaseTestCase):

    name = 'scratch'
    flavor = '1'
    project = randomname()

    def test_cloud_admin_all(self):
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin'
        )
        SampleFactory(cloud_admin) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_all(self):
        bu_admin = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'bu-admin'
        )
        domain_id = bu_admin.get_keystone().user_domain_id
        print "BEHOLD %s" % bu_admin.auth_kwargs
        SampleFactory(bu_admin) \
            .set(GrantRoleFactory.PROJECT_CREATE,
                 kwargs={'name':"egle1", 'domain':domain_id}, clients=bu_admin) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_different_domain_different_user_grant_roles(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'bu-admin'
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-admin'
        )
        GrantRoleFactory(bu_admin) \
            .set(GrantRoleFactory.PROJECT_CREATE,
                 clients=creator) \
            .set(GrantRoleFactory.USER_CREATE,
                 clients=creator) \
            .set(GrantRoleFactory.ROLE_GRANT_USER_PROJECT,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_different_domain_different_user_revoke_roles(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'bu-admin'
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-admin'
        )
        RevokeRoleFactory(bu_admin) \
            .set(RevokeRoleFactory.PROJECT_CREATE,
                 clients=creator) \
            .set(RevokeRoleFactory.USER_CREATE,
                 clients=creator) \
            .set(RevokeRoleFactory.ROLE_GRANT_USER_PROJECT,
                 clients=creator) \
            .set(RevokeRoleFactory.ROLE_REVOKE_USER_PROJECT,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_different_domain_different_user_delete(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'bu-admin'
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-admin'
        )
        UserDeleteFactory(bu_admin) \
            .set(UserDeleteFactory.PROJECT_CREATE,
                 clients=creator) \
            .set(UserDeleteFactory.USER_CREATE,
                 clients=creator) \
            .set(UserDeleteFactory.USER_DELETE,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_different_domain_different_project_delete(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'bu-admin'
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-admin'
        )
        ProjectDeleteFactory(bu_admin) \
            .set(ProjectDeleteFactory.PROJECT_CREATE,
                 clients=creator) \
            .set(ProjectDeleteFactory.PROJECT_DELETE,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

## bu_user
    #todo : fix this
    def test_bu_user_all(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'bu-user'
        )
        bu_admin = self.km.find_user_credentials(
            'Default', self.project, 'bu-admin'
        )
        GrantRoleFactory(bu_admin) \
            .set(GrantRoleFactory.PROJECT_CREATE) \
            .set(GrantRoleFactory.USER_CREATE) \
            .set(GrantRoleFactory.ROLE_GRANT_USER_PROJECT,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)
