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
# Date:       2020 / 11 / 12
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
import mayautils
import importlib

##########################################################
# GLOBALS
##########################################################

_LOGGER = logging.getLogger(__name__ + ".py")

##########################################################
# CLASSES
##########################################################


class MainBuild(object):
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
        self.rig_hierarchy = None

    def build_rig_hierarchy(self):
        rig_root_name = constants.RIG_ROOT_NODE.replace(
            name, self.rig_meta_data.get("rig_name")
        )
        icon = os.path.normpath(
            "{}/rig_hierarchy_logo.png".format(constants.ICONS_PATH)
        )
        self.rig_hierarchy = mayautils.ContainerNode(rig_root_name, icon)
        self.rig_hierarchy.create_container_content_from_list(
            [
                "M_RIG_0_GRP",
                "M_COMPONENTS_0_GRP",
                "M_GEO_0_GRP",
                "M_BSHP_0_GRP",
                "M_SHARED_ATTR_0_GRP",
                "M_NO_TRANSFORM_0_GRP",
            ]
        )

    def build_components(self, operator_meta_data=None):
        """
        Build all rig components based on the

        Args:
            operator_meta_data(List): Filled with dict.


        """
        if not operator_meta_data:
            operator_meta_data = self.operators_meta_data
        if not operator_meta_data:
            logger.log(
                level="error", message="No operators meta data " "accessible"
            )
            return False
        for data in operator_meta_data:
            root_meta_nd = data.get("root_meta_nd")
            meta_data = data.get("meta_data")
            logger.log(
                level="info",
                message="Build components for {}".format(root_meta_nd),
                logger=_LOGGER
            )
            for m_data in meta_data:
                component_module_name = "components.{}.create".format(
                    m_data.get(constants.META_MAIN_COMP_TYPE)
                )
                create_module = importlib.import_module(component_module_name)
                main_create = create_module.MainCreate()
                main_create.build_from_operator(m_data)
        return True

    def connect_components(self):
        raise NotImplemented()

    def build_deformation_rig(self):
        raise NotImplemented()

    def execute_building_steps(self, operator_meta_data=None):
        self.build_rig_hierarchy()
        self.build_components(operator_meta_data)

    def get_operators_meta_data_from_root_meta_node(self, root_meta_nd=None):
        """
        Gives back all operators meta data from operators root node.

        Args:
            root_meta_nd(pmc.PyNode, optional): Root meta node.

        Return:
            List: Filled with a dictionary for each root_meta_nd.
            [{"root_meta_nd":pmc.PyNode(), "meta_data":List}]

        """
        meta_data = []
        main_meta_nodes_data = self.get_main_meta_nodes_from_root_meta_node(
            root_meta_nd
        )
        main_meta_nodes = main_meta_nodes_data.get("main_meta_nodes")
        root_meta_nd = main_meta_nodes_data.get("root_meta_nd")
        if main_meta_nodes:
            all_main_op_nodes = [
                meta_node.get_main_op_nd() for meta_node in main_meta_nodes
            ]
            for main_op_nd in all_main_op_nodes:
                component_instance = components.main.Component(
                    main_operator_node=main_op_nd
                )
                component_instance.get_operator_meta_data()
                meta_data.append(component_instance.operator_meta_data)
        self.operators_meta_data = [
            {"root_meta_nd": root_meta_nd, "meta_data": meta_data}
        ]
        return [{"root_meta_nd": root_meta_nd, "meta_data": meta_data}]

    def get_main_meta_nodes_from_root_meta_node(self, root_meta_nd=None):
        """
        Get all main meta nodes from root meta nd.

        Args:
            root_meta_nd(pmc.PyNode, optional): Root meta node.

        Return:
            Dict: ALl connected meta_nodes.
            {"root_meta_nd":pmc.PyNode(), "main_meta_nodes":List}
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
        return {
            "root_meta_nd": root_meta_nd,
            "main_meta_nodes": root_meta_nd.get_main_meta_nodes(),
        }

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
            return True
        logger.log(
            level="error",
            message="No god meta node in the scene",
            logger=_LOGGER,
        )
        return False

    def get_operators_meta_data_from_god_node(self):
        """
        Collect the operators meta data from all root meta nodes in the scene.

        Return:
            List: Filled with a dictionary for each root_meta_nd.
            [{"root_meta_nd":pmc.PyNode(), "meta_data":List}]

        """
        result = []
        self.get_god_meta_nd_from_scene()
        if self.god_meta_nd:
            all_meta_nodes = self.god_meta_nd.list_meta_nodes()
            all_root_nodes = [
                root
                for root in all_meta_nodes
                if root.attr(constants.META_TYPE).get() == constants.META_TYPE_A
            ]
            for root_meta_node in all_root_nodes:
                self.get_operators_meta_data_from_root_meta_node(root_meta_node)
                result.append(self.operators_meta_data[0])
        self.operators_meta_data = result
        return result
