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
# Date:       2021 / 02 / 20

"""
Test the single_control component.
"""
import pymel.core as pmc
import pymel.core.datatypes as dt
from tests.mayaunittest import TestCase
import components.single_control.create as sc_create
import constants


class TestSingleControlComponent(TestCase):
    """
    Test the operators module.
    """

    def setUp(self):
        """
        Test the single control rig component.
        """
        self.single_control = sc_create.MainCreate("MOM", "M", 0)
        self.single_control._init_operator()
        self.single_control.set_control_shape("quader")
        self.single_control.set_rig_name("single_control_test")
        self.single_control.set_component_side("L")
        self.single_control.main_op_nd.translateX.set(-2.212)
        self.single_control.main_op_nd.translateY.set(19.393)
        self.single_control.main_op_nd.translateZ.set(-8.492)
        self.single_control.main_op_nd.rotateX.set(2.312)
        self.single_control.main_op_nd.rotateY.set(27.491)
        self.single_control.main_op_nd.rotateZ.set(69.401)

    def test_bnd_joint_creation_disabled(self):
        """
        Test if if bind joint creation is off.
        """
        self.single_control.set_bnd_joint_creation(False)
        self.single_control.build_from_operator()
        output_nd = self.single_control.component_root.get_container_content_by_string_pattern(
            "output"
        )[
            0
        ]
        self.assertFalse(
            output_nd.attr(constants.BND_OUTPUT_WS_PORT_NAME).connections()
        )
        self.assertFalse(self.single_control.component_root.get_bnd_root_nd())

    def test_control_curve_worldspace_orientation(self):
        """
        Test if the control curve in orientated in worldspace zero.
        """
        self.single_control.set_worldspace_orientation(True)
        self.single_control.build_from_operator()
        control_curve = self.single_control.controls[0]
        ws_matrix = control_curve.getMatrix(worldSpace=True)
        tm_matrix = dt.TransformationMatrix(ws_matrix)
        self.assertEqual(
            tm_matrix.getRotation(),
            dt.EulerRotation([0.0, -0.0, 0.0], unit="radians"),
        )

    def test_lock_and_hide_transform_attributes(self):
        """
        Test if all transform attributes of the control curve are locked and
        hidden of the channelBox.
        """
        lock_attr_axes = ["X", "Y", "Z"]
        lock_attr_list = ["translate", "rotate", "scale"]
        for attr in lock_attr_list:
            for axe in lock_attr_axes:
                self.single_control.set_lock_and_hide_transform_attribute(
                    "{}{}".format(attr, axe), True
                )
        self.single_control.build_from_operator()
        control_curve = self.single_control.controls[0]
        for attr_ in lock_attr_list:
            for axe_ in lock_attr_axes:
                self.assertTrue(
                    control_curve.attr("{}{}".format(attr_, axe_)).isLocked()
                )
                self.assertFalse(
                    control_curve.attr(
                        "{}{}".format(attr_, axe_)
                    ).isInChannelBox()
                )
