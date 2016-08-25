"""Module containing actions to manage keystone projects."""
from roletester.log import logging
from roletester.exc import KeystoneNotFound

logger = logging.getLogger('roletester.actions.keystone.project')


def create(clients, context, name="test_project", domain='Default'):
    """Create a new keystone project

    Sets context['project_obj']

    :param clients: Client Manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference object
    :type context: Dict
    :param name: Name for the new project
    :type name: String
    :param domain: The domain in which to create the project
    :type domain: String
    """

    logger.debug("Taking action project.create {}.".format(name))
    keystone = clients.get_keystone()
    project = keystone.projects.create(name, domain)
    context.update({'project_obj': project})
    context.setdefault('stack', []).append({'project_obj': project})


def delete(clients, context):
    """Delete an existing keystone project

    Uses context['project_obj']

    :param clients: Client Manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference object
    :type context: Dict
    """

    logger.debug("My context: {}".format(context))
    project = context['project_obj']
    context.pop('project_obj')

    logger.debug("Taking action project.delete {}.".format(project.name))
    keystone = clients.get_keystone()
    try:
        keystone.projects.delete(project)
    except KeystoneNotFound:
        pass


def list(clients, context, domain='Default'):
    """Create a new keystone project

    Sets context['project_obj']

    :param clients: Client Manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference object
    :type context: Dict
    :param domain: The domain in which to create the project
    :type domain: String
    """

    logger.debug("Taking action project.list.")
    keystone = clients.get_keystone()
    project = keystone.projects.list(domain)


def list_user(clients, context, domain='Default', user=None):
    """Create a new keystone project

    Sets context['project_obj']

    :param clients: Client Manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference object
    :type context: Dict
    :param domain: The domain in which to create the project
    :type domain: String
    """

    user = context['user_obj']
    logger.debug("Taking action project.list.")
    keystone = clients.get_keystone()
    project = keystone.projects.list(domain, user)