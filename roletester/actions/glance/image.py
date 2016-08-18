import time
import os
from roletester.exc import GlanceNotFound
from roletester.log import logging

logger = logging.getLogger('roletester.actions.glance.image')


def create(clients,
           context,
           image_file,
           visibility='private',
           name="glance test image",
           disk_format='qcow2',
           container_format='bare'):
    """Creates a glance image.

    Uses context['image_id']

    :param clients: Client manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference context object.
    :type context: Dict
    :param image_file: File path to image file you are uploading
    :type image_file: String
    :param visibility: Sets image availability. public | private
    :type visibility: Boolean
    :param name: Image name
    :type name: String
    :param disk_format: Glance disk file format
    :type disk_format: String
    :param container_format: Image container format
    :type container_format: String
    """
    logger.debug("Taking action image_create")

    kwargs = {
        'name': name,
        'disk_format': disk_format,
        'container_format': container_format,
        'visibility': visibility
    }
    glance = clients.get_glance()
    image = glance.images.create(**kwargs)
    context.update(image_id=image.id)
    context.setdefault('stack', []).append({'image_id': image.id})

    glance.images.upload(image.id, open(image_file, 'rb'))
    logger.debug("Created image {0}".format(image.name))


def delete(clients, context, image_key=None):
    """Deletes an image from Glance.

    Uses context['image_id']

    :param clients: Client manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference context object.
    :type context: Dict
    :param image_key: key name in context to delete (like server_image_id)
    :type image_id: String
    """
    def delete_image(id):
        """*Actually* deletes an image from Glance.

        Because delete controls for any image made by other services
        are handled by glance, we need a way to cleanup any image. Excluding
        the external_id param will default to context['image_id']

        :param id: Image id to be deleted
        :type id: String
        """
        glance = clients.get_glance()
        image = glance.images.get(id)
        logger.debug("Deleting image %s" % image.id)
        glance.images.delete(image.id)
        logger.debug("Deleted image %s" % image.id)
    if image_key is None:
        image_id = context['image_id']
    else:
        image_id = context[image_key]
    delete_image(image_id)
    logger.debug(context)


def show(clients, context, image_key='image_id', context_key='image_status'):
    """Shows a glance image.

    Uses context['image_id'] or other specified with image_key
    Sets context['image_status'] or other specified with context_key

    :param clients: Client manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference context object.
    :type context: Dict
    :param image_key: Explicit image id to show
    :type image_key: String
    :param context_key: Context key to set. Useful for volume, server images
    :type context_key: String
    """

    image_id = context[image_key]
    logger.debug("Showing image %s" % image_id)
    image = clients.get_glance().images.get(image_id)
    logger.debug(
        'Image info "%s": name: "%s" status: "%s"' %
        (image.id, image.name, image.status)
    )
    context[context_key] = image.status.lower()


def download(clients, context, image_key='image_id', context_key='image_status'):
    """downloads a glance image.

    Uses context['image_id'] or other specified with image_key
    Sets context['image_status'] or other specified with context_key

    :param clients: Client manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference context object.
    :type context: Dict
    :param image_key: Explicit image id to show
    :type image_key: String
    :param context_key: Context key to set. Useful for volume, server images
    :type context_key: String
    """

    image_id = context[image_key]
    logger.debug("Showing image %s" % image_id)
    image = clients.get_glance().images.data(image_id)
    logger.debug(
        'Downloading image "%s"' % image_id
    )
    save_image(image, image_id)


def save_image(data, path):
    """Save an image to the specified path.
    :param data: binary data of the image
    :param path: path to save the image to
    """
    image = open(path, 'wb')
    try:
        for chunk in data:
            image.write(chunk)
    finally:
        if path is not None:
            image.close()


def list(clients, context):
    """Lists glance images

    :param clients: Client manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference context object.
    :type context: Dict
    """
    glance = clients.get_glance()
    logger.debug("Listing all images.")
    # It's a generator
    images = [x.name for x in glance.images.list()]
    log_template = "Images listing: " + ', '.join(["\"%s\""] * len(images))
    logger.debug(log_template % tuple(images))


def update(clients, context):
    """Updates glance metadata

     Uses context['image_id']

    :param clients: Client manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference context object.
    :type context: Dict
    """
    glance = clients.get_glance()
    image_id = context['image_id']
    glance.images.update(image_id, metadata='updated')
    logger.debug("Updated metadata for image %s" % image_id)


# Statuses that indicate a terminating status
_DONE_STATUS = set(['active', 'killed', 'deleted'])


def wait_for_status(admin_clients,
                    context,
                    image_key=None,
                    timeout=60,
                    interval=5,
                    initial_wait=None,
                    target_status='active'):
    """Waits for a image to go to a request status.

    Uses context['image_id']
    Uses context['image_status']

    :param admin_clients: Client manager
    :type admin_clients: roletester.clients.ClientManager
    :param context: Pass by reference context object.
    :type context: Dict
    :param image_key: context[key] to find image_id
    :type image_key: String
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
    logger.debug("Taking action wait for image")

    if initial_wait:
        time.sleep(initial_wait)

    start = time.time()
    kwargs = {}
    image_status = 'image_status'
    if image_key is not None:
        image_status = '_'.join([image_key, 'status'])
        kwargs = {
            'image_key': image_key,
            'context_key': image_status
        }
    try:
        while (time.time() - start < timeout):
            show(admin_clients, context, **kwargs)
            status = context[image_status]
            logger.debug("Found status {}".format(status))
            if status == target_status:
                context.pop(image_status)
                break
            if status in _DONE_STATUS:
                raise Exception(
                    "Was looking for status {} but found {}"
                    .format(target_status, status)
                )
            time.sleep(interval)
    except GlanceNotFound:
        if target_status != 'deleted':
            raise
