"""
JoMRS build unittest module
"""
import build
import pymel.core as pmc
import test_operators
from tests.mayaunittest import TestCase


class TestBuild(TestCase):
    """
    Test the build module.
    """

    def setUp(self):
        """
        Setup variables for all other tests.
        """
        self.rig_operators = test_operators.TestOperators
        self.set_up = self.rig_operators.setUp
        self.build_main = build.Main()

    def test_build_rig_data(self):
        self.assertIsNotNone(self.build_main.root_op_meta_nd)
        self.overall_rig_data = self.build_main.get_overall_rig_data
        self.assertIsNotNone(self.overall_rig_data)