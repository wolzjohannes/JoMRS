# Copyright (c) 2018 Johannes Wolz

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission
# notice shall be included in all.
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Author:     Johannes Wolz / Rigging TD
# Date:       2020 / 11 / 24

"""
JoMRS operator unittest module
"""
import operators
import pymel.core as pmc
import pymel.core.datatypes as datatypes
from tests.mayaunittest import TestCase
import re
import constants


class TestOperators(TestCase):
    """
    Test the operators module.
    """

    TEST_0_OP_SUB_COUNT = 2
    TEST_0_OP_NAME = "test"
    TEST_0_OP_INDEX = 0
    TEST_0_OP_SIDE = "L"

    TEST_1_OP_SUB_COUNT = 3
    TEST_1_OP_NAME = "TEST"
    TEST_1_OP_INDEX = 1
    TEST_1_OP_SIDE = "L"

    def setUp(self):
        """
        Setup variables for all other tests.
        """
        self.test_op_0 = operators.ComponentOperator()
        self.test_op_0.create_component_op_node(
            name=self.TEST_0_OP_NAME,
            side=self.TEST_0_OP_SIDE,
            index=self.TEST_0_OP_INDEX,
            sub_operators_count=self.TEST_0_OP_SUB_COUNT,
        )

        self.test_op_0.main_op_nd.translate.set(10, 5, 3)
        self.test_op_0.main_op_nd.rotate.set(100, 20.56, 342.11)

        self.test_op_1 = operators.ComponentOperator()
        self.test_op_1.create_component_op_node(
            name=self.TEST_1_OP_NAME,
            side=self.TEST_1_OP_SIDE,
            index=self.TEST_1_OP_INDEX,
            sub_operators_count=self.TEST_1_OP_SUB_COUNT,
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
            self.test_op_1.get_main_op_ws_matrix()
        )
        test_ws_vec = datatypes.Vector(
            [27.820655082060398, -0.7524801847300928, -4.0237613976076]
        )
        test_ws_rotation = datatypes.EulerRotation(
            [1.934698909968065, -0.16331263127797427, 1.1967119606022243],
            unit="radians",
        )

        ws_matrix_test_op_1_subs = [
            datatypes.TransformationMatrix(matrix)
            for matrix in self.test_op_1.get_sub_op_nodes_ws_matrix()
        ]

        ws_vec_test_op_1_subs = [
            ts_matrix.getTranslation("world")
            for ts_matrix in ws_matrix_test_op_1_subs
        ]

        test_ws_vec_subs = [
            datatypes.Vector(
                [31.42623634611877, 8.432088910758539, -2.397884932907285]
            ),
            datatypes.Vector(
                [35.03181761017714, 17.61665800624717, -0.7720084682069708]
            ),
            datatypes.Vector(
                [38.637398874235515, 26.801227101735805, 0.8538679964933436]
            ),
        ]

        self.assertEqual(ws_vec_test_op_1_subs, test_ws_vec_subs)

        self.assertEqual(
            ws_matrix_test_op_1.getTranslation("world"), test_ws_vec
        )

        self.assertEqual(ws_matrix_test_op_1.getRotation(), test_ws_rotation)

    def test_setters_and_getters(self):
        """
        Test all setter and getter methods.
        Mainly testing the meta data creation.
        """
        # Test name, side and index.
        self.assertEqual(
            self.test_op_0.get_component_name(), self.TEST_0_OP_NAME
        )
        self.assertEqual(
            self.test_op_1.get_component_name(), self.TEST_1_OP_NAME
        )
        self.assertEqual(
            self.test_op_0.get_component_index(), self.TEST_0_OP_INDEX
        )
        self.assertEqual(
            self.test_op_1.get_component_index(), self.TEST_1_OP_INDEX
        )
        self.test_op_1.set_component_name("MUM")
        comp_name = self.test_op_1.get_component_name()
        self.assertEqual(comp_name, "MUM")
        self.test_op_1.set_component_side("M")
        comp_side = self.test_op_1.get_component_side()
        self.assertEqual(comp_side, "M")
        self.test_op_1.set_component_index(10)
        comp_index = self.test_op_1.get_component_index()
        self.assertEqual(comp_index, 10)
        # Test Component type data.
        self.test_op_1.set_component_type("single_control")
        comp_type = self.test_op_1.get_component_type()
        self.assertEqual(comp_type, "single_control")
        # Test connection types
        self.assertFalse(self.test_op_1.set_connection_type('translate'))
        self.test_op_1.set_connection_type(['translate', 'rotate'])
        self.assertEqual(self.test_op_1.get_connection_types(), ['translate',
                                                                 'rotate'])
        # Test ik ref data.
        self.assertFalse(self.test_op_1.set_ik_spaces_ref('world'))
        self.test_op_1.set_ik_spaces_ref(list(["world", "root", "chest"]))
        spaces = self.test_op_1.get_ik_spaces_ref().split(";")
        self.assertEqual(spaces, list(["world", "root", "chest"]))
        # Test connect node data.
        self.test_op_1.set_connect_nd(str(self.test_op_0.main_op_nd))
        connect_nd = self.test_op_1.get_connect_nd()
        self.assertEqual(connect_nd, str(self.test_op_0.main_op_nd))
        parent_node = self.test_op_1.get_parent_nd()
        self.assertEqual(parent_node, self.test_op_0.main_meta_nd)
        # Test parent and child data.
        child_nodes = self.test_op_0.get_child_nd()
        self.assertEqual(child_nodes, list([self.test_op_1.main_meta_nd]))
        # Test if main_op_nd exist.
        main_op_nd = self.test_op_1.get_main_op_node_from_sub(
            self.test_op_1.sub_operators[-1]
        )
        self.assertEqual(self.test_op_1.main_op_nd, main_op_nd)
        # Test sup_operators.
        sub_operators = self.test_op_1.get_sub_op_nodes_from_main_op_nd()
        self.assertIs(len(sub_operators), self.TEST_1_OP_SUB_COUNT)
        self.assertEqual(sub_operators, self.test_op_1.sub_operators)
        # Test UUID
        uuid_string = self.test_op_1.get_uuid()
        uuid_string_search = self.test_op_1.root_meta_nd.attr(
            constants.UUID_ATTR_NAME).get()
        self.assertEqual(uuid_string_search, uuid_string)


    def test_naming_convention(self):
        """
        Test the naming convention of all container nodes.
        """
        index_regex = r"(\w_\d+_)"
        # Test the side in node names.
        for node in self.test_op_1.get_node_list():
            self.assertEqual(str(node)[0], self.TEST_1_OP_SIDE)
        self.test_op_1.change_operator_side("M")
        for node in self.test_op_1.get_node_list():
            self.assertEqual(str(node)[0], "M")
        self.assertEqual(self.test_op_1.get_component_side(), "M")
        # Test the index in nodes names
        for node in self.test_op_1.get_node_list():
            match = re.search(index_regex, str(node))
            instance = match.groups()[0]
            index = re.sub(r"[a-zA-Z]", "", instance)
            self.assertEqual(index, "_{}_".format(str(self.TEST_1_OP_INDEX)))
        self.test_op_1.change_operator_index(10)
        for node in self.test_op_1.get_node_list():
            match = re.search(index_regex, str(node))
            instance = match.groups()[0]
            index = re.sub(r"[a-zA-Z]", "", instance)
            self.assertEqual(index, "_10_")
        # Test operator name in nodes name.
        for node in self.test_op_1.get_node_list():
            match = re.search(self.TEST_1_OP_NAME, str(node))
            self.assertTrue(match)
        self.test_op_1.rename_operator_nodes("PeterParker")
        for node in self.test_op_1.get_node_list():
            match = re.search("PeterParker", str(node))
            self.assertTrue(match)

    def test_lra_node(self):
        """
        Test local rotation axes node.
        """
        # Test if aim constrain exist.
        self.assertIn(
            pmc.PyNode(
                "L_MAIN_op_{}"
                "_{}_LRA_CON_buffer_GRP_CONST".format(
                    self.TEST_1_OP_NAME, self.TEST_1_OP_INDEX
                )
            ),
            self.test_op_1.get_node_list(),
        )
        self.test_op_0.main_op_nd.rotate.set(0, 0, 0)
        sub_nodes = self.test_op_0.get_sub_op_nodes_from_main_op_nd()
        sub_nodes[0].translate.set(10, 3, -4)
        lra_buffer_local_rotation = (
            self.test_op_0.lra_node_buffer_grp.rotate.get()
        )
        lra_buffer_local_rotation = datatypes.Vector(
            [round(value, 4) for value in lra_buffer_local_rotation]
        )
        lra_buffer_test_rotation = datatypes.Vector([3.1108, 20.9634, 16.6992])
        self.assertEqual(lra_buffer_local_rotation, lra_buffer_test_rotation)
