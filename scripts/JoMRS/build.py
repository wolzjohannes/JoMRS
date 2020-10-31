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
# Date:       2020 / 10 / 22
"""
Rig build module. Collect the rig data based on the specified rig guide
in the scene. Based on that data it execute the rig build.
To Do:
build.py should find all operators. Build the rigs based on the operators
meta data. Then it should connect each Component via input and output matrix.
And connect ud attributes if necessary.
All this should be defined in the operators meta data.
"""

import pymel.core as pmc
import constants
import logger
import logging
import components.main
import importlib

reload(components.main)

##########################################################
# GLOBALS
##########################################################

_LOGGER = logging.getLogger(__name__ + ".py")

##########################################################
# CLASSES
##########################################################


class Main(object):
    def __init__(self):
        self.selection = components.main.selected()
        self.component_instance = components.main.Component(
            operators_root_node=self.selection,
            main_operator_node=self.selection,
            sub_operator_node=self.selection,
        )
        self.god_meta_nd = []
        self.operators_meta_data = []
        self.rig_meta_data = {}
        self.rig_transform = None
        self.rig_components = None
        self.rig_hierarchy = None
        self.rig_geo = None
        self.rig_bshp = None
        self.shared_attr = None
        self.no_transform = None

    def build_rig_hierarchy(self):
        rig_root_name = constants.RIG_ROOT_NODE.replace(
            name, self.rig_meta_data.get("rig_name")
        )
        self.rig_hierarchy = pmc.createNode("container", n=rig_root_name)
        icon = os.path.normpath(
            "{}/rig_hierarchy_logo.png".format(constants.ICONS_PATH)
        )
        self.rig_hierarchy.iconName.set(icon)
        self.rig_transform = pmc.createNode("transform", n="M_RIG_0_GRP")
        self.rig_components = pmc.createNode(
            "transform", n="M_COMPONENTS_0_GRP"
        )
        self.rig_geo = pmc.createNode("transform", n="M_GEO_0_GRP")
        self.rig_bshp = pmc.createNode("transform", n="M_BSHP_0_GRP")
        self.shared_attr = pmc.createNode("transform", n="M_SHARED_ATTR_0_GRP")
        self.no_transform = pmc.createNode(
            "transform", n="M_NO_TRANSFORM_0_GRP"
        )
        hierarchy_nodes = [self.rig_transform, self.rig_components, ]

    def add_node_to_rig_hierarchy(self, node):
        """
        Add node to rig hierarchy.

        Args:
            node(pmc.PyNode()): Node to add.

        """
        self.rig_hierarchy.addNode(node, ish=True, ihb=True, iha=True, inc=True)

    def build_components(self):
        raise NotImplemented()

    def connect_components(self):
        raise NotImplemented()

    def build_deformation_rig(self):
        raise NotImplemented()

    def execute_building_steps(self, operator_data=None):
        self.build_rig_hierarchy()

    def get_operators_meta_data_from_root_meta_node(self, root_meta_nd=None):
        """
        Gives back all operators meta data from operators root node.

        Args:
            root_meta_nd(pmc.PyNode, optional): Root meta node.

        Return:
            List: Filled with a dictionary for each operator in the scene.

        """
        main_meta_nodes = self.get_main_meta_nodes_from_root_meta_node(
            root_meta_nd
        )
        if main_meta_nodes:
            all_main_op_nodes = [
                meta_node.get_main_op_nd() for meta_node in main_meta_nodes
            ]
            for main_op_nd in all_main_op_nodes:
                component_instance = components.main.Component(
                    main_operator_node=main_op_nd
                )
                component_instance.get_operator_meta_data()
                self.operators_meta_data.append(
                    component_instance.operator_meta_data
                )
        return self.operators_meta_data

    def get_main_meta_nodes_from_root_meta_node(self, root_meta_nd=None):
        """
        Get all main meta nodes from root meta nd.

        Args:
            root_meta_nd(pmc.PyNode, optional): Root meta node.

        Return:
            List: ALl connected meta_nodes.
            False if fail.

        """
        if not root_meta_nd:
            if self.component_instance.root_meta_nd:
                root_meta_nd = self.component_instance.root_meta_nd
            else:
                logger.log(
                    level="error",
                    message="Need a selected JoMRS node " "in the scene",
                    logger=_LOGGER,
                )
                return False
        return root_meta_nd.get_main_meta_nodes()

    def get_god_meta_nd_from_scene(self):
        """
        Get the scene meta node.

        Returns:
            pmc.PyNode(): The god network node.

        """
        temp = pmc.ls(typ="network")
        for node in temp:
            if (
                node.hasAttr(constants.META_NODE_ID)
                and node.attr(constants.META_NODE_ID).get() is True
                and node.attr(constants.META_TYPE).get()
                == constants.META_GOD_TYPE
            ):
                self.god_meta_nd.append(node)
        if self.god_meta_nd:
            if len(self.god_meta_nd) > 1:
                logger.log(
                    level="error",
                    message="More then one god meta node in the scene not allowed.",
                    logger=_LOGGER,
                )
                self.god_meta_nd = None
                return False
            self.god_meta_nd = self.god_meta_nd[0]
            return self.god_meta_nd
        logger.log(
            level="error",
            message="No god meta node in the scene",
            logger=_LOGGER,
        )
        return False

    def get_operators_meta_data_from_god_node(self):
        raise NotImplemented()
