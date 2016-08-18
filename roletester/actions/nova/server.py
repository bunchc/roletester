import time
from roletester.exc import NovaNotFound
from roletester.log import logging

logger = logging.getLogger('roletester.actions.nova.server')


def create(clients,
           context,
           name='nova test instance',
           flavor=None,
           image=None):
    """Creates server with random image and flavor.

    Sets context['server_id']

    :param clients: Client manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference object
    :type context: Dict
    :param name: Server name
    :type name : String
    :param flavor: Flavor id
    :type flavor: Integer
    :param image: Image id
    :type image: String
    """
    nova = clients.get_nova()
    if flavor is None:
        flavor = nova.flavors.list()[0].id
    else:
        flavor = nova.flavors.get(flavor)
    if image is None:
        image = nova.images.get(context['image_id'])
    else:
        image = nova.images.get(image)
    logger.info(": %s" % image.id)
    logger.info("Taking action create")
    meta = {"test-key": "test-value"}
    nic = [{'net-id': context['network_id']}]

    #todo: add networks with kwargs
    server = nova.servers.create(name, image, flavor, meta=meta, nics=nic)
    context.update({'server_id': server.id})
    context.setdefault('stack', []).append({'server_id': server.id})
    logger.info("Created server {}".format(name))


def delete(clients, context):
    """Deletes a server.

    Uses context['server_id']

    :param clients: Client manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference object
    :type context: Dict
    """
    logger.info("Taking action delete")
    nova = clients.get_nova()
    server_id = context['server_id']
    logger.info("Deleting {0} ...".format(server_id))
    nova.servers.delete(server_id)


def update(clients, context, meta={"test-key": "modified-test-value"}):
    """Update's a server's metadata

    Uses context['server_id']

    :param clients: Client manager
    :type clients: roletester.clients.ClientManager
    :param meta: new metadata
    :type meta: Dict
    """
    nova = clients.get_nova()
    server = nova.servers.get(context['server_id'])
    logger.debug("Editing instance %s" % server.id)
    nova.servers.set_meta(server, meta)
    logger.debug("Instance %s edited." % server.id)


def list(clients, context):
    """Lists nova servers.

    :param clients: Client Manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by referece object
    :type context: Dict
    """
    logger.info("Listing active servers")
    nova = clients.get_nova()
    servers = nova.servers.list()
    for s in servers:
        logger.info("{0} - {1} - {2}".format(s.name, s.metadata, s.status))


def show(clients, context):
    """Shows a nova server.

    Uses context['server_id']
    Sets context['server_status']

    :param clients: Client manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference context object.
    :type context: Dict
    """
    logger.info("Taking action server.show")
    nova = clients.get_nova()
    server_id = context['server_id']
    server = nova.servers.get(server_id)
    context.update(server_status=server.status)


def create_image(clients, context, name='nova test image'):
    """Takes a snapshot of an image.

    Uses context['server_id']
    Sets context['server_image_id']

    :param clients: Client manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference context object.
    :type context: Dict
    """
    nova = clients.get_nova()
    server_id = context['server_id']
    server = nova.servers.get(server_id)
    meta = server.metadata
    logger.info("Creating image of instance %s" % server_id)
    image_id = server.create_image(name, meta)
    context.update(server_image_id=image_id)
    context.setdefault('stack', []).append({'image_id': image_id})
    logger.info("Created server image %s" % image_id)


# Statuses that indicate a terminating status
_DONE_STATUS = set(['ACTIVE', 'ERROR', 'DELETED'])


def wait_for_status(admin_clients,
                    context,
                    timeout=60,
                    interval=5,
                    initial_wait=None,
                    target_status='ACTIVE'):
    """Waits for a server to go to a request status.

    Uses context['server_id']
    Uses context['server_status']

    :param admin_clients: Client manager
    :type admin_clients: roletester.clients.ClientManager
    :param context: Pass by reference context object.
    :type context: Dict
    :param timeout: Timeout in seconds.
    :type timeout: Integer
    :param interval: Time in seconds to wait between polls.
    :type timeout: Integer
    :param initial_wait: Time in seconds to wait before beginning to poll.
        Useful for expecting a server that is ACTIVE to go to DELETED
    :type initial_wait: Integer
    :param target_status: Status to wait for. If desired status is DELETED,
        a NotFoundException will be allowed.
    :type target_status: String
    """
    logger.info("Taking action wait for server")

    if initial_wait:
        time.sleep(initial_wait)

    start = time.time()
    try:
        while (time.time() - start < timeout):
            show(admin_clients, context)
            status = context['server_status']
            logger.debug("Found status {}".format(status))
            if status == target_status:
                context.pop('server_status')
                break
            if status in _DONE_STATUS:
                raise Exception(
                    "Was looking for status {} but found {}"
                    .format(target_status, status)
                )
            time.sleep(interval)
    except NovaNotFound:
        if target_status != 'DELETED':
            raise
