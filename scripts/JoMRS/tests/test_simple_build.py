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
# Date:       2021 / 02 / 18

"""
Test the build module with a very simple and basic example. We will use
simple test component which is only one control.
"""
import pymel.core as pmc
from tests.mayaunittest import TestCase
import components.test_single_control.create as test_sc_create
import build
import os
import constants


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
        Setup a simple operator hierarchy for a simple build.
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

    def test_rig_container_content(self):
        """
        Test the rig container content.
        """
        # The patterns for check the content dic.
        content_check_str_patterns = [
            "_BSHP_",
            "_COMPONENTS_",
            "_GEO_",
            "_RIG_",
            "_SHARED_ATTR_",
        ]
        pmc.select(clear=True)
        self.build_instance = build.MainBuild()
        self.build_instance.execute_building_steps()
        # Get the rig container in the scene based on the meta god nd.
        rig_container = self.build_instance.get_rig_containers_from_scene()[0]
        rig_container_instance = build.RigContainer(rig_container=rig_container)
        # Init to get the container content dic.
        rig_container_instance.get_container_content()
        # Check the container_content dic for the patterns.
        for pattern in content_check_str_patterns:
            container_content = rig_container_instance.get_container_content_by_string_pattern(
                pattern
            )
            self.assertIsNotNone(container_content)
            self.assertIn(pattern, container_content[0].name())

    def test_bnd_rig_container(self):
        """
        Check if the bind rig container has the correct jnts in it.
        """
        pmc.select(clear=True)
        self.build_instance = build.MainBuild()
        self.build_instance.execute_building_steps()
        # Get the rig container in the scene based on the meta god nd.
        rig_container = self.build_instance.get_rig_containers_from_scene()[0]
        rig_container_instance = build.RigContainer(rig_container=rig_container)
        rig_container_instance.get_container_content()
        bnd_rig_container = rig_container_instance.get_container_content_by_string_pattern(
            "_RIG_"
        )[
            1
        ]
        bnd_rig_container_content = bnd_rig_container.getNodeList()
        self.assertIsNotNone(bnd_rig_container_content)
        for jnt in bnd_rig_container_content:
            self.assertEquals(jnt.nodeType(), "joint")
            self.assertIn("_BND_", jnt.name())
        # Merge all joint names into one single string for a easier checkup.
        bnd_rig_container_content_string = "_".join(
            [jnt.name() for jnt in bnd_rig_container_content]
        )
        self.assertIn(
            "_{}_".format(self.CONTROL_NAME), bnd_rig_container_content_string
        )
        self.assertIn(
            "_{}_".format(self.CONTROL_NAME_1), bnd_rig_container_content_string
        )

    def test_component_container_content(self):
        """
        Test if the components container of the rig container has the
        correct content count.
        """
        pmc.select(clear=True)
        self.build_instance = build.MainBuild()
        self.build_instance.execute_building_steps()
        # Get the rig container in the scene based on the meta god nd.
        rig_container = self.build_instance.get_rig_containers_from_scene()[0]
        rig_container_instance = build.RigContainer(rig_container=rig_container)
        rig_container_instance.get_container_content()
        component_container = rig_container_instance.get_container_content_by_string_pattern(
            "_COMPONENTS_"
        )[
            0
        ]
        components = component_container.getNodeList()
        self.assertEqual(len(components), 2)

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
        # Test the rig names
        rig_containers = self.build_instance.get_rig_containers_from_scene()
        self.assertIn(self.RIG_NAME, rig_containers[0].name())
        self.assertIn(self.RIG_NAME_1, rig_containers[1].name())
        self.assertIn(self.RIG_NAME_2, rig_containers[2].name())

    def test_build_rig_from_json_file(self):
        """
        Test for building a rig with a json file.
        """
        file_path = os.path.normpath(
            "{}/temp/test_rig_build.json".format(constants.BUILD_JSON_PATH)
        )
        pmc.newFile(force=True)
        self.build_instance = build.MainBuild()
        self.build_instance.build_from_json_file(file_path)
