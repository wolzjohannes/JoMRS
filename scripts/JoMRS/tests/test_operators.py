"""
JoMRS operator unittest module
"""
import operators
import pymel.core as pmc
from tests.mayaunittest import TestCase


class TestOperators(TestCase):
    """
    Test the operators module.
    """

    def setUp(self):
        """
        Setup variables for all other tests.
        """
        test_op_0 = operators.ComponentOperator()
        test_op_0.create_component_op_node(
            name="test", side="L", index=0, sub_operators_count=3
        )

        test_op_0.main_op_nd.translate.set(10, 5, 3)
        test_op_0.main_op_nd.rotate.set(100, 20.56, 342.11)

        test_op_1 = operators.ComponentOperator(
            main_operator_node=test_op_0.main_op_nd
        )
        test_op_1.create_component_op_node(
            name="test", side="L", index=1, sub_operators_count=3
        )

        test_op_1.main_op_nd.translate.set(20, 35, -20)
        test_op_1.main_op_nd.rotate.set(110, 200, -20.89)

    def test_spine_operator(self):
        """
        Test the spine operator.
        """
        world_space = self.spine_main_op.getTranslation(space="world")
        self.assertEqual(world_space, dt.Vector([0.0, 15.0, 0.0]))
        self.assertEqual(self.spine_main_meta_nd.component_name.get(), "spine")
        self.assertEqual(
            self.spine_main_meta_nd.component_type.get(), "spine_component"
        )
        self.assertEqual(self.spine_main_meta_nd.component_side.get(), "M")
        self.assertEqual(
            self.spine_main_op, pmc.PyNode("M_MAIN_op_spine_0_CON")
        )
        self.assertEqual(
            self.spine_sub_op.main_operator_nd.get(),
            pmc.PyNode("M_MAIN_op_spine_0_CON"),
        )

    def test_clavicle_operator(self):
        """
        Test the clavicle operator.
        """
        world_space = self.clavicle_main_op.getTranslation(space="world")
        self.assertEqual(world_space, dt.Vector([2.000000000000002, 25.0, 0.0]))
        object_space = self.clavicle_main_op.getTranslation(space="object")
        self.assertEqual(object_space, dt.Vector([0.0, -2.0, 0.0]))
        self.assertEqual(
            self.clavicle_main_op, pmc.PyNode("L_MAIN_op_clavicle_0_CON")
        )
        self.assertEqual(
            self.clavicle_main_op.main_op_meta_nd.get(),
            self.clavicle_main_meta_nd,
        )
        self.assertEqual(
            self.clavicle_main_op.getParent(generations=2), self.spine_sub_op
        )

    def test_god_meta_nd(self):
        """
        Test scene god node.
        """
        self.assertTrue(pmc.PyNode("god_meta_0_METAND"))
        meta_nodes = []
        for x in range(8):
            meta_nodes.append(
                pmc.PyNode("god_meta_0_METAND")
                .attr("meta_nd_{}".format(str(x)))
                .get()
            )
        self.assertIs(len(meta_nodes), 8)
