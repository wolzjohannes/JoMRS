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
# Date:       2019 / 09 / 16

"""
Rig build method. Collect the rig data based on the specified rig guide
in the scene. Based on that data it execute the rig build.
"""

import pymel.core as pmc
import logger
import logging
import operators
import strings
import meta
reload(operators)
reload(meta)

##########################################################
# GLOBALS
##########################################################

module_logger = logging.getLogger(__name__ + ".py")
OPROOTTAGNAME = operators.OPROOTTAGNAME
OPMAINTAGNAME = operators.OPMAINTAGNAME
OPSUBTAGNAME = operators.OPSUBTAGNAME
ROOTOPMETANDATTRNAME = operators.ROOTOPMETANDATTRNAME
STEPS = [
    "collect_overall_rig_data",
    "collect_main_operators_data",
    "collect_components_inputs_outputs"
    "create_main_ops_dic",
    "create_init_hierarchy",
    "create_rig_elements",
    "connect_rig_elements",
    "build_bind_skeleton",
]
OVERALLRIGPARAMS = meta.ROOTOPMETAPARAMS
MAINOPCOMPPARAMS = meta.MAINOPMETAPARAMS
MAINMETANDPLUG = meta.MAINMETANDPLUG

##########################################################
# CLASSES
##########################################################


class Main(object):
    """
    Main class for execute the rig build.
    """

    def __init__(
        self,
        op_root_tag_name=OPROOTTAGNAME,
        root_op_meta_nd_attr_name=ROOTOPMETANDATTRNAME,
        steps=STEPS,
    ):
        """
        Args:
                op_root_tag_name(str):Tag name.
                root_op_meta_nd_attr_name(str): Message attr to root op meta nd.
                steps(list of strings): The build steps.
        """

        self.selection = pmc.ls(sl=True)
        if not self.selection:
            self.selection = pmc.ls(typ="transform")
        self.root_operator_nd = [
            node
            for node in self.selection
            if node.hasAttr(op_root_tag_name)
            and node.attr(op_root_tag_name).get() is True
        ]

        self.steps = steps
        self.root_op_meta_nd = [
            meta_nd.attr(root_op_meta_nd_attr_name).get()
            for meta_nd in self.root_operator_nd
        ]
        self.main_operators_data = []
        self.rig_overall_data = []
        self.components_input_connects = []
        self.build_data = []

    def get_overall_rig_data(self, overall_rig_parameters=OVERALLRIGPARAMS):
        """
        Get overall rig data for each root operator node. And pass it to
        self.rig_overall_data class list.
        Args:
                overall_rig_parameters(list): Params to search for.
        Return:
                list: self.rig_overall_data class list.
        """

        overall_rig_parameters = overall_rig_parameters

        for meta_nd in self.root_op_meta_nd:
            data = {}
            data["root_operator_meta_nd"] = meta_nd
            for param in overall_rig_parameters:
                data[param] = meta_nd.attr(param).get()
            self.rig_overall_data.append(data)

        logger.log(level="info", message=self.steps[0], logger=module_logger)
        return self.rig_overall_data

    def get_main_operators_data(self, plug=MAINMETANDPLUG,
                                main_op_comp_params = MAINOPCOMPPARAMS):
        """
        Get the main operators data.
        Args:
                plug(str): Name for main_nd message attribute.
                main_op_comp_params(list): Attribute names to search for.
        Return:
                list: Dictonaries with main operators data for each
                root_operator_meta_nd.
        """

        for main_nd in self.root_op_meta_nd:
            data = {}
            data["root_operator_meta_nd"] = main_nd
            ud_attr = main_nd.listAttr(ud=True)
            ud_attr = [
                attr_
                for attr_ in ud_attr
                if strings.search(plug, str(attr_))
            ]
            main_operators_meta_nd = [node.get() for node in ud_attr]
            for x in range(len(main_operators_meta_nd)):
                main_operator_nd = main_operators_meta_nd[
                    x].main_operator_nd.get()
                temp_data = {}
                temp_data['main_operator_nd'] = main_operator_nd
                for param in main_op_comp_params:
                    temp_data[param] = main_operators_meta_nd[x].attr(
                        param).get()
                data['main_op_data_{}'.format(str(x))] = temp_data
            self.main_operators_data.append(data)
        logger.log(level="info", message=self.steps[1], logger=module_logger)
        return self.main_operators_data

    def define_component_edges(self):
        pass

