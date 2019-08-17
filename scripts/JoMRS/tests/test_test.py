import operators
from tests.mayaunittest import TestCase

class TestExample(TestCase):

    def test_create_main_op(self):
        op = operators.create_component_operator()
        print op
