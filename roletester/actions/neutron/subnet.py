"""Module containing action to create a nova server."""
from roletester.log import logging

logger = logging.getLogger('roletester.actions.neutron.subnet')


def create(clients, context,
           name="test_subnet",
           ip_version=4,
           cidr="11.10.10.0/24"):
    """Create a subnet

    Uses context['network_id']
    Sets context['subnet_id']

    :param clients: Client Manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference object
    :type context: Dict
    :param name: Name of the new subnet
    :type name: String
    :param ipversion: IPVersion of the subnet
    :type iperverion: String|Integer
    :param cidr: Cidr of the subnet
    :type cidr: String
    """
    network_id = context['network_id']
    logger.info("Taking action subnet.create {}.".format(name))
    neutron = clients.get_neutron()
    body = {
        "subnet": {
            "network_id": network_id,
            "name": name,
            "ip_version": ip_version,
            "cidr": cidr
        }
    }
    resp = neutron.create_subnet(body=body)
    subnet = resp['subnet']
    context['subnet_id'] = subnet['id']
    context.setdefault('stack', []).append({'subnet_id': subnet['id']})


def delete(clients, context):
    """Deletes a subnet.

    Uses context['subnet_id']

    :param clients: Client Manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference object
    :type context: Dict
    """
    subnet_id = context['subnet_id']
    logger.info("Taking action subnet.delete {}".format(subnet_id))
    neutron = clients.get_neutron()
    neutron.delete_subnet(subnet_id)
    context.pop('subnet_id')


def show(clients, context):
    """Shows info for a specific subnet.

    Uses context['subnet_id']
    Sets subnet['name']

    :param clients: Client Manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference object
    :type context: Dict
    """
    subnet_id = context['subnet_id']
    logger.info("Taking action subnet.show {}".format(subnet_id))
    neutron = clients.get_neutron()
    resp = neutron.show_subnet(subnet_id)
    subnet = resp['subnet']
    context['subnet_name'] = subnet['name']


def update(clients, context, name=None):
    """Update properties of a subnet.

    Uses context['subnet_id']

    :param clients: Client Manager
    :type clients: roletester.clients.ClientManager
    :param context: Pass by reference object
    :type context: Dict
    :param name: Optional new name of subnet
    :type name: String
    """
    subnet_id = context['subnet_id']
    logger.info("Taking action subnet.update {}.".format(subnet_id))
    neutron = clients.get_neutron()
    body = {'subnet': {}}
    if name is not None:
        body['subnet']['name'] = name
    neutron.update_subnet(subnet_id, body=body)
