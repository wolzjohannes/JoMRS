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
# Date:       2021 / 03 / 01

"""
Test the global_component.
"""
import pymel.core as pmc
import pymel.core.datatypes as dt
from tests.mayaunittest import TestCase
from components.main import selected
import components.global_component.create as gl_comp
import constants


class TestGlobalComponent(TestCase):
    """
    Test global_component.
    """

    def setUp(self):
        """
        Test the single control rig component.
        """
        self.gl_comp_0 = gl_comp.MainCreate()
        self.gl_comp_0._init_operator()
        self.gl_comp_0.set_rig_name("test")
        self.gl_comp_0.main_op_nd.scale.set(5, 5, 5)
        self.gl_comp_0.main_op_nd.translate.set(-4, 20, -20)
        self.gl_comp_0.main_op_nd.rotate.set(-60, 70, -47)
        self.gl_comp_0.sub_operators[0].translate.set(1, 11, -6)
        pmc.select(self.gl_comp_0.sub_operators[0])
        self.selection = selected()
        # For hard testing i create a second component and parent it under
        # the first one. This component is not designed for that purposes but
        # this abstraction is good for testing.
        self.gl_comp_1 = gl_comp.MainCreate(
            1, self.selection, self.selection, self.selection
        )
        self.gl_comp_1._init_operator(parent=self.selection)
        self.gl_comp_1.main_op_nd.scale.set(5, 5, 5)
        self.gl_comp_1.main_op_nd.translate.set(32, 20, -20)
        self.gl_comp_1.main_op_nd.rotate.set(-60, 70, -47)
        self.gl_comp_1.sub_operators[0].translate.set(1, 11, -6)

    def test_build_from_operator(self):
        """
        Isolated component build testing.
        """
        self.gl_comp_0.build_from_operator()
        self.gl_comp_1.build_from_operator()

    def test_bnd_joint_creation_disabled(self):
        """
        Test the bnd creation for one component. So we check if it works
        separately.
        """
        self.gl_comp_1.set_bnd_joint_creation(True)
        self.gl_comp_0.build_from_operator()
        self.gl_comp_1.build_from_operator()
        output_nd_0 = self.gl_comp_0.component_root.get_container_content_by_string_pattern(
            "output"
        )[
            0
        ]
        self.assertFalse(
            output_nd_0.attr(constants.BND_OUTPUT_WS_PORT_NAME).connections()
        )
        self.assertFalse(self.gl_comp_0.component_root.get_bnd_root_nd())
        output_nd_1 = self.gl_comp_1.component_root.get_container_content_by_string_pattern(
            "output"
        )[
            0
        ]
        self.assertTrue(
            output_nd_1.attr(constants.BND_OUTPUT_WS_PORT_NAME).connections()
        )
        self.assertTrue(self.gl_comp_1.component_root.get_bnd_root_nd())

    def test_control_curve_worldspace_orientation(self):
        """
        Test if the control curve in orientated in worldspace zero.
        """
        self.gl_comp_1.set_worldspace_orientation(False)
        self.gl_comp_0.build_from_operator()
        self.gl_comp_1.build_from_operator()
        global_control_curve_0 = self.gl_comp_0.global_control_curve[1]
        global_control_curve_1 = self.gl_comp_1.global_control_curve[1]
        gl_comp_0_ws_matrix = global_control_curve_0.getMatrix(worldSpace=True)
        gl_comp_1_ws_matrix = global_control_curve_1.getMatrix(worldSpace=True)
        self.assertEqual(
            gl_comp_0_ws_matrix.rotate, dt.Quaternion([0.0, 0.0, 0.0, 1.0])
        )
        self.assertNotEqual(
            gl_comp_1_ws_matrix.rotate, dt.Quaternion([0.0, 0.0, 0.0, 1.0])
        )

    def test_callback_attributes(self):
        """
        Test the change pivot callback.
        """
        self.gl_comp_0.build_from_operator()
        self.gl_comp_1.build_from_operator()
        self.gl_comp_0.change_pivot_control_curve[1].attr(
            self.gl_comp_0.CHANGE_PIVOT_ATTR
        ).set(1)
        self.gl_comp_0.change_pivot_control_curve[1].attr(
            self.gl_comp_0.CHANGE_PIVOT_ATTR
        ).set(0)
        self.gl_comp_1.change_pivot_control_curve[1].attr(
            self.gl_comp_1.CHANGE_PIVOT_ATTR
        ).set(1)
        self.gl_comp_1.change_pivot_control_curve[1].attr(
            self.gl_comp_1.CHANGE_PIVOT_ATTR
        ).set(0)
        self.gl_comp_0.change_pivot_control_curve[1].attr(
            self.gl_comp_0.RESET_PIVOT_ATTR
        ).set(1)
        self.gl_comp_0.change_pivot_control_curve[1].attr(
            self.gl_comp_0.RESET_PIVOT_ATTR
        ).set(0)
        self.gl_comp_1.change_pivot_control_curve[1].attr(
            self.gl_comp_1.RESET_PIVOT_ATTR
        ).set(1)
        self.gl_comp_1.change_pivot_control_curve[1].attr(
            self.gl_comp_1.RESET_PIVOT_ATTR
        ).set(0)
