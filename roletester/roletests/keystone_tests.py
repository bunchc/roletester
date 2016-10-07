from base import Base as BaseTestCase
from roletester.actions.keystone import user_create
from roletester.actions.keystone import user_delete
from roletester.actions.keystone import project_create
from roletester.actions.keystone import project_delete
from roletester.actions.keystone import project_list
from roletester.actions.keystone import project_list_user
from roletester.actions.keystone import role_grant_user_project
from roletester.actions.keystone import role_grant_user_domain
from roletester.actions.keystone import role_revoke_user_project
from roletester.actions.keystone import role_revoke_user_domain
from roletester.exc import KeystoneUnauthorized
from roletester.exc import KeystoneForbidden
from roletester.scenario import ScenarioFactory as Factory
from roletester.utils import randomname


from roletester.log import logging

logger = logging.getLogger("roletester.glance")


class SampleFactory(Factory):

    _ACTIONS = [
        project_create,
        project_list,
        user_create,
        role_grant_user_project,
        role_revoke_user_project,
        user_delete,
        project_delete,

    ]

    PROJECT_CREATE = 0
    PROJECT_LIST = 1
    USER_CREATE = 2
    ROLE_GRANT_USER_PROJECT = 3
    ROLE_REVOKE_USER_PROJECT = 4
    USER_DELETE = 5
    PROJECT_DELETE = 6


class GrantRoleFactory(Factory):

    _ACTIONS = [
        project_create,
        user_create,
        role_grant_user_domain
    ]

    PROJECT_CREATE = 0
    USER_CREATE = 1
    ROLE_GRANT_USER_DOMAIN = 2


class RevokeRoleFactory(Factory):

    _ACTIONS = [
        project_create,
        user_create,
        role_grant_user_domain,
        role_revoke_user_domain
    ]

    PROJECT_CREATE = 0
    USER_CREATE = 1
    ROLE_GRANT_USER_DOMAIN = 2
    ROLE_REVOKE_USER_DOMAIN = 3


class UserCreateFactory(Factory):

    _ACTIONS = [
        project_create,
        user_create,
    ]

    PROJECT_CREATE = 0
    USER_CREATE = 1


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


class ProjectCreateFactory(Factory):

    _ACTIONS = [
        project_create
    ]

    PROJECT_CREATE = 0

class ProjectListFactory(Factory):

    _ACTIONS = [
        project_create,
        user_create,
        project_list_user
    ]

    PROJECT_CREATE = 0
    USER_CREATE = 1
    PROJECT_LIST_USER = 2


class TestSample(BaseTestCase):

    name = 'scratch'
    flavor = '1'
    project = randomname()

    def test_cloud_admin_all(self):
        cloud_admin = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin', False
        )

        SampleFactory(cloud_admin) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_all(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin', False
        )
        bu_admin = self.km.find_user_credentials(
            'Default', 'torst', 'bu-admin'
        )
        domain_id = bu_admin.auth_kwargs['domain_id']
        GrantRoleFactory(bu_admin) \
            .set(GrantRoleFactory.PROJECT_CREATE,
                 kwargs={'domain':domain_id}, clients=creator) \
            .set(GrantRoleFactory.USER_CREATE, kwargs={'domain':domain_id}, clients=creator) \
            .set(GrantRoleFactory.ROLE_GRANT_USER_DOMAIN, kwargs={'domain':domain_id}, clients=creator) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_different_domain_different_user_grant_roles(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', self.project, 'cloud-admin', False
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-admin'
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        GrantRoleFactory(bu_admin) \
            .set(GrantRoleFactory.PROJECT_CREATE,
                kwargs={'name': "project1", 'domain': creator_domain_id},
                clients=creator) \
            .set(GrantRoleFactory.USER_CREATE,
                 kwargs={'domain': creator_domain_id},
                 clients=creator) \
            .set(GrantRoleFactory.ROLE_GRANT_USER_DOMAIN, kwargs={'domain': domain_id}, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_different_domain_different_user_revoke_roles(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', self.project, 'cloud-admin', False
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-admin'
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        RevokeRoleFactory(bu_admin) \
            .set(RevokeRoleFactory.PROJECT_CREATE,
                 kwargs={'name': "project1", 'domain': creator_domain_id},
                 clients=creator) \
            .set(RevokeRoleFactory.USER_CREATE,
                 kwargs={'domain': creator_domain_id},
                 clients=creator) \
            .set(RevokeRoleFactory.ROLE_GRANT_USER_DOMAIN,
                 kwargs={'domain': domain_id}, clients=creator) \
            .set(RevokeRoleFactory.ROLE_REVOKE_USER_DOMAIN,
                 kwargs={'domain': domain_id}, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_different_domain_different_user_delete(self):
        creator = self.km.find_user_credentials(
            'Default', self.project, 'cloud-admin', False
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-admin'
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']

        UserDeleteFactory(bu_admin) \
            .set(UserDeleteFactory.PROJECT_CREATE,
                 kwargs={'domain': creator_domain_id},
                 clients=creator) \
            .set(UserDeleteFactory.USER_CREATE,
                 kwargs={'domain': creator_domain_id},
                 clients=creator) \
            .set(UserDeleteFactory.USER_DELETE,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_admin_different_domain_different_project_delete(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', self.project, 'cloud-admin', False
        )
        bu_admin = self.km.find_user_credentials(
            'Domain2', self.project, 'bu-admin'
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        ProjectDeleteFactory(bu_admin) \
            .set(ProjectDeleteFactory.PROJECT_CREATE,
                 kwargs={'domain': creator_domain_id},
                 clients=creator) \
            .set(ProjectDeleteFactory.PROJECT_DELETE,
                 expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

## bu_user
    def test_bu_user_all(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'bu-user'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        ProjectListFactory(bu_admin) \
            .set(ProjectListFactory.PROJECT_CREATE,
                 kwargs={'domain': domain_id}) \
            .set(ProjectListFactory.USER_CREATE,
                 kwargs={'domain': domain_id}) \
            .set(ProjectListFactory.PROJECT_LIST_USER,
                 kwargs={'domain': creator_domain_id, 'user': username},
                 clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_user_different_domain(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', self.project, 'bu-user'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain_1', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        ProjectListFactory(bu_admin) \
            .set(ProjectListFactory.PROJECT_CREATE,
                 kwargs={'domain': domain_id}) \
            .set(ProjectListFactory.USER_CREATE,
                 kwargs={'domain': domain_id}) \
            .set(ProjectListFactory.PROJECT_LIST_USER,
                 kwargs={'domain': creator_domain_id, 'user': username},
                 clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_user_create_user(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', self.project, 'bu-user'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain_1', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        UserCreateFactory(bu_admin) \
            .set(UserCreateFactory.PROJECT_CREATE,
                 kwargs={'domain': domain_id}) \
            .set(ProjectListFactory.USER_CREATE,
                 kwargs={'domain': domain_id}, clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_user_delete_user(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'bu-user'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        UserDeleteFactory(bu_admin) \
            .set(UserDeleteFactory.USER_DELETE, clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_user_delete_project(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'bu-user'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        ProjectDeleteFactory(bu_admin) \
            .set(ProjectDeleteFactory.PROJECT_DELETE, clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_user_create_project(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'bu-user'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        ProjectCreateFactory(bu_admin) \
            .set(ProjectCreateFactory.PROJECT_CREATE, clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)
#cirt
    def test_cirt_user_all(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cirt'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        ProjectListFactory(bu_admin) \
            .set(ProjectListFactory.PROJECT_CREATE,
                 kwargs={'domain': domain_id}) \
            .set(ProjectListFactory.USER_CREATE,
                 kwargs={'domain': domain_id}) \
            .set(ProjectListFactory.PROJECT_LIST_USER,
                 kwargs={'domain': creator_domain_id, 'user': username},
                 clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_cirt_user_different_domain(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', self.project, 'cirt'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain_1', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        ProjectListFactory(bu_admin) \
            .set(ProjectListFactory.PROJECT_CREATE,
                 kwargs={'domain': domain_id}) \
            .set(ProjectListFactory.USER_CREATE,
                 kwargs={'domain': domain_id}) \
            .set(ProjectListFactory.PROJECT_LIST_USER,
                 kwargs={'domain': creator_domain_id, 'user': username},
                 clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_cirt_user_create_user(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', self.project, 'cirt'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain_1', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        UserCreateFactory(bu_admin) \
            .set(UserCreateFactory.PROJECT_CREATE,
                 kwargs={'domain': domain_id}) \
            .set(ProjectListFactory.USER_CREATE,
                 kwargs={'domain': domain_id}, clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_cirt_user_delete_user(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cirt'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        UserDeleteFactory(bu_admin) \
            .set(UserDeleteFactory.USER_DELETE, clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_cirt_user_delete_project(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cirt'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        ProjectDeleteFactory(bu_admin) \
            .set(ProjectDeleteFactory.PROJECT_DELETE, clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_cirt_user_create_project(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cirt'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        ProjectCreateFactory(bu_admin) \
            .set(ProjectCreateFactory.PROJECT_CREATE, clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)


#bu-poweruser
    def test_bu_poweruser_all(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'bu-poweruser'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        ProjectListFactory(bu_admin) \
            .set(ProjectListFactory.PROJECT_CREATE,
                 kwargs={'domain': domain_id}) \
            .set(ProjectListFactory.USER_CREATE,
                 kwargs={'domain': domain_id}) \
            .set(ProjectListFactory.PROJECT_LIST_USER,
                 kwargs={'domain': creator_domain_id, 'user': username},
                 clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_poweruser_different_domain(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', self.project, 'bu-poweruser'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain_1', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        ProjectListFactory(bu_admin) \
            .set(ProjectListFactory.PROJECT_CREATE,
                 kwargs={'domain': domain_id}) \
            .set(ProjectListFactory.USER_CREATE,
                 kwargs={'domain': domain_id}) \
            .set(ProjectListFactory.PROJECT_LIST_USER,
                 kwargs={'domain': creator_domain_id, 'user': username},
                 clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_poweruser_create_user(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', self.project, 'bu-poweruser'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain_1', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        UserCreateFactory(bu_admin) \
            .set(UserCreateFactory.PROJECT_CREATE,
                 kwargs={'domain': domain_id}) \
            .set(ProjectListFactory.USER_CREATE,
                 kwargs={'domain': domain_id}, clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_poweruser_delete_user(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'bu-poweruser'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        UserDeleteFactory(bu_admin) \
            .set(UserDeleteFactory.USER_DELETE, clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_poweruser_delete_project(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'bu-poweruser'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        ProjectDeleteFactory(bu_admin) \
            .set(ProjectDeleteFactory.PROJECT_DELETE, clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_poweruser_create_project(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'bu-poweruser'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        ProjectCreateFactory(bu_admin) \
            .set(ProjectCreateFactory.PROJECT_CREATE, clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

#cloud-support
    def test_cloud_support_all(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cloud-support'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        ProjectListFactory(bu_admin) \
            .set(ProjectListFactory.PROJECT_CREATE,
                 kwargs={'domain': domain_id}) \
            .set(ProjectListFactory.USER_CREATE,
                 kwargs={'domain': domain_id}) \
            .set(ProjectListFactory.PROJECT_LIST_USER,
                 kwargs={'domain': creator_domain_id, 'user': username},
                 clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_cloud_support_different_domain(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', self.project, 'cloud-support'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain_1', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        ProjectListFactory(bu_admin) \
            .set(ProjectListFactory.PROJECT_CREATE,
                 kwargs={'domain': domain_id}) \
            .set(ProjectListFactory.USER_CREATE,
                 kwargs={'domain': domain_id}) \
            .set(ProjectListFactory.PROJECT_LIST_USER,
                 kwargs={'domain': creator_domain_id, 'user': username},
                 clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_cloud_support_create_user(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', self.project, 'cloud-support'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain_1', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        UserCreateFactory(bu_admin) \
            .set(UserCreateFactory.PROJECT_CREATE,
                 kwargs={'domain': domain_id}) \
            .set(ProjectListFactory.USER_CREATE,
                 kwargs={'domain': domain_id}, clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_cloud_support_delete_user(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cloud-support'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        UserDeleteFactory(bu_admin) \
            .set(UserDeleteFactory.USER_DELETE, clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_cloud_support_delete_project(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cloud-support'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        ProjectDeleteFactory(bu_admin) \
            .set(ProjectDeleteFactory.PROJECT_DELETE, clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_cloud_support_create_project(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cloud-support'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        ProjectCreateFactory(bu_admin) \
            .set(ProjectCreateFactory.PROJECT_CREATE, clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)


#bu-brt
    def test_bu_brt_all(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'bu-brt'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        ProjectListFactory(bu_admin) \
            .set(ProjectListFactory.PROJECT_CREATE,
                 kwargs={'domain': domain_id}) \
            .set(ProjectListFactory.USER_CREATE,
                 kwargs={'domain': domain_id}) \
            .set(ProjectListFactory.PROJECT_LIST_USER,
                 kwargs={'domain': creator_domain_id, 'user': username},
                 clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_brt_different_domain(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', self.project, 'bu-brt'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain_1', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        ProjectListFactory(bu_admin) \
            .set(ProjectListFactory.PROJECT_CREATE,
                 kwargs={'domain': domain_id}) \
            .set(ProjectListFactory.USER_CREATE,
                 kwargs={'domain': domain_id}) \
            .set(ProjectListFactory.PROJECT_LIST_USER,
                 kwargs={'domain': creator_domain_id, 'user': username},
                 clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_brt_create_user(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', self.project, 'bu-brt'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain_1', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        UserCreateFactory(bu_admin) \
            .set(UserCreateFactory.PROJECT_CREATE,
                 kwargs={'domain': domain_id}) \
            .set(ProjectListFactory.USER_CREATE,
                 kwargs={'domain': domain_id}, clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_brt_delete_user(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'bu-brt'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        UserDeleteFactory(bu_admin) \
            .set(UserDeleteFactory.USER_DELETE, clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_brt_delete_project(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'bu-brt'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        ProjectDeleteFactory(bu_admin) \
            .set(ProjectDeleteFactory.PROJECT_DELETE, clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)

    def test_bu_brt_create_project(self):
        creator = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'bu-brt'
        )
        bu_admin = self.km.find_user_credentials(
            'CustomDomain', 'torst', 'cloud-admin', False
        )
        creator_domain_id = creator.auth_kwargs['domain_id']
        domain_id = bu_admin.auth_kwargs['domain_id']
        username = creator.auth_kwargs['username']
        ProjectCreateFactory(bu_admin) \
            .set(ProjectCreateFactory.PROJECT_CREATE, clients=creator, expected_exceptions=[KeystoneUnauthorized]) \
            .produce() \
            .run(context=self.context)