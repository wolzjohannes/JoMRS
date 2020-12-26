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
# Date:       2020 / 12 / 26
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
import strings
import importlib
import os

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
        self.rig_meta_data = []
        self.parenting_data_dic = []
        self.rig_hierarchy = None
        self.rig_hierarchy_uuid = ""

    def get_meta_data(self, rig_meta_data=None, operator_meta_data=None):
        """
        Get meta data. If no operators_root node or main_op_nd is
        selected get the data found in the scene.

        Args:
            rig_meta_data(List): Filled with dict.
            operator_meta_data(List): Filled with dict.

        """
        logger.log(
            level="info", message="### Get meta data. " "###", logger=_LOGGER
        )
        self.operators_meta_data = operator_meta_data
        self.rig_meta_data = rig_meta_data
        if not operator_meta_data:
            if not self.selection:
                self.get_meta_data_from_god_node("operators")
            else:
                self.get_operators_meta_data_from_root_meta_node()
        if not rig_meta_data:
            if not self.selection:
                self.get_meta_data_from_god_node("rig")
            else:
                self.get_operators_meta_data_from_root_meta_node()

    def process_component_parenting_data(self, component_parenting_data=None):
        """
        Process the correct parenting data based on the rig and operator meta
        data.

        Args:
            component_parenting_data(List): Filled with dict

        """
        logger.log(
            level="info",
            message="### Processing component parenting data dictionary. "
            "###",
            logger=_LOGGER,
        )
        result = []
        self.parenting_data_dic = component_parenting_data
        if not component_parenting_data:
            for op_meta_data in self.operators_meta_data:
                data_dic = {}
                for rig_meta_data in self.rig_meta_data:
                    if op_meta_data.get("root_meta_nd") == rig_meta_data.get(
                        "root_meta_nd"
                    ):
                        rig_components_list = []
                        for rig_components in op_meta_data.get("meta_data"):
                            comp_container_uuid = strings.search_and_replace(
                                rig_components.get(constants.UUID_ATTR_NAME),
                                constants.MAIN_OP_ND_UUID_SUFFIX,
                                constants.COMP_CONTAINER_UUID_SUFFIX,
                            )
                            rig_components_list.append(comp_container_uuid)
                        data_dic[
                            "root_meta_nd_uuid"
                        ] = strings.search_and_replace(
                            rig_meta_data.get("meta_data").get(
                                constants.UUID_ATTR_NAME
                            ),
                            constants.OP_ROOT_ND_UUID_SUFFIX,
                            constants.RIG_CONTAINER_UUID_SUFFIX,
                        )
                        data_dic["rig_components_uuid"] = rig_components_list
                result.append(data_dic)
            self.parenting_data_dic = result

    def build_rig_container(self):
        """
        Build the rig container and its contents groups..
        """
        logger.log(
            level="info",
            message="### Start building rig hierarchy. " "###",
            logger=_LOGGER,
        )
        for data in self.rig_meta_data:
            self.rig_hierarchy = RigContainer(
                data.get("meta_data").get("rig_name")
            )
            self.rig_hierarchy.create_rig_container()
            self.rig_hierarchy_uuid = (
                data.get("meta_data")
                .get(constants.UUID_ATTR_NAME)
                .replace(
                    constants.OP_ROOT_ND_UUID_SUFFIX,
                    constants.RIG_CONTAINER_UUID_SUFFIX,
                )
            )
            self.rig_hierarchy.set_uuid(self.rig_hierarchy_uuid)

    def build_components(self):
        """
        Build all rig components based on passed operators meta data.
        """
        if not self.operators_meta_data:
            logger.log(
                level="error", message="No operators meta data " "accessible"
            )
            return False
        logger.log(
            level="info",
            message="### Start building rig components. " "###",
            logger=_LOGGER,
        )
        for data in self.operators_meta_data:
            root_meta_nd = data.get("root_meta_nd")
            meta_data = data.get("meta_data")
            logger.log(
                level="info",
                message="Build components for {}".format(root_meta_nd),
                logger=_LOGGER,
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
        logger.log(
            "error",
            message="Not implemented yet",
            func=self.connect_components,
            logger=_LOGGER,
        )

    def build_deformation_rig(self):
        logger.log(
            "error",
            message="Not implemented yet",
            func=self.build_deformation_rig,
            logger=_LOGGER,
        )

    def parent_components(self):
        logger.log(
            "error",
            message="Not implemented yet",
            func=self.parent_components,
            logger=_LOGGER,
        )

    def execute_building_steps(
        self,
        rig_meta_data=None,
        operator_meta_data=None,
        component_parenting_data=None,
    ):
        """
        Execute all rig building steps.

        Args:
            rig_meta_data(List): Filled with dict.
            operator_meta_data(List): Filled with dict.
            component_parenting_data(List): Filled with dict.

        """
        self.get_meta_data(rig_meta_data, operator_meta_data)
        self.process_component_parenting_data(component_parenting_data)
        self.build_rig_container()
        self.build_components()
        self.connect_components()
        self.parent_components()
        self.build_deformation_rig()

    def get_root_meta_nd_from_god_meta_node(self):
        """
        Return all root meta nodes from god meta node.

        Return:
            List: All root meta nodes connected to the god meta node.

        """
        if not self.god_meta_nd:
            self.get_god_meta_nd_from_scene()
        if self.god_meta_nd:
            all_meta_nodes = self.god_meta_nd.list_meta_nodes()
            return [
                root
                for root in all_meta_nodes
                if root.attr(constants.META_TYPE).get() == constants.META_TYPE_A
            ]

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

    def get_rig_meta_data_from_root_meta_node(self, root_meta_nd=None):
        """
        Get rig meta data from root meta node.

        Args:
            root_meta_nd(pmc.PyNode, optional): Root meta node.

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
        operator_root_node = root_meta_nd.get_root_op_nd()
        component_instance = components.main.Component(
            operators_root_node=operator_root_node
        )
        component_instance.get_rig_meta_data()
        self.rig_meta_data = [
            {
                "root_meta_nd": root_meta_nd,
                "meta_data": component_instance.rig_meta_data,
            }
        ]
        return self.rig_meta_data

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

    def get_meta_data_from_god_node(self, meta_data_type):
        """
        Collect the meta data from all root meta nodes in the scene.

        Args:
            meta_data_type(str): Defines meta data type to collect.
            Valid values are ['operators', 'rig']

        Return:
            List: Filled with a dictionary for each root_meta_nd.
            [{"root_meta_nd":pmc.PyNode(), "meta_data":List}]

        """
        result = []
        all_root_nodes = self.get_root_meta_nd_from_god_meta_node()
        if meta_data_type == "operators":
            for root_meta_node in all_root_nodes:
                self.get_operators_meta_data_from_root_meta_node(root_meta_node)
                result.append(self.operators_meta_data[0])
            self.operators_meta_data = result
        elif meta_data_type == "rig":
            for root_meta_node in all_root_nodes:
                self.get_rig_meta_data_from_root_meta_node(root_meta_node)
                result.append(self.rig_meta_data[0])
            self.rig_meta_data = result
        return result

    @staticmethod
    def get_container_node_from_uuid(uuid_):
        """
        Get a container from JoMRS uuid.

        Args:
            uuid_(str): The uuid for the node to search for

        Return:
            pmc.PyNode(): If successful. None if fail.

        """
        result = None
        scene_containers = pmc.ls(containers=True)
        for container in scene_containers:
            container_instance = mayautils.ContainerNode(
                container_node=container
            )
            try:
                if container_instance.get_uuid() == uuid_:
                    result = container_instance.container
            except:
                continue
        return result


class RigContainer(mayautils.ContainerNode):
    """
    Create a container node designed for the rig content.
    """

    CONTENT_GROUPS = [
        "M_RIG_0_GRP",
        "M_COMPONENTS_0_GRP",
        "M_GEO_0_GRP",
        "M_BSHP_0_GRP",
        "M_SHARED_ATTR_0_GRP",
        "M_NO_TRANSFORM_0_GRP",
    ]

    def __init__(self, rig_name=None, rig_container=None):
        """
        Args
            comp_name(str): The rig component name.
            comp_side(str): The component side.
            comp_index(int): The component index.
            component_container(pmc.PyNode()): A component container to pass.
        """
        mayautils.ContainerNode.__init__(self, content_root_node=True)
        self.meta_nd_name = constants.RIG_META_NODE_NAME
        self.name = constants.RIG_ROOT_NODE
        self.icon = os.path.normpath(
            "{}/rig_hierarchy_logo.png".format(constants.ICONS_PATH)
        )
        self.container = rig_container
        if not self.container:
            if rig_name:
                self.name = self.name.replace("name", rig_name)
                self.name = strings.string_checkup(self.name)
                self.container_content_root_name = self.container_content_root_name.replace(
                    "M", "M_RIG"
                ).replace(
                    "content_root", "{}_content_root".format(rig_name)
                )

    def create_rig_container(self):
        """
        Create the rig container.
        """
        self.create_container()
        self.create_container_content_from_list(self.CONTENT_GROUPS)
