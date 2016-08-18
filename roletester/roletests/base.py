import unittest
from roletester.garbage import Collector as GC
from roletester.keystone_manager import KeystoneManager as KM
from roletester.log import logging

logger = logging.getLogger('roletester.base')


class Base(unittest.TestCase):
    """Base test class.

    Actual role test classes should subclass this this test class.
    """

    def setUp(self):
        """Called before each test method."""

        # Pass this context to scenraio.run()
        self.context = {}

        # Keystone manage - use this for test credentials
        self.km = KM()

        # Set up the garbage collector
        # admin = self.km.find_user_credentials('Default', 'admin', 'admin')
        print "Garbage user:"
        admin = self.km.find_user_credentials('Default', 'Default', 'cloud-admin')
        self.gc = GC(admin)

    def tearDown(self):
        """Called after each test method."""
        try:
            self.gc.collect(self.context)
        except Exception:
            logger.exception("Exception when garbage collecting")
        finally:
            self.km.teardown()
