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
# Date:       2019 / 11 / 30

"""
Rig elements main class. Every rig element should inherit this class.
From this class you can build the element operators and the actual rig
component.
This class should do:
- Template class for all components operators.
- Should create a operator for his own component.
- Should create the component init hierarchy.
- Should build the rig component based on the created operators.
- Should be able to import or reference a component maya file and change
the names of the components nodes. And get/return the meta node.
- Maybe split things of. One class to create component operators and
another to import comps.
- The create component class should inherit all impotand things to create
the operators and create the final rig.
- All of them should be able to use with nodegraph qt.
- Create component class should create the component init hierarchy.
- Maya the build module i wrote can be in this module.
- This module creates a nodeGraph node.
"""
import pymel.core as pmc
import logger
import logging
import operators
import os
import strings

##########################################################
# GLOBALS
##########################################################

module_logger = logging.getLogger(__name__ + ".py")
JOMRSVAR = os.environ['JoMRS']
ELEMENTSPATH = "/scripts/JoMRS/elements"

##########################################################
# CLASSES
##########################################################

class operator(operators.create_component_operator):
    # def __init__(self):
    #     super(Main, self).__init__()
    #     self.element_op_hierarchy = self._init_hierarchy()

    def _init_hierarchy(self, element_name, side):
        self.component_root = pmc.createNode('transform', )

    def build_operator(operator_name, self):
        self.operator = self.operators.build_node(operator_name=operator_name)

    def set_element_type(self):
        pass

    def set_element_module_path(self):
        pass

    def create_input_port(self):
        pass

    def create_output_port(self):
        pass

    def build_from_operator(self):
        pass