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

    def setUp(self):
        """
        Setup variables for all other tests.
        """
        self.test_single_control = test_sc_create.MainCreate("MOM", "M", 0)
        self.test_single_control._init_operator()
        self.test_single_control.set_control_shape("sphere")
        self.test_single_control.set_rig_name("MOM")
        self.test_single_control.main_op_nd.translate.set(2, 10, 0)

        self.test_single_control_1 = test_sc_create.MainCreate("Test", "L", 1)
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
        self.build_instance = None

    def test_build_execute_from_scene(self):
        """
        Test if the build execute correctly if nothing is selected.
        """
        pmc.select(clear=True)
        self.build_instance = build.MainBuild()
        self.build_instance.execute_building_steps()
        # rig_meta_data = self.build_instance.rig_meta_data
        # operators_meta_data = self.build_instance.operators_meta_data
        # parenting_data_dic = self.build_instance.parenting_data_dic

    def test_build_execute_from_selected(self):
        pass
