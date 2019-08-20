import operators
import pymel.core as pmc
from tests.mayaunittest import TestCase


class TestOperators(TestCase):
    def setUp(self):
        op_instance = operators.create_component_operator()
        self.spine_op = op_instance.build_node(
            operator_name="spine", side="M"
        )
        self.spine_main_op =
            self.spine_op.root_op_meta_nd.get().main_meta_nd_0.get()
        self.spine_sub_op = self.spine_main_op.sub_meta_nd_0.get()
        self.spine_main_op.rotateZ.set(90)
        self.spine_main_op.translateY.set(15)
        pmc.select(self.spine_sub_op)
        self.clavicle_op = op_instance.build_node(
            operator_name="clavicle", side="L"
        )
        self.clavicle_main_op = (
            self.clavicle_op.root_op_meta_nd.get().main_meta_nd_1.get()
        )
        self.clavicle_sub_op = self.clavicle_main_op.sub_meta_nd_0.get()
        pmc.select(clear=True)
        self.clavicle_main_op.rotateZ.set(-90)
        self.clavicle_main_op.translateY.set(-2)

    def test_spine_operator_object(self):
        self.assertEqual(self.spine_main_op, pmc.PyNode('M_MAIN_op_spine_0_CON'))
