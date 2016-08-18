import pprint
from roletester.log import logging

logger = logging.getLogger('roletester.scenario')


class ExpectedException(Exception):
    def __init__(self, expected_exceptions):
        msg = 'Was expecting one of {} to be raised and none were raised.' \
            .format(', '.join([str(e) for e in expected_exceptions]))
        super(ExpectedException, self).__init__(msg)


class Scenario(list):

    def chain(self, action, clients, *args, **kwargs):
        """Add an action to the list of actions in a scenario.

        :param action: Action to take
        :type action: Function
        :param clients: Client manager
        :type clients: roletester.clients.ClientManager
        :param context: Context of the scenario. An object that is passed by
            reference and altered throughout the scenario.
        :type context: Dict | None
        :param expected_exceptions: List of expected exceptions
        :type expected_exceptions: List
        """
        expected_exceptions = None
        if 'expected_exceptions' in kwargs:
            expected_exceptions = kwargs.pop('expected_exceptions')

        self.append(
            [action, clients, expected_exceptions, args, kwargs]
        )
        return self

    def run(self, context=None):
        """Run the scenario

        :param context: Object that will be passed by reference to
            each action in the scenario.
        :type context: Dict
        """
        context = context if context is not None else {}
        for action, clients, expected_exceptions, args, kwargs in self:
            try:
                action(clients, context, *args, **kwargs)
                if expected_exceptions:
                    raise ExpectedException(expected_exceptions)
            except Exception as e:
                matches = [isinstance(e, t) for t in expected_exceptions or []]
                if not any(matches):
                    logger.exception('Unexpected Exception!')
                    logger.debug("Type: {}".format(type(e)))
                    raise e
                logger.debug("Found expected exception {}".format(type(e)))
            logger.debug('Context: {}'.format(pprint.pprint(context)))


class ScenarioFactory(object):

    # This must be described in subclasses
    _ACTIONS = []
    _CLIENTS_INDEX = 1
    _ARGS_INDEX = 2
    _KWARGS_INDEX = 3

    def __init__(self, default_clients):
        """Init the factory

        :param default_clients: Default client manager to use for all actions
        :type default_clients: roletester.clients.ClientManager
        """
        # Build a list of tuples that can be modified before chaining into
        # a scenario
        self._links = []
        for action in self._ACTIONS:
            self._links.append([action, default_clients, [], {}])

    def set_clients(self, link_index, clients):
        """Set the client manager for a single action.

        :param link_index: Index of the action in the scenario
        "type link_index: Integer
        :param clients: New client manager for the action
        :type clients: roletester.clients.ClientManager
        :returns: Self for chaining
        :rtype: ScenarioFactory
        """
        self._links[link_index][self._CLIENTS_INDEX] = clients
        return self

    def set_args(self, link_index, args):
        """Set the args for a single action.

        :param link_index: Index of the action
        :type link_index: Integer
        :param args: List of args for action
        :type args: List|Tuple
        :returns: Self for chaining
        :rtype: ScenarioFactory
        """
        self._links[link_index][self._ARGS_INDEX] = args
        return self

    def set_kwargs(self, link_index, kwargs):
        """Set the kwargs for a single action

        :param link_index: Index of the action
        :type link_index: Integer
        :param kwargs: Keyword args for the action
        :type kwargs: Dict
        :returns: Self for chaining
        :rtype: ScenarioFactory
        """
        self._links[link_index][self._KWARGS_INDEX] = kwargs
        return self

    def set_expected_exceptions(self, link_index, expected_exceptions):
        """Set the expected exceptions for a single action.

        :param link_index: Index of the action
        :type link_index: Integer
        :param expected_exceptions: Expected exceptions
        :type expected_exceptions: List
        :returns: Self for chaining
        :rtype: ScenarioFactory
        """
        self._links[link_index][self._KWARGS_INDEX].update({
            'expected_exceptions': expected_exceptions
        })

    def set(self,
            link_index,
            clients=None,
            args=None,
            kwargs=None,
            expected_exceptions=None):
        """Set all attributes of an action or None

        :param link_index: Index of the action
        :type link_index: Integer
        :param clients: Client manager for action
        :type clients: roletester.clients.ClientManager
        :param args: Args for the action
        :type args: None|List|Tuple
        :param kwargs: Keyword args for the action
        :type args: None|Dict
        :param expected_exceptions: List of expected exceptions
        :type expected_exceptions: None|List
        :returns: Self for chaining
        :rtype: ScenarioFactory
        """
        if clients is not None:
            self.set_clients(link_index, clients)

        if args is not None:
            self.set_args(link_index, args)

        if kwargs is not None:
            self.set_kwargs(link_index, kwargs)

        if expected_exceptions is not None:
            self.set_expected_exceptions(link_index, expected_exceptions)

        return self

    def produce(self):
        """Creates the scenario from links.

        :returns: Scenario
        :rtype: Scenario
        """
        scenario = Scenario()
        for link in self._links:
            action, clients, args, kwargs = link
            scenario.chain(action, clients, *args, **kwargs)
        return scenario
