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
# Date:       2021 / 03 / 28

"""
Test the fk_chain_component.
"""
import pymel.core.datatypes as dt
from tests.mayaunittest import TestCase
import components.fk_chain_component.create as fk_chain_comp


class TestFkChainComponent(TestCase):
    """
    Test fk_chain_component.
    """

    SUB_OPERATORS_COUNT = 3

    def setUp(self):
        """
        Test the single control rig component.
        """
        self.fk_chain_comp_0 = fk_chain_comp.MainCreate(
            name="Test",
            side="L",
            index=1,
            axes="X",
            sub_operators_count=self.SUB_OPERATORS_COUNT,
        )
        self.fk_chain_comp_0._init_operator()
        self.fk_chain_comp_0.main_op_nd.scale.set(10, 10, 10)
        self.fk_chain_comp_0.set_rig_name("testrig")
        self.fk_chain_comp_0.main_op_nd.translate.set(-60, 100, 70)
        self.fk_chain_comp_0.main_op_nd.rotate.set(4, 30, 6)

        self.fk_chain_comp_0.sub_operators[0].translate.set(9, 5, -4)
        self.fk_chain_comp_0.sub_operators[1].translate.set(6, -2, 6)
        self.fk_chain_comp_0.sub_operators[2].translate.set(2.5, -5, 6)

    def test_sub_lra_nodes(self):
        """
        Test if all sub operators has a lra node.
        """
        self.assertEqual(
            len(self.fk_chain_comp_0.sub_lra_nodes), self.SUB_OPERATORS_COUNT
        )

    def test_build_with_parent_aim(self):
        """
        Test the component build with parent aim option.
        """
        self.fk_chain_comp_0.set_parent_aim(True)
        self.fk_chain_comp_0.build_from_operator()
        for node in self.fk_chain_comp_0.sub_chain_controls:
            self.assertTrue(
                node.hasAttr(self.fk_chain_comp_0.parent_aim_attr_name)
            )

    def test_build_without_parent_aim(self):
        """
        Test the component build without the parent aim.
        """
        self.fk_chain_comp_0.build_from_operator()
        for node in self.fk_chain_comp_0.sub_chain_controls:
            self.assertFalse(
                node.hasAttr(self.fk_chain_comp_0.parent_aim_attr_name)
            )

    def test_end_control_orientation(self):
        """
        Test end control orientation.
        """
        self.fk_chain_comp_0.build_from_operator()
        sub_chain_control_rotation_0 = dt.TransformationMatrix(
            self.fk_chain_comp_0.sub_chain_controls[-1].getMatrix(
                worldSpace=True
            )
        ).getRotation()
        sub_chain_control_rotation_1 = dt.TransformationMatrix(
            self.fk_chain_comp_0.sub_chain_controls[-2].getMatrix(
                worldSpace=True
            )
        ).getRotation()
        for x in range(3):
            self.assertAlmostEqual(
                sub_chain_control_rotation_0[x], sub_chain_control_rotation_1[x]
            )
