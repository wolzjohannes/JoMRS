"""
JoMRS operator unittest module
"""
import operators
import pymel.core as pmc
import pymel.core.datatypes as datatypes
from tests.mayaunittest import TestCase

reload(operators)


class TestOperators(TestCase):
    """
    Test the operators module.
    """

    def setUp(self):
        """
        Setup variables for all other tests.
        """
        self.test_op_0 = operators.ComponentOperator()
        self.test_op_0.create_component_op_node(
            name="test", side="L", index=0, sub_operators_count=2
        )

        self.test_op_0.main_op_nd.translate.set(10, 5, 3)
        self.test_op_0.main_op_nd.rotate.set(100, 20.56, 342.11)

        self.test_op_1 = operators.ComponentOperator()
        self.test_op_1.create_component_op_node(
            name="test",
            side="L",
            index=1,
            sub_operators_count=3,
            parent=self.test_op_0.sub_operators[-1],
        )

        self.test_op_1.main_op_nd.translate.set(0, 0, 0)
        self.test_op_1.main_op_nd.rotate.set(0, 90, 0)

    def test_node_list(self):
        """
        Test if node_list are the same as all container nodes..
        """
        node_list_op_0 = self.test_op_0.get_node_list()
        node_list_op_1 = self.test_op_1.get_node_list()
        self.assertEqual(node_list_op_0, self.test_op_0.all_container_nodes)
        self.assertEqual(node_list_op_1, self.test_op_1.all_container_nodes)

    def test_world_position(self):
        """
        Test the world space position in translate and rotate.
        """
        ws_matrix_test_op_1 = datatypes.TransformationMatrix(
            self.test_op_1.main_op_nd.getMatrix(worldSpace=True)
        )
        test_ws_pos = datatypes.Vector(
            [27.820655082060398, -0.7524801847300928, -4.0237613976076]
        )
        test_ws_rotation = datatypes.EulerRotation(
            [1.934698909968065, -0.16331263127797427, 1.1967119606022243],
            unit="radians",
        )

        self.assertEqual(
            ws_matrix_test_op_1.getTranslation("world"),
            test_ws_pos,
            msg="{} has not the correct ws position. Maybe the position of "
            "the parent node is wrong".format(self.test_op_1),
        )

        self.assertEqual(ws_matrix_test_op_1.getRotation(), test_ws_rotation)

    def test_setters_and_getters(self):
        """
        Test all setter and getter methods.
        Mainly testing the meta data creation.
        """
        self.test_op_1.set_component_name("MUM")
        comp_name = self.test_op_1.get_component_name()
        self.assertEqual(comp_name, "MUM")
        self.test_op_1.set_component_side("L")
        comp_side = self.test_op_1.get_component_side()
        self.assertEqual(comp_side, "L")
        self.test_op_1.set_component_index(10)
        comp_index = self.test_op_1.get_component_index()
        self.assertEqual(comp_index, 10)
        self.test_op_1.set_component_type("single_control")
        comp_type = self.test_op_1.get_component_type()
        self.assertEqual(comp_type, "single_control")
        self.test_op_1.set_ik_spaces_ref(list(["world", "root", "chest"]))
        spaces = self.test_op_1.get_ik_spaces_ref().split(";")
        self.assertEqual(spaces, list(["world", "root", "chest"]))
        self.test_op_1.set_connect_nd(str(self.test_op_0.main_op_nd))
        connect_nd = self.test_op_1.get_connect_nd()
        self.assertEqual(connect_nd, str(self.test_op_0.main_op_nd))
        parent_node = self.test_op_1.get_parent_nd()
        self.assertEqual(parent_node, self.test_op_0.main_meta_nd)
        child_nodes = self.test_op_0.get_child_nd()
        self.assertEqual(child_nodes, list([self.test_op_1.main_meta_nd]))
