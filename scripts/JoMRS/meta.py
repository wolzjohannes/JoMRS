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
# Date:       2019 / 08 / 21

"""
Meta node creation module.
"""
import pymel.all as pmc
import logging
import attributes
import re
import strings

##########################################################
# GLOBALS
#########################################################
module_logger = logging.getLogger(__name__ + ".py")
NODEID = "meta_node"
TYPE = "meta_class"
BASETYPE = "meta_node_class"
GODTYPE = "god_meta_class"
TYPEA = "root_operators_meta_class"
TYPEB = "main_operator_meta_class"
TYPEC = "sub_operator_meta_class"
DEFAULTCONNECTIONTYPES = "translate;rotate;scale"

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
    def _isVirtual(cls, obj, name, tag=NODEID):
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
        cls, newNode, tag=NODEID, type=TYPE, class_type=BASETYPE
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

    SUBNODE_TYPE = GODTYPE

    @classmethod
    def list(cls, *args, **kwargs):
        """ Returns all instances of all characters in the scene """

        kwargs["type"] = cls.__melnode__
        return [
            node for node in pmc.ls(*args, **kwargs) if isinstance(node, cls)
        ]

    @classmethod
    def _isVirtual(cls, obj, name, tag=NODEID, type=TYPE):
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
    def _postCreateVirtual(cls, newNode, type=TYPE, name="god_meta_0_METAND"):
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

    def add_meta_node(self, node, plug="meta_nd"):
        """
        Add a meta node to the god meta node as message attr connection.
        Args:
                node(dagnode): The node to add.
                plug(str): The attributes name for message connection.
        """
        new_attribute = {}
        ud_attr = self.listAttr(ud=True)
        ud_attr = [str(attr_).split(".")[1] for attr_ in ud_attr]
        meta_plug = [attr_ for attr_ in ud_attr if re.search(plug, attr_)]
        if not meta_plug:
            count = "0"
        else:
            count = str(int(meta_plug[-1][-1]) + 1)
        new_attribute["name"] = "{}_{}".format(plug, count)
        new_attribute["attrType"] = "message"
        new_attribute["keyable"] = False
        new_attribute["channelBox"] = False
        new_attribute["input"] = node.message
        attributes.add_attr(node=self, **new_attribute)

    def list_meta_nodes(self, plug="meta_nd", class_filter=None, type=TYPE):
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
        meta_plug = [
            attr_ for attr_ in ud_attr if re.search(plug, str(attr_))
        ]
        if meta_plug:
            result = [node.get() for node in meta_plug]
        if class_filter:
            result = [
                node
                for node in result
                if node.attr(type).get() == class_filter
            ]
        return result


class RootOpMetaNode(MetaNode):
    """
    Creates a Meta Node as Root Meta Node for all operators meta nodes.
    """

    SUBNODE_TYPE = TYPEA

    @classmethod
    def list(cls, *args, **kwargs):
        """ Returns all instances of all characters in the scene """

        kwargs["type"] = cls.__melnode__
        return [
            node for node in pmc.ls(*args, **kwargs) if isinstance(node, cls)
        ]

    @classmethod
    def _isVirtual(cls, obj, name, tag=NODEID, type=TYPE):
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
        cls, newNode, type=TYPE, god_meta_name="god_meta_0_METAND"
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
        name = strings.string_checkup(name, logger_=module_logger)
        newNode.rename(name)

        rigname_attr = {
            "name": "rig_name",
            "attrType": "string",
            "keyable": False,
        }

        l_ik_rig_color_attr = {
            "name": "l_ik_rig_color",
            "attrType": "long",
            "keyable": False,
            "defaultValue": 13,
            "minValue": 0,
            "maxValue": 31,
        }

        l_ik_rig_sub_color_attr = {
            "name": "l_ik_rig_sub_color",
            "attrType": "long",
            "keyable": False,
            "defaultValue": 18,
            "minValue": 0,
            "maxValue": 31,
        }

        r_ik_rig_color_attr = {
            "name": "r_ik_rig_color",
            "attrType": "long",
            "keyable": False,
            "defaultValue": 6,
            "minValue": 0,
            "maxValue": 31,
        }

        r_ik_rig_sub_color_attr = {
            "name": "r_ik_rig_sub_color",
            "attrType": "long",
            "keyable": False,
            "defaultValue": 9,
            "minValue": 0,
            "maxValue": 31,
        }

        m_ik_rig_color_attr = {
            "name": "m_ik_rig_color",
            "attrType": "long",
            "keyable": False,
            "defaultValue": 17,
            "minValue": 0,
            "maxValue": 31,
        }

        m_ik_rig_sub_color_attr = {
            "name": "m_ik_rig_sub_color",
            "attrType": "long",
            "keyable": False,
            "defaultValue": 11,
            "minValue": 0,
            "maxValue": 31,
        }

        root_node_param_list = [
            rigname_attr,
            l_ik_rig_color_attr,
            l_ik_rig_sub_color_attr,
            r_ik_rig_color_attr,
            r_ik_rig_sub_color_attr,
            m_ik_rig_color_attr,
            m_ik_rig_sub_color_attr,
        ]
        for attr_ in root_node_param_list:
            attributes.add_attr(node=newNode, **attr_)

    def add_main_meta_node(self, node, plug="main_meta_nd"):
        """
        Add a main meta node to the root meta node as message attr connection.
        Args:
                node(dagnode): The node to add.
                plug(str): The attributes name for message connection.
        """
        new_attribute = {}
        ud_attr = self.listAttr(ud=True)
        ud_attr = [str(attr_).split(".")[1] for attr_ in ud_attr]
        meta_plug = [attr_ for attr_ in ud_attr if re.search(plug, attr_)]
        if not meta_plug:
            count = "0"
        else:
            count = str(int(meta_plug[-1][-1]) + 1)
        new_attribute["name"] = "{}_{}".format(plug, count)
        new_attribute["attrType"] = "message"
        new_attribute["keyable"] = False
        new_attribute["channelBox"] = False
        new_attribute["input"] = node.message
        attributes.add_attr(node=self, **new_attribute)


class MainOpMetaNode(MetaNode):
    """
    Creates a Meta Node as Main Operator Meta Node for a component.
    """

    SUBNODE_TYPE = TYPEB

    @classmethod
    def list(cls, *args, **kwargs):
        """ Returns all instances of all characters in the scene """

        kwargs["type"] = cls.__melnode__
        return [
            node for node in pmc.ls(*args, **kwargs) if isinstance(node, cls)
        ]

    @classmethod
    def _isVirtual(cls, obj, name, tag=NODEID, type=TYPE):
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
        type=TYPE,
        god_meta_name="god_meta_0_METAND",
        connection_types=DEFAULTCONNECTIONTYPES,
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
        name = strings.string_checkup(name, logger_=module_logger)
        newNode.rename(name)

        comp_name_attr = {
            "name": "component_name",
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }

        comp_type_attr = {
            "name": "component_type",
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }

        comp_side_attr = {
            "name": "component_side",
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }

        comp_index_attr = {
            "name": "component_index",
            "attrType": "long",
            "keyable": False,
            "channelBox": False,
            "defaultValue": 0,
        }

        connection_type_attr = {
            "name": "connection_type",
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
            "value": connection_types,
        }

        ik_spaces_ref_attr = {
            "name": "ik_spaces_ref",
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }

        fk_spaces_ref_attr = {
            "name": "fk_spaces_ref",
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }

        ik_pvec_spaces_ref_attr = {
            "name": "ik_pvec_spaces_ref",
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
        }

        main_operator_connection = {
            "name": "main_operator_nd",
            "attrType": "message",
            "keyable": False,
            "channelBox": False,
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
        ]
        for attr_ in main_node_param_list:
            attributes.add_attr(node=newNode, **attr_)

    def add_sub_meta_node(self, node, plug="sub_meta_nd"):
        """
        Add a sub meta node to the main meta node as message attr connection.
        Args:
                node(dagnode): The node to add.
                plug(str): The attributes name for message connection.
        """
        new_attribute = {}
        ud_attr = self.listAttr(ud=True)
        ud_attr = [str(attr_).split(".")[1] for attr_ in ud_attr]
        meta_plug = [attr_ for attr_ in ud_attr if re.search(plug, attr_)]
        if not meta_plug:
            count = "0"
        else:
            count = str(int(meta_plug[-1][-1]) + 1)
        new_attribute["name"] = "{}_{}".format(plug, count)
        new_attribute["attrType"] = "message"
        new_attribute["keyable"] = False
        new_attribute["channelBox"] = False
        new_attribute["input"] = node.message
        attributes.add_attr(node=self, **new_attribute)


class SubOpMetaNode(MetaNode):
    """
    Creates a Meta Node as Sub Meta Node for a component..
    """

    SUBNODE_TYPE = TYPEC

    @classmethod
    def list(cls, *args, **kwargs):
        """ Returns all instances of all characters in the scene """

        kwargs["type"] = cls.__melnode__
        return [
            node for node in pmc.ls(*args, **kwargs) if isinstance(node, cls)
        ]

    @classmethod
    def _isVirtual(cls, obj, name, tag=NODEID, type=TYPE):
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
        type=TYPE,
        god_meta_name="god_meta_0_METAND",
        connection_types=DEFAULTCONNECTIONTYPES,
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
        name = strings.string_checkup(name, logger_=module_logger)
        newNode.rename(name)

        connection_type_attr = {
            "name": "connection_type",
            "attrType": "string",
            "keyable": False,
            "channelBox": False,
            "value": connection_types,
        }

        sub_operator_connection = {
            "name": "sub_operator_nd",
            "attrType": "message",
            "keyable": False,
            "channelBox": False,
        }

        sub_node_param_list = [connection_type_attr, sub_operator_connection]

        for attr_ in sub_node_param_list:
            attributes.add_attr(node=newNode, **attr_)


pmc.factories.registerVirtualClass(MetaNode, nameRequired=False)
pmc.factories.registerVirtualClass(GodMetaNode, nameRequired=False)
pmc.factories.registerVirtualClass(RootOpMetaNode, nameRequired=False)
pmc.factories.registerVirtualClass(MainOpMetaNode, nameRequired=False)
pmc.factories.registerVirtualClass(SubOpMetaNode, nameRequired=False)
