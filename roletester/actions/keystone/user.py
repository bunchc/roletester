"""Module containing actions to manage keystone users."""
from roletester.log import logging
from roletester.exc import KeystoneNotFound

logger = logging.getLogger('roletester.actions.keystone.user')


def create(clients, context, name="test_user", password="test_pass", domain="Default"):
    """Create a new keystone user

    Sets context['user_obj']

    :param clients: Client Manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference object
    :type context: Dict
    :param name: Name for the new user.
    :type name: String
    :param domain: Domain id for the new user
    :type domain: String
    :param password: Password for the new user
    :type password: String
    """

    logger.debug("Taking action user.create {}.".format(name))
    keystone = clients.get_keystone()
    user = keystone.users.create(name, domain=domain, password=password)
    context.update({'user_obj': user})
    context.setdefault('stack', []).append({'user_obj': user})


def delete(clients, context):
    """Delete an existing keystone user

    Uses context['user_obj']

    :param clients: Client Manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference object
    :type context: Dict
    """

    user = context['user_obj']

    logger.debug("Taking action user.delete {}.".format(user.name))
    keystone = clients.get_keystone()
    try:
        keystone.users.delete(user)
    except KeystoneNotFound:
        pass


def change_name(clients, context, new_name="new_test_user"):
    """Changes the name of an existing keystone user

    Uses context['user_obj']

    :param clients: Client Manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference object
    :type context: Dict
    :param new_name: New name for user
    :type new_name: String
    """

    user = context['user_obj']

    logger.debug("Taking action user.change_name {}.".format(user.name))
    keystone = clients.get_keystone()
    keystone.users.update(user, name=new_name)

