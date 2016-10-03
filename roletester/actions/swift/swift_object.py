"""Module containing actions to manage swift objects."""
from roletester.log import logging
from roletester.swift_error_decorator import swift_error
import copy

logger = logging.getLogger('roletester.actions.swift.swift_object')

@swift_error
def put(clients, context, obj_name="test_object", obj_contents=""):
    """Create an object in a container

    Uses context['container_name']
    Sets context['object_name']

    :param clients: Client Manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference object
    :type context: Dict
    :param obj_name: Name of the object to create.
    :type obj_name: String
    :param obj_contents: Contents of the object to create.
    :type obj_contents: String
    """
    container = context['container_name']

    logger.info("Taking action object.create {}.".format(obj_name))

    swift = clients.get_swift()
    swift.put_object(container, obj_name, obj_contents)

    context.update({"object_name": obj_name})
    context.setdefault('stack', []).append({
        'container_name': container,
        'object_name': obj_name
    })


@swift_error
def delete(clients, context):
    """Deletes an object from a container

    Uses context['container_name']
    Uses context['object_name']

    :param clients: Client Manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference object
    :type context: Dict
    """
    container = context['container_name']
    obj_name = context['object_name']

    logger.info("Taking action object.delete {}.".format(obj_name))

    swift = clients.get_swift()
    swift.delete_object(container, obj_name)


@swift_error
def get(clients, context):
    """Retrieves stats and lists objects in a container.

    Uses context['container_name']
    Uses context['object_name']

    :param clients: Client Manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference object
    :type context: Dict
    """
    container = context['container_name']
    obj_name = context['object_name']

    logger.info("Taking action object.get {}.".format(obj_name))

    swift = clients.get_swift()
    swift.head_object(container, obj_name)
    swift.get_object(container, obj_name)

@swift_error
def replace_metadata(clients, context,
                     metadata={"X-Object-Meta-Author": "JohnDoe"}):
    """Adds and deletes a metadata key/value pair on a container

    Uses context['container_name']
    Uses context['object_name']

    :param clients: Client Manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference object
    :type context: Dict
    :param metadata: Dict of metadata headers
    :type metadata: Dict
    """
    logger.info(
        "Taking action object.replace_metadata {}."
        .format(context['object_name'])
    )
    add_metadata(clients, context, metadata)
    delete_metadata(clients, context)

@swift_error
def add_metadata(clients, context,
                 metadata={"X-Object-Meta-Author": "JohnDoe"}):
    """Sets metadata on an an object in a container.

    Uses context['container_name']
    Uses context['object_name']
    Sets context['object_metadata']

    :param clients: Client Manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference object
    :type context: Dict
    :param metadata: Dict of metadata headers
    :type metadata: Dict
    """
    container = context['container_name']
    obj_name = context['object_name']
    context.update({"object_metadata": copy.deepcopy(metadata)})

    logger.info("Taking action object.add_metadata {}.".format(obj_name))

    swift = clients.get_swift()
    swift.post_object(container, obj_name, metadata)


@swift_error
def delete_metadata(clients, context):
    """Deletes metadata on an object in a container.

    Uses context['container_name']
    Uses context['object_name']
    Deletes context['object_metadata']

    :param clients: Client Manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference object
    :type context: Dict
    :param metadata: Dict of metadata headers
    :type metadata: Dict
    """
    container = context['container_name']
    obj_name = context['object_name']
    metadata = copy.deepcopy(context['object_metadata'])
    logger.info("Taking action object.delete_metadata {}.".format(obj_name))

    # Delete metadata by removing each key's value
    for key in metadata.keys():
        metadata[key] = ''

    swift = clients.get_swift()
    swift.post_object(container, obj_name, metadata)
    context.pop('object_metadata')
