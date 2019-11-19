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
# Date:       2019 / 11 / 19

"""
Rig elements main class.
This class should do:
- Template class for all components operators.
- Should create a operator for his own component.
- Should create the component init hierarchy.
- Should build the rig component based on the created operators.
- Should be able to import or reference a component maya file and change
the names of the components nodes. And get/return the meta node.
"""
import pymel.core as pmc
import logger
import logging
import operators
import os

##########################################################
# GLOBALS
##########################################################

module_logger = logging.getLogger(__name__ + ".py")
JOMRSVAR = os.environ['JoMRS']
ELEMENTSPATH = "/scripts/JoMRS/elements"

##########################################################
# CLASSES
##########################################################

class Main(operators.create_component_operator):
    def __init__(self):
        super(Main, self).__init__()
        self.operators = self

    def build_operator(operator_name, self):
        self.operator = self.operators.build_node(operator_name=operator_name)