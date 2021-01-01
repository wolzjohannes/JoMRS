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
# Date:       2020 / 12 / 30
"""
Rig build module. Collect the rig data based on the specified rig operators
in the scene. Based on that data it execute the rig build. This module produces
a bunch of list and dictionaries which are used to build the final rig.
This data can be saved as json file. And it can build a rig based on a json
file imports.
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
    """
    Main class to build a rig based on the operators in the scene.
    The rig building is divided in steps. All steps are their own method.
    And the "self.execute_building_steps()" method will execute them in the
    right order. This method is the finale building method.

    The steps are:
    self.get_meta_data(rig_meta_data, operator_meta_data)
    self.process_component_parenting_data(component_parenting_data)
    self.build_rig_container()
    self.build_components()
    self.connect_components()
    self.parent_components()
    self.build_deformation_rig()

    """

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
        self.rig_container = None
        self.rig_container_uuid = ""

    def get_meta_data(self, rig_meta_data=None, operator_meta_data=None):
        """
        Get meta data. If no operators_root node or main_op_nd is
        selected get the data found in the scene. It collect the
        rig_meta_data and the operator_meta_data. It stores the data in the
        "self.rig_meta_data" and "self.operators_meta_data" variables.

        Args:
            rig_meta_data(List): Filled with dict.
            operator_meta_data(List): Filled with dict.

        Example:
            >>>import build
            >>>build_instance = build.MainBuild()
            >>>build_instance.get_meta_data()
            [{'root_meta_nd': nt.RootOpMetaNode(u'M_ROOT_op_0_METAND'),
            'meta_data': {'rig_name': u'MOM', 'r_rig_color': 6,
            'l_rig_sub_color': 18,
            'JoMRS_UUID': u'cc4064e3-f3b0-4512-8e44-b914b3df3c1e-root_op',
            'l_rig_color': 13, 'r_rig_sub_color': 9, 'm_rig_sub_color': 11,
            'm_rig_color': 17}},
            {'root_meta_nd': nt.RootOpMetaNode(u'M_ROOT_op_1_METAND'),
            'meta_data': {'rig_name': u'Test', 'r_rig_color': 6,
            'l_rig_sub_color': 18,
            'JoMRS_UUID': u'd16fe8f1-0d50-4a20-9b61-79a2f2f817bd-root_op',
            'l_rig_color': 13, 'r_rig_sub_color': 9, 'm_rig_sub_color': 11,
            'm_rig_color': 17}}]
            [{'root_meta_nd': nt.RootOpMetaNode(u'M_ROOT_op_0_METAND'),
            'meta_data': [{'component_type': u'single_control',
            'component_side': u'L',
            'main_op_nd_ws_matrix':
            Matrix([[-0.855774425863, -0.416261824405, -0.307207137909, 0.0],
            [0.495584209548, -0.489167922022, -0.717712362519, 0.0],
            [0.148480380138, -0.766446891577, 0.624910184831, 0.0],
            [-16.108, 14.13, 0.97, 1.0]]), 'sub_op_nd_ws_matrix': [],
            'connection_types': [u'translate', u'rotate', u'scale'],
            'ik_spaces_ref': None, 'connect_nd': None, 'child_nd': [],
            'parent_nd': None, u'control_shape': 1, 'component_index': 0,
            'JoMRS_UUID': u'f0bc993e-38e5-4210-816c-3dac633b6ee0-main_op',
            'component_name': u'MOM'}]},
            {'root_meta_nd': nt.RootOpMetaNode(u'M_ROOT_op_1_METAND'),
            'meta_data': [{'component_type': u'single_control',
            'component_side': u'M',
            'main_op_nd_ws_matrix':
            Matrix([[0.0498978099393, 0.554286236569, -0.830829089834, 0.0],
            [0.439365178618, 0.734866446494, 0.516652248263, 0.0],
            [0.896921651194, -0.390817187144, -0.206865845057, 0.0],
            [13.124, 13.397, -9.37, 1.0]]), 'sub_op_nd_ws_matrix': [],
            'connection_types': [u'translate', u'rotate', u'scale'],
            'ik_spaces_ref': None, 'connect_nd': None, 'child_nd': [],
            'parent_nd': None, u'control_shape': 2, 'component_index': 1,
            'JoMRS_UUID': u'62c00a43-269b-4b19-b275-2bc7d9b28162-main_op',
            'component_name': u'Test'}]}]

        """
        logger.log(
            level="info", message="### Get meta data. " "###", logger=_LOGGER
        )
        # Pass data from json file or other source.
        self.operators_meta_data = operator_meta_data
        self.rig_meta_data = rig_meta_data
        # If no data passed generate it.
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
        data. It will store the data in the "self.parenting_data_dic" variable.

        Args:
            component_parenting_data(List): List filled with dict to pass.

        Example:
            >>>import build
            >>>build_instance = build.MainBuild()
            >>>build_instance.process_component_parenting_data()
            [{'root_meta_nd_uuid':
            u'cc4064e3-f3b0-4512-8e44-b914b3df3c1e-rig_container',
            'rig_components_uuid':
            [u'f0bc993e-38e5-4210-816c-3dac633b6ee0-comp_container']},
            {'root_meta_nd_uuid':
            u'd16fe8f1-0d50-4a20-9b61-79a2f2f817bd-rig_container',
            'rig_components_uuid': [
            u'62c00a43-269b-4b19-b275-2bc7d9b28162-comp_container']}]

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
        Build the rig container and its sibling containers.
        """
        logger.log(
            level="info",
            message="### Start building rig container. " "###",
            logger=_LOGGER,
        )
        # Loop through the rig meta data.
        for data in self.rig_meta_data:
            self.rig_container = RigContainer(
                data.get("meta_data").get("rig_name")
            )
            self.rig_container.create_rig_container()
            # Refactor root_op uuid to rig_container uuid. So we are able to
            # find the container easier in the scene and we are not limited
            # to hardcoded names. The refactored uuid link the operators root
            # and the rig container. This is important for the component
            # parenting.
            self.rig_container_uuid = (
                data.get("meta_data")
                .get(constants.UUID_ATTR_NAME)
                .replace(
                    constants.OP_ROOT_ND_UUID_SUFFIX,
                    constants.RIG_CONTAINER_UUID_SUFFIX,
                )
            )
            # Give the rig container its refactored uuid.
            self.rig_container.set_uuid(self.rig_container_uuid)

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
        # Loop through the operators meta data
        for data in self.operators_meta_data:
            # Get root meta node. This represent the operators root node.
            root_meta_nd = data.get("root_meta_nd")
            # Get the operators meta data belongs to root_meta_nd.
            meta_data = data.get("meta_data")
            logger.log(
                level="info",
                message="Build components for {}".format(root_meta_nd),
                logger=_LOGGER,
            )
            # loop through meta data
            for m_data in meta_data:
                # based on the component type stored in the meta data create
                # the python import statement string for each found component
                # type.
                component_module_name = "components.{}.create".format(
                    m_data.get(constants.META_MAIN_COMP_TYPE)
                )
                # import correct module for each component based on the
                # formatted import statement string.
                create_module = importlib.import_module(component_module_name)
                # reload(create_module)
                # instance the MainCreate class which is the base of each rig
                # component.
                main_create = create_module.MainCreate()
                # build each component
                main_create.build_from_operator(m_data)

    def connect_components(self):
        """
        Will connect all input and outputs of each component.
        """
        logger.log(
            "error",
            message="Not implemented yet",
            func=self.connect_components,
            logger=_LOGGER,
        )

    def build_deformation_rig(self):
        """
        Will build the deformation rig hierarchy.
        """
        logger.log(
            "error",
            message="Not implemented yet",
            func=self.build_deformation_rig,
            logger=_LOGGER,
        )

    def parent_components(self):
        """
        Add the rig components to the components sibling node of the rig
        container. Based on the parenting_data_dic dictionary.
        """
        logger.log(
            level="info",
            message="### Add rig components to rig container. " "###",
            logger=_LOGGER,
        )
        for data_dic in self.parenting_data_dic:
            # Filter the rig container in the scene based on his JoMRS uuid.
            rig_container_nd = self.get_container_node_from_uuid(
                data_dic.get("root_meta_nd_uuid")
            )
            rig_container_nd = RigContainer(rig_container=rig_container_nd)
            # add rig components to rig container
            for comp_container_uuid in data_dic.get("rig_components_uuid"):
                comp_container = self.get_container_node_from_uuid(
                    comp_container_uuid
                )
                rig_container_nd.add_rig_component(comp_container)

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

        Returns:
            List: All root meta nodes connected to the god meta node.
            None if fail.

        """
        # If no god meta node stored, store it.
        if not self.god_meta_nd:
            self.get_god_meta_nd_from_scene()
        if self.god_meta_nd:
            # If god meta node stored get all JoMRS meta nodes in the scene.
            all_meta_nodes = self.god_meta_nd.list_meta_nodes()
            # Return only all found root_op_meta nodes. Root meta nodes only
            # exist ones for each operators root node. It stores dependencies
            # to all meta main nodes corresponding to the operators root node.
            return [
                root
                for root in all_meta_nodes
                if root.attr(constants.META_TYPE).get() == constants.META_TYPE_A
            ]

    def get_operators_meta_data_from_root_meta_node(self, root_meta_nd=None):
        """
        Gives back all operators meta data from operators root node. And
        store it the "self.operators_meta_data()" variable.

        Args:
            root_meta_nd(pmc.PyNode, optional): Root meta node.

        Returns:
            List: Filled with a dictionary for each root_meta_nd.
            [{"root_meta_nd":pmc.PyNode(), "meta_data":List}]

        """
        meta_data = []
        # Get all main meta nodes from root meta node as dictionaries.
        main_meta_nodes_data = self.get_main_meta_nodes_from_root_meta_node(
            root_meta_nd
        )
        # Filter the meta nodes from the dic.
        main_meta_nodes = main_meta_nodes_data.get("main_meta_nodes")
        # Filter the root meta nodes from the dic.
        root_meta_nd = main_meta_nodes_data.get("root_meta_nd")
        # if main meta nodes exist. Get the operators meta data and store it
        # in a list.
        if main_meta_nodes:
            # get each main operator node from each main_op_meta node.
            all_main_op_nodes = [
                meta_node.get_main_op_nd() for meta_node in main_meta_nodes
            ]
            # Store component class instance and pass the main_op_node. So we
            # can use the get_operator_meta_data() method. The we store the
            # operator_meta_data dic in the meta_data list.
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
        # If no root_meta_nd stored get the selected JoMRS node and from
        # there get the root_meta_nd.
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
        # Get the operator_root_node from root_meta_no. Then create a
        # component class instance and pass the operators_root_nd. So we are
        # able to use the "get_rig_meta_data()" class and store the
        # rig_meta_data dic.
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

        Returns:
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
        # Filter the JoMRS meta nodes from all found network nodes.
        for node in temp:
            if (
                node.hasAttr(constants.META_NODE_ID)
                and node.attr(constants.META_NODE_ID).get() is True
                and node.attr(constants.META_TYPE).get()
                == constants.META_GOD_TYPE
            ):
                self.god_meta_nd.append(node)
        # Be sure that only one god_meta_nd exist.
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

        Returns:
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
        # Get all container nodes in the scene.
        scene_containers = pmc.ls(containers=True)
        for container in scene_containers:
            # Create a container class instance so we are able to use the
            # get_uuid() method.
            container_instance = mayautils.ContainerNode(
                container_node=container
            )
            try:
                # Use a try and except to get the uuid because not every
                # container node has the uuid stored as meta data. And we are
                # only interested for the nodes with this meta data.
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
            rig_name(str): The rig name.
            rig_container(pmc.PyNode()): A rig container to pass.
        """
        mayautils.ContainerNode.__init__(self)
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

    def create_transform(self, name):
        """
        Overwritten method from base class. It use a container node instead
        of a simple transform.

        Args:
            name(str): Container name.

        """
        self.container_content[name] = pmc.nt.Container(n=name)
        self.container.addNode(
            self.container_content[name], ish=True, ihb=True, iha=True, inc=True
        )
        # Check if a container node with the same name exist.
        # If so the new created container get a number in the suffix as maya
        # standard procedure. Then we take that and put it at the correct place
        # in our naming convention.
        container_content_name = strings.normalize_suffix_1(
            self.container_content[name].name(), logger_=_LOGGER
        )
        self.container_content[name].rename(container_content_name)

    def add_node_to_container_content(self, node, content_name):
        """
        Overwritten base class method. Add node to container content.

        Args:
            node(pmc.PyNode()): The node to add.
            content_name(str): The content node.

        """
        self.container_content.get(content_name).addNode(
            node, ish=True, ihb=True, iha=True, inc=True
        )

    def create_rig_container(self):
        """
        Create the rig container.
        """
        self.create_container()
        self.create_container_content_from_list(self.CONTENT_GROUPS)

    def add_rig_component(self, rig_component=None):
        """
        Add rig component to rig container.

        Args:
            rig_component(pmc.PyNode()): The rig component node.

        """
        # Get container content
        self.get_container_content()
        # Filter the component group
        keys = self.container_content.keys()
        component_key = [
            comp_key
            for comp_key in keys
            if strings.search("COMPONENTS", comp_key)
        ][0]
        # Add rig component node to component sibling of the rig container.
        self.add_node_to_container_content(rig_component, component_key)
