from log import logging

from exc import CinderNotFound
from exc import GlanceNotFound
from exc import KeystoneNotFound
from exc import NeutronNotFound
from exc import NovaNotFound
from exc import SwiftNotFoundException

from roletester.actions.cinder import volume_delete
from roletester.actions.cinder import volume_detach
from roletester.actions.cinder import volume_wait_for_status
from roletester.actions.glance import image_delete
from roletester.actions.keystone import project_delete
from roletester.actions.keystone import user_delete
from roletester.actions.neutron import floatingip_delete
from roletester.actions.neutron import network_delete
from roletester.actions.neutron import port_delete
from roletester.actions.neutron import router_delete
from roletester.actions.neutron import router_remove_interface
from roletester.actions.neutron import security_group_delete
from roletester.actions.neutron import security_group_rule_delete
from roletester.actions.neutron import subnet_delete
from roletester.actions.nova import server_delete
from roletester.actions.nova import server_wait_for_status
from roletester.actions.swift import swift_container_delete
from roletester.actions.swift import swift_object_delete

from scenario import Scenario

logger = logging.getLogger('roletester.garbage.Collector')


class Collector(object):

    def __init__(self, clients):
        """Init the collector with a set of admin clients.

        :param clients: Client manager. Should have admin privileges
        :type clients: roletester.clients.ClientManager
        """
        self._clients = clients
        self._delete_map = {
            'container_name': Scenario()
            .chain(swift_container_delete, clients),

            'floatingip_id': Scenario().chain(floatingip_delete, clients),
            'image_id': Scenario().chain(image_delete, clients),
            'object_name': Scenario().chain(swift_object_delete, clients),
            'network_id': Scenario().chain(network_delete, clients),
            'port_id': Scenario().chain(port_delete, clients),
            'router_id': Scenario().chain(router_delete, clients),

            'security_group_id': Scenario()
            .chain(security_group_delete, clients),

            'security_group_rule_id': Scenario()
            .chain(security_group_rule_delete, clients),

            'server_id': Scenario().chain(server_delete, clients)
            .chain(
                server_wait_for_status,
                clients,
                target_status='DELETED',
                initial_wait=5
            ),

            'subnet_id': Scenario().chain(subnet_delete, clients),

            'volume_id': Scenario()
            .chain(volume_wait_for_status, clients)
            .chain(volume_delete, clients),

            'volume_attachment_id': Scenario()
            .chain(volume_detach, clients),

            'project_obj': Scenario()
            .chain(project_delete, clients),

            'user_obj': Scenario()
            .chain(user_delete, clients),

            'router_subnet_mdx': Scenario()
            .chain(router_remove_interface, clients)
        }

    def delete(self, resource_dict):
        """Clean up a specific resource item.

        :param resource_dict: Dict containing the type_id and value
        :type resource_dict: Dict
        """
        for key, resource_id in resource_dict.items():
            scenario = self._delete_map.get(key)
            if not scenario:
                logger.warn(
                    'Unable to find scenario to clean {}:{}'
                    .format(key, resource_id)
                )
                continue
            try:
                scenario.run(context=resource_dict)
            except (CinderNotFound,
                    GlanceNotFound,
                    KeystoneNotFound,
                    NeutronNotFound,
                    NovaNotFound,
                    SwiftNotFoundException):
                logger.debug("{}:{} Was not found.".format(key, resource_id))
                pass
            except Exception:
                logger.exception(
                    "Error garbage collecting {}:{}"
                    .format(key, resource_id)
                )

    def collect(self, contexts):
        """Clean up any remaining resources.

        :param contexts: List of scenario contexts.
        :type contexts: List of Dicts
        """
        logger.debug("Beginning resource garbage collection.")
        if not isinstance(contexts, list):
            contexts = [contexts]

        for context in contexts:
            stack = context.get('stack', [])
            while stack:
                self.delete(stack.pop())
