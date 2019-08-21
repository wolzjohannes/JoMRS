import operators
import pymel.core as pmc
from tests.mayaunittest import TestCase


class TestOperators(TestCase):
    def setUp(self):
        spine_op_instance = operators.create_component_operator()
        self.spine_op = spine_op_instance.build_node(
            operator_name="spine", side="M"
        )
        self.spine_main_op = (
            self.spine_op.root_op_meta_nd.get()
            .main_meta_nd_0.get()
            .main_operator_nd.get()
        )
        self.spine_sub_op = (
            self.spine_main_op.main_op_meta_nd.get()
            .sub_meta_nd_0.get()
            .sub_operator_nd.get()
        )
        self.spine_main_op.rotateZ.set(90)
        self.spine_main_op.translateY.set(15)
        pmc.select(self.spine_sub_op)
        clavicle_op_instance = operators.create_component_operator()
        self.clavicle_op = clavicle_op_instance.build_node(
            operator_name="clavicle", side="L"
        )
        self.clavicle_main_op = (
            self.clavicle_op.root_op_meta_nd.get()
            .main_meta_nd_1.get()
            .main_operator_nd.get()
        )
        self.clavicle_sub_op = (
            self.clavicle_main_op.main_op_meta_nd.get()
            .sub_meta_nd_0.get()
            .sub_operator_nd.get()
        )
        pmc.select(clear=True)
        self.clavicle_main_op.rotateZ.set(-90)
        self.clavicle_main_op.translateY.set(-2)
        pmc.select(self.clavicle_sub_op)
        l_arm_op_instance = operators.create_component_operator()
        self.arm_op = l_arm_op_instance.build_node(
            operator_name="arm", side="L", sub_operators_count=2
        )
        self.arm_main_op = (
            self.arm_op.root_op_meta_nd.get()
            .main_meta_nd_2.get()
            .main_operator_nd.get()
        )
        self.arm_sub_op_0 = (
            self.arm_main_op.main_op_meta_nd.get()
            .sub_meta_nd_0.get()
            .sub_operator_nd.get()
        )
        self.arm_sub_op_1 = (
            self.arm_main_op.main_op_meta_nd.get()
            .sub_meta_nd_1.get()
            .sub_operator_nd.get()
        )
        self.arm_main_op.rotateZ.set(-45)
        pmc.select(clear=True)

    def test_spine_operator_object(self):
        world_space = self.spine_main_op.world
        self.assertEqual(
            self.spine_main_op, pmc.PyNode("M_MAIN_op_spine_0_CON")
        )
