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
# Date:       2020 / 09 / 07

"""
Build a single control
"""

import pymel.core as pmc
import curves
from components import main

reload(main)

##########################################################
# CLASSES
##########################################################


class Main(main.component):
    """
    Main class for component building.It handles the operator building,
    component logic and rig building.
    """

    COMP_TYPE = "control"
    SUB_OPERATORS_COUNT = 0
    LOCAL_ROTATION_AXES = False
    AXES = "X"

    def __init__(
        self,
        name=None,
        side=None,
        index=None,
        operators_root_node=None,
        main_operator_node=None,
        sub_operator_node=None,
    ):
        """
        Init function.

        Args:
            main_operator_node(pmc.PyNode): The main operator node.

        """
        main.component.__init__(
            self,
            name,
            self.COMP_TYPE,
            side,
            index,
            operators_root_node,
            main_operator_node,
            sub_operator_node,
        )

    def _init_operator(self):
        """
        Init the operator creation.
        """
        self.build_operator(
            self.AXES, self.SUB_OPERATORS_COUNT, self.LOCAL_ROTATION_AXES
        )

    def build_component_logic(self):
        """
        Build component logic. It is derivative method
        """
        curve_instance = curves.BoxControl()
        curve = curve_instance.create_curve(name=self.name)
        self.controls.append(curve[1])
        self.component_rig_list.append(curve[0])
        self.input_matrix_offset_grp.append(curve[0])
        self.bnd_output_matrix.append(curve[1])
