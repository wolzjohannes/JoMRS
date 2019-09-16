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
        self.rig_operators = test_operators.TestOperators()
        self.set_up = self.rig_operators.setUp()
        self.build_main = build.main()

    def test_build_rig_data(self):
        self.build_steps = self.build_main.steps()