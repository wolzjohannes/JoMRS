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
# Date:       2020 / 08 / 04

"""
Build a single control
"""

import pymel.core as pmc
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

    def __init__(self, name, side, index, main_operator_node=None):
        """
        Init function.

        Args:
            main_operator_node(pmc.PyNode): The main operator node.

        """
        main.component.__init__(self, main_operator_node)
        self.main_operator_node = main_operator_node
        self.name = name
        self.side = side
        self.index = index

    def _init_operator(self, name, side, index):
        """
        Init the operator creation.

        Args:
            name(str): Component name.
            side(str): The component side.
            index(str): Component index.

        """
        self.build_operator(
            self.name,
            self.COMP_TYPE,
            self.side,
            self.AXES,
            self.index,
            self.SUB_OPERATORS_COUNT,
            self.LOCAL_ROTATION_AXES,
        )

    def build_component_logic(self):
        """
        Build component logic. It is derivative method
        """
        jnt = pmc.createNode('joint')
        self.component.addChild(jnt)
