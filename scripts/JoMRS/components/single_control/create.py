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
# Date:       2020 / 09 / 11

"""
Build a single single_control
"""

import pymel.core as pmc
import constants
import curves
from components import main

reload(main)
reload(curves)

##########################################################
# CLASSES
##########################################################


class Main(main.component):
    """
    Single single_control component class
    """

    COMP_TYPE = "single_control"
    SUB_OPERATORS_COUNT = 0
    LOCAL_ROTATION_AXES = True
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
            name(str, optional): Component name.
            component_type(str, optional): Component type.
            side(str, optional): The component side.
            index(int, optional): The component index.
            operators_root_node(pmc.PyNode(), optional): The operators root
            node.
            main_operator_node(pmc.PyNode(), optional): The main operator_node.
            sub_operator_node(pmc.PyNode(), optional)): The sub operator node.

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

    def build_component_logic(self, main_operator_ws_matrix=None):
        """
        Build component logic. It is derivative method from parent class.
        """
        if not main_operator_ws_matrix:
            main_operator_ws_matrix = self.get_main_op_ws_matrix()
        control_name = constants.DEFAULT_CONTROL_NAME_PATTERN
        control_name = control_name.replace("M_", self.side + "_")
        control_name = control_name.replace("name", self.name)
        control_name = control_name.replace("index", str(self.index))
        offset_grp = pmc.createNode('transform', n=control_name + '_offset_GRP')
        curve_instance = curves.BoxControl()
        curve = curve_instance.create_curve(
            name=control_name, match=main_operator_ws_matrix
        )
        offset_grp.addChild(curve[0])
        self.controls.append(curve[1])
        self.component_rig_list.append(offset_grp)
        self.input_matrix_offset_grp.append(offset_grp)
        self.bnd_output_matrix.append(curve[1])
