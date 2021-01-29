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
# Date:       2021 / 01 / 23

"""
Test the build module with a very simple and basic example. We will use
simple test component which is only one control.
"""
import pymel.core as pmc
import pymel.core.datatypes as datatypes
from tests.mayaunittest import TestCase
import components.test_single_control.create as test_sc_create
import build


class TestSimpleBuild(TestCase):
    """
    Test the operators module.
    """

    RIG_NAME = "MOM"
    RIG_NAME_1 = "DAD"
    RIG_NAME_2 = "AUNT"
    CONTROL_NAME = "MOM"
    CONTROL_NAME_1 = "Test"
    CONTROL_NAME_2 = "DAD"
    CONTROL_NAME_3 = "CHILD"
    CONTROL_NAME_4 = "AUNT"
    CONTROL_NAME_5 = "UNCLE"

    def setUp(self):
        """
        Setup variables for all other tests.
        """
        self.test_single_control = test_sc_create.MainCreate(
            self.CONTROL_NAME, "M", 0
        )
        self.test_single_control._init_operator()
        self.test_single_control.set_control_shape("sphere")
        self.test_single_control.set_rig_name(self.RIG_NAME)
        self.test_single_control.main_op_nd.translate.set(2, 10, 0)

        self.test_single_control_1 = test_sc_create.MainCreate(
            self.CONTROL_NAME_1, "L", 1
        )
        self.test_single_control_1._init_operator(
            parent=self.test_single_control.main_op_nd
        )
        self.test_single_control_1.set_control_shape("pyramide")
        self.test_single_control_1.main_op_nd.translate.set(
            13.124, 13.397, -9.37
        )
        self.test_single_control_1.main_op_nd.rotate.set(
            111.821, 56.184, 84.856
        )
        self.test_single_control_2 = None
        self.test_single_control_3 = None
        self.test_single_control_4 = None
        self.test_single_control_5 = None
        self.build_instance = None

    def test_build_execute_from_scene(self):
        """
        Test if the build execute correctly if nothing is selected.
        """
        pmc.select(clear=True)
        self.build_instance = build.MainBuild()
        self.build_instance.execute_building_steps()

    def test_build_execute_from_selected_operators_root_nd(self):
        """
        Test if the build execute correctly if you select a operators root node.
        """
        pmc.select(self.test_single_control.op_root_nd)
        self.build_instance = build.MainBuild()
        self.build_instance.execute_building_steps()

    def test_build_execute_from_selected_main_op_nd(self):
        """
        Test if the build execute correctly if you select a main op node.
        """
        pmc.select(self.test_single_control.main_op_nd)
        self.build_instance = build.MainBuild()
        self.build_instance.execute_building_steps()

    # def test_rig_container_content(self):
    #     """
    #     Test the rig container content.
    #     """
    #     component_root = self.test_single_control.component_root
    #     component_root.get_container_content()
    #     container_content = component_root.container_content
    #     self.assertIsNotNone(container_content.get('M_BSHP_0_GRP'))
    #     self.assertIsNotNone(container_content.get('M_COMPONENTS_0_GRP'))
    #     self.assertIsNotNone(container_content.get('M_GEO_0_GRP'))
    #     self.assertIsNotNone(container_content.get('M_RIG_0_GRP'))
    #     self.assertIsNotNone(container_content.get('M_SHARED_ATTR_0_GRP'))


    # def bind_rig_container(self):
    #     pass

    def test_build_with_multiple_operators_root_nd(self):
        """
        Test if the build succeed if we have multiple operators root nd in the
        scene.
        """
        # second root_op_nd
        pmc.select(clear=True)
        self.test_single_control_2 = test_sc_create.MainCreate(
            self.CONTROL_NAME_2, "M", 0
        )
        self.test_single_control_2._init_operator()
        self.test_single_control_2.set_control_shape("sphere")
        self.test_single_control_2.set_rig_name(self.RIG_NAME_1)
        self.test_single_control_2.main_op_nd.translate.set(10, 20, 0)

        self.test_single_control_3 = test_sc_create.MainCreate(
            self.CONTROL_NAME_3, "L", 1
        )
        self.test_single_control_3._init_operator(
            parent=self.test_single_control_2.main_op_nd
        )
        self.test_single_control_3.set_control_shape("pyramide")
        self.test_single_control_3.main_op_nd.translate.set(14, 100, 40)
        self.test_single_control_3.main_op_nd.rotate.set(30, 60, 80)
        # third root_op_nd
        pmc.select(clear=True)
        self.test_single_control_4 = test_sc_create.MainCreate(
            self.CONTROL_NAME_4, "M", 0
        )
        self.test_single_control_4._init_operator()
        self.test_single_control_4.set_control_shape("box")
        self.test_single_control_4.set_rig_name(self.RIG_NAME_2)
        self.test_single_control_4.main_op_nd.translate.set(10, 20, 0)
        self.test_single_control_5 = test_sc_create.MainCreate(
            self.CONTROL_NAME_5, "L", 1
        )
        self.test_single_control_5._init_operator(
            parent=self.test_single_control_4.main_op_nd
        )
        self.test_single_control_5.set_control_shape("pyramide")
        self.test_single_control_5.main_op_nd.translate.set(200, 10, 80)
        self.test_single_control_5.main_op_nd.rotate.set(60, 30, 100)
        pmc.select(clear=True)
        self.build_instance = build.MainBuild()
        self.build_instance.execute_building_steps()
        # # Test the rig names
        # print self.test_single_control.get_rig_name()
        # print self.test_single_control_2.get_rig_name()
        # print self.test_single_control_4.get_rig_name()
        # self.assertIn(self.test_single_control.get_rig_name(), self.RIG_NAME)
        # self.assertIn(self.test_single_control_2.get_rig_name(),
        #               self.RIG_NAME_1)
        # self.assertIn(self.test_single_control_4.get_rig_name(),
        #               self.RIG_NAME_2)