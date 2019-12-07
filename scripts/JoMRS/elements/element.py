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
# Date:       2019 / 11 /

"""
Rig elements main module. This class is the template to create a rig
element. This class should inherit later from each element main module.
"""
import pymel.core as pmc
import logger
import logging
import operators
import os
import strings
import attributes

##########################################################
# GLOBALS
##########################################################

module_logger = logging.getLogger(__name__ + ".py")
JOMRSVAR = os.environ["JoMRS"]
ELEMENTSPATH = "/scripts/JoMRS/elements"

##########################################################
# CLASSES
# - able to build the input and offset connections
##########################################################


class build_rig_element(object):

    def init_hierarchy(self, element_name, side):
        element_root_name = "{}_RIG_{}_element_0_GRP".format(
            side, element_name.lower()
        )
        element_root_name = strings.string_checkup(element_root_name)
        self.element_root = pmc.createNode("transform", n=element_root_name)
        attributes.lock_and_hide_attributes(self.element_root)
        temp = [
            pmc.createNode("transform", n="input"),
            pmc.createNode("transform", n="output"),
            pmc.createNode("transform", n="element"),
            pmc.createNode("transform", n="spaces"),
        ]
        for node in temp:
            self.element_root.addChild(node)
            attributes.lock_and_hide_attributes(node)

    def create_input_port(self):
        pass

    def create_output_port(self):
        pass

    def build_from_operator(self):
        pass
