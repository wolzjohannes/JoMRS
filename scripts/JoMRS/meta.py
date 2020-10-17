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
# Date:       2020 / 09 / 25

"""
Meta node creation module.
"""
import pymel.all as pmc
import logging
import attributes
import re
import strings
import constants

reload(constants)
reload(attributes)

##########################################################
# GLOBALS
#########################################################

_LOGGER = logging.getLogger(__name__ + ".py")

##########################################################
# CLASSES
##########################################################


class MetaNode(pmc.nt.Network):
    """
    Creates a network node which works as MetaNode node.
    """

    @classmethod
    def list(cls, *args, **kwargs):
        """ Returns all instances the node in the scene """

        kwargs["type"] = cls.__melnode__
        return [
            node for node in pmc.ls(*args, **kwargs) if isinstance(node, cls)
        ]

    @classmethod
    def _isVirtual(cls, obj, name, tag=constants.META_NODE_ID):
        """
        This actual creates the node. If a specific tag is found.
        If not it will create a default node.
        PyMEL code should not be used inside the callback,
        only API and maya.cmds.
        Args:
                obj(dagnode): The network node.
                name(str): The nodes name.
                tag(str): The specific creation tag.
        Return:
                True if node with tag exist / False if not or tag is disable.
        """
        fn = pmc.api.MFnDependencyNode(obj)
        try:
            if fn.hasAttribute(tag):
                plug = fn.findPlug(tag)
                if plug.asBool() == 1:
                    return True
                return False
        except:
            pass
        return False

    @classmethod
    def _preCreateVirtual(cls, **kwargs):
        """This is called before creation. python allowed."""
        return kwargs

    @classmethod
    def _postCreateVirtual(
        cls,
        newNode,
        tag=constants.META_NODE_ID,
        type=constants.META_TYPE,
        class_type=constants.META_BASE_TYPE,
    ):
        """
        This is called after creation, pymel/cmds allowed.
        It will create a set of attributes. And the important check up tag for
        the meta node.
        Args:
                newNode(dagnode): The new node.
                tag(str): The specific creation tag.
                type(str): The meta node type.
                class_type(str): The class type.
        """
        newNode.addAttr(tag, at="bool")
        newNode.attr(tag).set(1)
        newNode.addAttr(type, dt="string")
        newNode.attr(type).set(class_type)


class GodMetaNode(MetaNode):
    """
    Creates a Meta Node as God Meta Node for all meta nodes in the scene.
    """

    SUBNODE_TYPE = constants.META_GOD_TYPE

    @classmethod
    def list(cls, *args, **kwargs):
        """ Returns all instances of all characters in the scene """

        kwargs["type"] = cls.__melnode__
        return [
            node for node in pmc.ls(*args, **kwargs) if isinstance(node, cls)
        ]

    @classmethod
    def _isVirtual(
        cls, obj, name, tag=constants.META_NODE_ID, type=constants.META_TYPE
    ):
        """
         This actual creates the node. If a specific tag is found.
         If not it will create a default node.
         PyMEL code should not be used inside the callback,
         only API and maya.cmds.
         Args:
                 obj(dagnode): The network node.
                 name(str): The nodes name.
                 tag(str): The specific creation tag.
                 type(str): The meta node type.
         Return:
                 True if node with tag exist / False if not or tag is disable.
         """
        fn = pmc.api.MFnDependencyNode(obj)
        try:
            if fn.hasAttribute(tag):
                plug = fn.findPlug(tag)
                if plug.asBool() == 1:
                    if fn.hasAttribute(type):
                        plug = fn.findPlug(type)
                        if plug.asString() == cls.SUBNODE_TYPE:
                            return True
                    return False
        except:
            pass
        return False

    @classmethod
    def _postCreateVirtual(
        cls, newNode, type=constants.META_TYPE, name="god_meta_0_METAND"
    ):
        """
        This is called after creation, pymel/cmds allowed.
        It will create a set of attributes. And the important check up tag for
        the meta node.
        Args:
                newNode(dagnode): The new node.
                tag(str): The specific creation tag.
                type(str): The meta node type.
                name(str): The name of the god meta node.
        """
        MetaNode._postCreateVirtual(newNode)
        newNode.attr(type).set(cls.SUBNODE_TYPE)
        newNode.rename(name)

    def add_meta_node(self, node):
        """
        Add a meta node to the god meta node as message attr connection.

        Args:
                node(dagnode): The node to add.

        """
        new_attribute = {}
        ud_attr = self.listAttr(ud=True)
        ud_attr = [str(attr_).split(".")[1] for attr_ in ud_attr]
        dirty_plugs = []
        meta_plug = [
            attr_
            for attr_ in ud_attr
            if re.search(constants.META_GOD_META_ND_ATTR, attr_)
        ]
        if not meta_plug:
            count = "0"
        else:
            for plug in meta_plug:
                if not self.attr(plug).get():
                    self.attr(plug).delete()
                else:
                    dirty_plugs.append(plug)
            integer = dirty_plugs[-1].split(
                "{}_".format(constants.META_GOD_META_ND_ATTR)
            )[1]
            count = str(int(integer) + 1)
        new_attribute["name"] = "{}_{}".format(
            constants.MAIN_META_ND_PLUG, count
        )
        new_attribute["attrType"] = "message"
        new_attribute["keyable"] = False
        new_attribute["channelBox"] = False
        new_attribute["input"] = node.message
        attributes.add_attr(node=self, **new_attribute)

    def list_meta_nodes(
        self, plug="meta_nd", class_filter=None, type=constants.META_TYPE
    ):
        """
        List all meta nodes in the scene.
        Args:
                plug(str): The attributes name for message connection.
                class_filter(str): Filters a class type to return.
                If none it returns all classes found in the scene.
        Return:
                list: All found meta nodes in the scene.
        """
        result = None
        ud_attr = self.listAttr(ud=True)
        meta_plug = [attr_ for attr_ in ud_attr if re.search(plug, str(attr_))]
        if meta_plug:
            result = [node.get() for node in meta_plug]
        if class_filter:
            result = [
                node for node in result if node.attr(type).get() == class_filter
            ]
        return result


class RootOpMetaNode(MetaNode):
    """
    Creates a Meta Node as Root Meta Node for all operators meta nodes.
    """

    SUBNODE_TYPE = constants.META_TYPE_A

    @classmethod
    def list(cls, *args, **kwargs):
        """ Returns all instances of all characters in the scene """

        kwargs["type"] = cls.__melnode__
        return [
            node for node in pmc.ls(*args, **kwargs) if isinstance(node, cls)
        ]

    @classmethod
    def _isVirtual(
        cls, obj, name, tag=constants.META_NODE_ID, type=constants.META_TYPE
    ):
        """
         This actual creates the node. If a specific tag is found.
         If not it will create a default node.
         PyMEL code should not be used inside the callback,
         only API and maya.cmds.
         Args:
                 obj(dagnode): The network node.
                 name(str): The nodes name.
                 tag(str): The specific creation tag.
                 type(str): The meta node type.
         Return:
                 True if node with tag exist / False if not or tag is disable.
         """
        fn = pmc.api.MFnDependencyNode(obj)
        try:
            if fn.hasAttribute(tag):
                plug = fn.findPlug(tag)
                if plug.asBool() == 1:
                    if fn.hasAttribute(type):
                        plug = fn.findPlug(type)
                        if plug.asString() == cls.SUBNODE_TYPE:
                            return True
                    return False
        except:
            pass
        return False

    @classmethod
    def _postCreateVirtual(
        cls,
        newNode,
        type=constants.META_TYPE,
        god_meta_name="god_meta_0_METAND",
    ):
        """
        This is called after creation, pymel/cmds allowed.
        It will create a set of attributes. And the important check up tag for
        the meta node.
        Args:
                newNode(dagnode): The new node.
                tag(str): The specific creation tag.
                type(str): The meta node type.
                god_meta_name(str): The name of the god meta node.
        """
        MetaNode._postCreateVirtual(newNode)
        try:
            god_mata_nd = pmc.PyNode(god_meta_name)
        except:
            god_mata_nd = GodMetaNode()
        newNode.attr(type).set(cls.SUBNODE_TYPE)
        god_mata_nd.add_meta_node(newNode)
        name = "{}_METAND".format(str(newNode))
        name = strings.string_checkup(name, logger_=_LOGGER)
        newNode.rename(name)

        rigname_attr = {
            "name": constants.META_ROOT_RIG_NAME,
            "attrType": "string",
            "keyable": False,
            "value": "None",
        }

        l_rig_color_attr = {
            "name": constants.META_LEFT_RIG_COLOR,
            "attrType": "long",
            "keyable": False,
            "defaultValue": 13,
            "minValue": 0,
            "maxValue": 31,
        }

        l_rig_sub_color_attr = {
            "name": constants.META_LEFT_RIG_SUB_COLOR,
            "attrType": "long",
            "keyable": False,
            "defaultValue": 18,
            "minValue": 0,
            "maxValue": 31,
        }

        r_rig_color_attr = {
            "name": constants.META_RIGHT_RIG_COLOR,
            "attrType": "long",
            "keyable": False,
            "defaultValue": 6,
            "minValue": 0,
            "maxValue": 31,
        }

        r_rig_sub_color_attr = {
            "name": constants.META_RIGHT_RIG_SUB_COLOR,
            "attrType": "long",
            "keyable": False,
            "defaultValue": 9,
            "minValue": 0,
            "maxValue": 31,
        }

        m_rig_color_attr = {
            "name": constants.META_MID_RIG_COLOR,
            "attrType": "long",
            "keyable": False,
            "defaultValue": 17,
            "minValue": 0,
            "maxValue": 31,
        }

        m_rig_sub_color_attr = {
            "name": constants.META_MID_RIG_SUB_COLOR,
            "attrType": "long",
            "keyable": False,
            "defaultValue": 11,
            "minValue": 0,
            "maxValue": 31,
        }

        root_op_nd_attr = {
            "name": constants.ROOT_OP_MESSAGE_ATTR_NAME,
            "attrType": "message",
            "keyable": False,
            "channelBox": False,
        }

        root_node_param_list = [
            rigname_attr,
            l_rig_color_attr,
            l_rig_sub_color_attr,
            r_rig_color_attr,
            r_rig_sub_color_attr,
            m_rig_color_attr,
            m_rig_sub_color_attr,
            root_op_nd_attr,
        ]
        for attr_ in root_node_param_list:
            attributes.add_attr(node=newNode, **attr_)

    def add_main_meta_node(self, node):
        """
        Add a main meta node to the root meta node as message attr connection.

        Args:
                node(dagnode): The node to add.

        """
        new_attribute = {}
        dirty_plugs = []
        ud_attr = self.listAttr(ud=True)
        ud_attr = [str(attr_).split(".")[1] for attr_ in ud_attr]
        meta_plug = [
            attr_
            for attr_ in ud_attr
            if re.search(constants.MAIN_META_ND_PLUG, attr_)
        ]
        if not meta_plug:
            count = "0"
        else:
            for plug in meta_plug:
                if not self.attr(plug).get():
                    self.attr(plug).delete()
                else:
                    dirty_plugs.append(plug)
            integer = dirty_plugs[-1].split(
                "{}_".format(constants.MAIN_META_ND_PLUG)
            )[1]
            count = str(int(integer) + 1)
        new_attribute["name"] = "{}_{}".format(
            constants.MAIN_META_ND_PLUG, count
        )
        new_attribute["attrType"] = "message"
        new_attribute["keyable"] = False
        new_attribute["channelBox"] = False
        new_attribute["input"] = node.message
        attributes.add_attr(node=self, **new_attribute)

    def set_root_op_nd(self, root_op_node):
        """
        Connect meta node with root op node.

        Args:
            node(pmc.PyNode()): Root operator node.

        """
        root_op_node.message.connect(
            self.attr(constants.ROOT_OP_MESSAGE_ATTR_NAME)
        )


class MainOpMetaNode(MetaNode):
    """
    Creates a Meta Node as Main Operator Meta Node for a component.
    """

    SUBNODE_TYPE = constants.META_TYPE_B

    @classmethod
    def list(cls, *args, **kwargs):
        """ Returns all instances of all characters in the scene """

        kwargs["type"] = cls.__melnode__
        return [
            node for node in pmc.ls(*args, **kwargs) if isinstance(node, cls)
        ]

    @classmethod
    def _isVirtual(
        cls, obj, name, tag=constants.META_NODE_ID, type=constants.META_TYPE
    ):
        """
         This actual creates the node. If a specific tag is found.
         If not it will create a default node.
         PyMEL code should not be used inside the callback,
         only API and maya.cmds.
         Args:
                 obj(dagnode): The network node.
                 name(str): The nodes name.
                 tag(str): The specific creation tag.
                 type(str): The meta node type.
         Return:
                 True if node with tag exist / False if not or tag is disable.
         """
        fn = pmc.api.MFnDependencyNode(obj)
        try:
            if fn.hasAttribute(tag):
                plug = fn.findPlug(tag)
                if plug.asBool() == 1:
                    if fn.hasAttribute(type):
                        plug = fn.findPlug(type)
                        if plug.asString() == cls.SUBNODE_TYPE:
                            return True
                    return False
        except:
            pass
        return False

    @classmethod
    def _postCreateVirtual(
        cls,
        newNode,
        type=constants.META_TYPE,
        god_meta_name="god_meta_0_METAND",
        connection_types=constants.DEFAULT_CONNECTION_TYPES,
    ):
        """
        This is called after creation, pymel/cmds allowed.
        It will create a set of attributes. And the important check up tag for
        the meta node.
        Args:
                newNode(dagnode): The new node.
                tag(str): The specific creation tag.
                type(str): The meta node type.
                god_meta_name(str): The name of the god meta node.
        """
        MetaNode._postCreateVirtual(newNode)
        try:
            god_mata_nd = pmc.PyNode(god_meta_name)
        except:
            god_mata_nd = GodMetaNode()
        newNode.attr(type).set(cls.SUBNODE_TYPE)
        god_mata_nd.add_meta_node(newNode)
        name = "{}_METAND".format(str(newNode))
        name = strings.string_checkup(name, logger_=_LOGGER)
        newNode.rename(name)

        comp_name_attr = {
            "name": constants.META_MAIN_COMP_NAME,
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }

        comp_type_attr = {
            "name": constants.META_MAIN_COMP_TYPE,
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }

        comp_side_attr = {
            "name": constants.META_MAIN_COMP_SIDE,
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }

        comp_index_attr = {
            "name": constants.META_MAIN_COMP_INDEX,
            "attrType": "long",
            "keyable": False,
            "channelBox": False,
            "defaultValue": 0,
        }

        connection_type_attr = {
            "name": constants.META_DEFAULT_CONNECTION_TYPES,
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
            "value": constants.DEFAULT_CONNECTION_TYPES,
        }

        ik_spaces_ref_attr = {
            "name": constants.META_MAIN_IK_SPACES,
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }

        fk_spaces_ref_attr = {
            "name": constants.META_MAIN_FK_SPACES,
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }

        ik_pvec_spaces_ref_attr = {
            "name": constants.META_MAIN_IK_PVEC_SPACES,
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }

        main_operator_connection = {
            "name": constants.MAIN_OP_MESSAGE_ATTR_NAME,
            "attrType": "message",
            "keyable": False,
            "channelBox": False,
        }

        connect_nd_attr = {
            "name": constants.META_MAIN_CONNECT_ND,
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }

        rig_build_class_ref = {
            "name": constants.META_MAIN_RIG_BUILD_CLASS_REF,
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }

        parent_nd_attr = {
            "name": constants.META_MAIN_PARENT_ND,
            "attrType": "message",
            "keyable": False,
            "channelBox": False,
        }

        child_nd_attr = {
            "name": constants.META_MAIN_CHILD_ND,
            "attrType": "message",
            "keyable": False,
            "channelBox": False,
            "multi": True,
        }

        main_node_param_list = [
            comp_name_attr,
            comp_type_attr,
            comp_side_attr,
            comp_index_attr,
            connection_type_attr,
            ik_spaces_ref_attr,
            fk_spaces_ref_attr,
            ik_pvec_spaces_ref_attr,
            main_operator_connection,
            connect_nd_attr,
            rig_build_class_ref,
            parent_nd_attr,
            child_nd_attr,
        ]

        for attr_ in main_node_param_list:
            attributes.add_attr(node=newNode, **attr_)

    def add_sub_meta_node(self, node):
        """
        Add a sub meta node to the main meta node as message attr connection.
        Args:
                node(dagnode): The node to add.
        """
        new_attribute = {}
        ud_attr = self.listAttr(ud=True)
        ud_attr = [str(attr_).split(".")[1] for attr_ in ud_attr]
        meta_plug = [
            attr_
            for attr_ in ud_attr
            if re.search(constants.SUB_META_ND_PLUG, attr_)
        ]
        if not meta_plug:
            count = "0"
        else:
            count = str(int(meta_plug[-1][-1]) + 1)
        new_attribute["name"] = "{}_{}".format(
            constants.SUB_META_ND_PLUG, count
        )
        new_attribute["attrType"] = "message"
        new_attribute["keyable"] = False
        new_attribute["channelBox"] = False
        new_attribute["input"] = node.message
        attributes.add_attr(node=self, **new_attribute)

    def add_child_node(self, parent_node):
        """
        Add a node to the child node plug.

        Args:
            parent_node(pmc.PyNode()): Parent to add.

        """
        attributes.connect_next_available(
            parent_node,
            self,
            constants.META_MAIN_PARENT_ND,
            constants.META_MAIN_CHILD_ND,
        )


class SubOpMetaNode(MetaNode):
    """
    Creates a Meta Node as Sub Meta Node for a component..
    """

    SUBNODE_TYPE = constants.META_TYPE_C

    @classmethod
    def list(cls, *args, **kwargs):
        """ Returns all instances of all characters in the scene """

        kwargs["type"] = cls.__melnode__
        return [
            node for node in pmc.ls(*args, **kwargs) if isinstance(node, cls)
        ]

    @classmethod
    def _isVirtual(
        cls, obj, name, tag=constants.META_NODE_ID, type=constants.META_TYPE
    ):
        """
         This actual creates the node. If a specific tag is found.
         If not it will create a default node.
         PyMEL code should not be used inside the callback,
         only API and maya.cmds.
         Args:
                 obj(dagnode): The network node.
                 name(str): The nodes name.
                 tag(str): The specific creation tag.
                 type(str): The meta node type.
         Return:
                 True if node with tag exist / False if not or tag is disable.
         """
        fn = pmc.api.MFnDependencyNode(obj)
        try:
            if fn.hasAttribute(tag):
                plug = fn.findPlug(tag)
                if plug.asBool() == 1:
                    if fn.hasAttribute(type):
                        plug = fn.findPlug(type)
                        if plug.asString() == cls.SUBNODE_TYPE:
                            return True
                    return False
        except:
            pass
        return False

    @classmethod
    def _postCreateVirtual(
        cls,
        newNode,
        type=constants.META_TYPE,
        god_meta_name="god_meta_0_METAND",
    ):
        """
        This is called after creation, pymel/cmds allowed.
        It will create a set of attributes. And the important check up tag for
        the meta node.
        Args:
                newNode(dagnode): The new node.
                tag(str): The specific creation tag.
                type(str): The meta node type.
                god_meta_name(str): The name of the god meta node.
        """
        MetaNode._postCreateVirtual(newNode)
        try:
            god_mata_nd = pmc.PyNode(god_meta_name)
        except:
            god_mata_nd = GodMetaNode()
        newNode.attr(type).set(cls.SUBNODE_TYPE)
        god_mata_nd.add_meta_node(newNode)
        name = "{}_METAND".format(str(newNode))
        name = strings.string_checkup(name, logger_=_LOGGER)
        newNode.rename(name)

        connection_type_attr = {
            "name": constants.META_DEFAULT_CONNECTION_TYPES,
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
            "value": constants.DEFAULT_CONNECTION_TYPES,
        }

        sub_operator_connection = {
            "name": constants.SUB_OP_MESSAGE_ATTR_NAME,
            "attrType": "message",
            "keyable": False,
            "channelBox": False,
        }

        main_operator_connection = {
            "name": constants.MAIN_OP_MESSAGE_ATTR_NAME,
            "attrType": "message",
            "keyable": False,
            "channelBox": False,
        }

        sub_node_param_list = [
            connection_type_attr,
            sub_operator_connection,
            main_operator_connection,
        ]

        for attr_ in sub_node_param_list:
            attributes.add_attr(node=newNode, **attr_)

    def set_operator_nd(self, node):
        """
        Connect sub node with meta node.

        Args:
            node(pmc.PyNode()): The sub operator node.

        """
        node.message.connect(self.attr(constants.SUB_OP_MESSAGE_ATTR_NAME))

    def set_main_op_nd(self, main_op_nd):
        """
        Connect the main op node with the sub op meta node.

        main_op_nd(pmc:PyNode()): The main operator node.

        """
        main_op_nd.message.connect(
            self.attr(constants.MAIN_OP_MESSAGE_ATTR_NAME)
        )


pmc.factories.registerVirtualClass(MetaNode, nameRequired=False)
pmc.factories.registerVirtualClass(GodMetaNode, nameRequired=False)
pmc.factories.registerVirtualClass(RootOpMetaNode, nameRequired=False)
pmc.factories.registerVirtualClass(MainOpMetaNode, nameRequired=False)
pmc.factories.registerVirtualClass(SubOpMetaNode, nameRequired=False)
