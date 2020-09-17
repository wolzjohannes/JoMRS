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
# Date:       2020 / 05 / 03

"""
JoMRS attributes module. Module for attributes handling.
"""
import logging
import pymel.core as pmc
import logger

##########################################################
# GLOBALS
##########################################################

_LOGGER = logging.getLogger(__name__ + ".py")

##########################################################
# FUNCTIONS
##########################################################


def undo(func_):
    def inner(*args, **kwargs):
        with pmc.UndoChunk():
            result = func_(*args, **kwargs)
            return result

    return inner


def add_attr(
    node,
    name,
    attrType,
    value=None,
    defaultValue=None,
    minValue=None,
    maxValue=None,
    keyable=True,
    hidden=False,
    writable=True,
    channelBox=True,
    lock=False,
    input=None,
    output=None,
    multi=False,
):
    """
    Add attribute to a node.
    Args:
            node(dagNode): The node to add the attribute.
            name(str): Longname of the attribute.
            attrType(str): The type of the attribute.
            value(float or int): The value of the attribute.
            defaultValue(float or int): The default value of the attribute.
            minValue(float or int): The minimal value of the attribute.
            maxValue(float or int): The maximum value of the attribute.
            keyable(bool): Defines if the attribute is keyable.
            hidden(bool): Defines if the attribute is hidden.
            writable(bool): Defines if the attribute can get input connections.
            channelBox(bool): Defines if the attribute is in the channelbox.
            lock(bool): Lock/Unlock the attribute.
            input(dagNode.attribute): Connects the attribute with the input.
            output(dagNode.attribute): Connects the attribute with the output.
            multi(bool): Define if attribute is a multi attribute.
    Return:
            str: The new created attributes name.

    """

    if node.hasAttr(name):
        logger.log(
            level="error",
            message=name + " attribute already exist",
            logger=_LOGGER,
        )
        return

    data_dic = {}

    if attrType == "string":
        data_dic["dataType"] = attrType
    else:
        data_dic["attributeType"] = attrType

    data_dic["keyable"] = keyable
    data_dic["hidden"] = hidden
    data_dic["writable"] = writable
    data_dic["multi"] = multi

    if minValue is not None:
        data_dic["minValue"] = minValue
    if maxValue is not None:
        data_dic["maxValue"] = maxValue
    if defaultValue is not None:
        data_dic["defaultValue"] = defaultValue

    node.addAttr(name, **data_dic)

    if not channelBox:
        node.attr(name).set(channelBox=False)
    if lock:
        node.attr(name).set(lock=True)
    if value:
        node.attr(name).set(value)
    if input:
        pmc.PyNode(input).connect(node.attr(name))
    if output:
        node.attr(name).connect(pmc.PyNode(output))

    return node.attr(name)


def add_array_attribute(
    node,
    name,
    plugs_name,
    values=None,
    keyable=True,
    hidden=False,
    writable=True,
    channelBox=True,
    lock=False,
):
    """
    Add a array attribute to the node.
    Args:
            node(dagNode): The node to add the attribute.
            name(str): Longname of the attribute.
            plugs_name(list with str): Longnames of the child attributes.
            value(list with float or int): The value of the child attributes.
            keyable(bool): Defines if the child attributes are keyable.
            hidden(bool): Defines if the attribute are hidden.
            writable(bool): Defines if the attribute can get input connections.
            channelBox(bool): Defines if the child attributes are
                              in the channelbox.
            lock(bool): Lock/Unlock the child attributes.
    Return:
            list: The attributes name and the names of the child attributes.
    """

    if node.hasAttr(name):
        logger.log(
            level="error",
            message=name + " attribute already exist",
            logger=_LOGGER,
        )
        return

    data_dic = {}

    data_dic["attributeType"] = "float3"

    data_dic["keyable"] = keyable
    data_dic["hidden"] = hidden
    data_dic["writable"] = writable

    data_childs_dic = {}

    data_childs_dic["attributeType"] = "float"
    data_childs_dic["parent"] = name

    node.addAttr(name, **data_dic)

    for plug in plugs_name:
        node.addAttr(plug, **data_childs_dic)
    if values:
        for x in range(len(values)):
            node.attr(plugs_name[x]).set(values[x])
    for plug_ in plugs_name:
        node.attr(plug_).set(lock=lock, keyable=keyable, channelBox=True)
        if not channelBox:
            node.attr(plug_).set(lock=lock, keyable=False, channelBox=False)

    result = [node.attr(name)]
    result.extend([node.attr(plug__) for plug__ in plugs_name])
    return result


def add_enum_attribute(
    node,
    name,
    enum,
    value=0,
    keyable=True,
    hidden=False,
    writable=True,
    channelBox=True,
    lock=False,
):
    """
    Add a enum attribute to the node.
    Args:
            node(dagNode): The node to add the attribute.
            name(str): Longname of the attribute.
            enum(list with str): Names of the enums.
            value(float or int): The value of the attribute.
            keyable(bool): Defines if the attribute is keyable.
            hidden(bool): Defines if the attribute are hidden.
            writable(bool): Defines if the attribute can get input connections.
            channelBox(bool): Defines if the attribute is in the channelbox.
            lock(bool): Lock/Unlock the attribute.

    Return:
            dic: A dic with the enum and their index.
                 Inclusive the attribute name.

    """

    if node.hasAttr(name):
        logger.log(
            level="error",
            message=name + " attribute already exist",
            logger=_LOGGER,
        )
        return

    enum_dic = {}
    data_dic = {}

    data_dic["attributeType"] = "enum"

    data_dic["en"] = ":".join(enum)
    data_dic["keyable"] = keyable
    data_dic["hidden"] = hidden
    data_dic["writable"] = writable

    node.addAttr(name, **data_dic)

    node.attr(name).set(value, lock=lock, keyable=keyable, channelBox=True)
    if not channelBox:
        node.attr(name).set(lock=lock, keyable=False, channelBox=False)

    for x in range(len(enum)):
        enum_dic["index_" + str(x)] = enum[x]

    enum_dic["attributeName"] = name

    return enum_dic


def add_separator_attr(node, name):
    """
    Function to add a separator attribute.
    Args:
            node(dagNode): The node to add the attribute.
            name(str): Longname of the attribute.
    """
    if name:
        add_enum_attribute(
            node=node, name=name, enum="#######", keyable=False, lock=True
        )
        return
    logger.log(
        level="error",
        message="no attributes name specified",
        logger=_LOGGER,
    )
    return


def lock_and_hide_attributes(node, lock=True, hide=True, attributes=None):
    """
    Lock and hide a attribute of the node.
    In Default it will lock and hide the default channels.
    Args:
            node(dagNode): The node the attribute belongs to.
            lock(bool): Lock/unlock the attribute.
            hide(bool): Hide/Unhide the attribute.
            attributes(list of str): The list with attributes to lock/hide
    Return:
            list: The locked attributes.
    """
    default_attr = ["tx", "ty", "tz", "ro", "rx", "ry", "rz", "sx", "sy", "sz"]
    result = []
    if attributes:
        if not isinstance(attributes, list):
            attributes = [attributes]
    else:
        attributes = default_attr
    for attr_ in attributes:
        node.attr(attr_).set(lock=lock)
        if hide:
            node.attr(attr_).set(keyable=False, channelBox=False)
        result.append(node.attr(attr_))
    return result


def set_non_keyable_attribute(node, keyable=None, attributes=None):
    """
    Set attribute of a node to nonkeyable.
    By default it sets the default channels unkeyable.
    Args:
            node(dagNode): The node the attribute belongs to.
            keyable(bool): Set the attribute keyable/nonkeyable.
            attributes(list of str): The attributes to set.
    Return:
            list: The keyable/nonkeyable attributes.
    """
    default_attr = [
        "tx",
        "ty",
        "tz",
        "ro",
        "rx",
        "ry",
        "rz",
        "sx",
        "sy",
        "sz",
        "visibility",
    ]
    result = []
    if attributes:
        if not isinstance(attributes, list):
            attributes = [attributes]
    else:
        attributes = default_attr
    for attr_ in attributes:
        node.attr(attr_).set(keyable=keyable)
        result.append(node.attr(attr_))
    return result


#####################################
# GETTERS AND CUSTOMS
#####################################


def get_usd_attributes(node, index=None):
    """
    Get the user defined attributes of a node.
    Args:
            node(dagNode): The node the attributes belongs to.
            index(bool): Set if you want a index for each
                         userdefined attribute.
    Return:
            list with dics: The attributes values as keys in a dic.
            Example:
                    [{'attrType': u'double',
                    'usd_attr': Attribute(u'null1.test_float'),
                    'index': 1, 'lock': False, 'defaultValue': 1.0,
                    'maxValue': 10.0, 'value': 0.0, 'minValue': 0.0,
                    'keyable': True, 'channelBox': False,
                    'output': [Attribute(u'null3.translateX')],
                    'input': [Attribute(u'null2.translateX')],
                    'hidden': False, 'enums': None}]
    """
    result = []
    usd_attr = node.listAttr(ud=True)
    for x in range(len(usd_attr)):
        attr_dic = {}
        attr_dic["usd_attr"] = usd_attr[x]
        attr_dic["attrType"] = usd_attr[x].get(typ=True)
        attr_dic["value"] = usd_attr[x].get()
        if attr_dic["attrType"] != "double" or attr_dic["attrType"] != "long":
            attr_dic["minValue"] = None
            attr_dic["maxValue"] = None
            attr_dic["defaultValue"] = None
        else:
            attr_dic["minValue"] = usd_attr[x].getMin()
            attr_dic["maxValue"] = usd_attr[x].getMax()
            attr_dic["defaultValue"] = pmc.addAttr(
                str(usd_attr[x]), query=True, dv=True
            )
        attr_dic["hidden"] = usd_attr[x].isHidden()
        attr_dic["keyable"] = usd_attr[x].isKeyable()
        attr_dic["channelBox"] = usd_attr[x].isInChannelBox()
        attr_dic["lock"] = usd_attr[x].isLocked()
        attr_dic["input"] = usd_attr[x].connections(s=True, d=False, p=True)
        attr_dic["output"] = usd_attr[x].connections(s=False, d=True, p=True)
        attr_dic["enums"] = None
        if attr_dic["attrType"] == "enum":
            attr_dic["enums"] = usd_attr[x].getEnums()
        if index:
            attr_dic["index"] = x
        result.append(attr_dic)
    return result


def re_arrange_usd_attributes_by_index(
    node, index_change=None, new_indexing=True, step_up=True, step_down=None
):
    """
    Rearrange the userdefined Attributes by index.
    By Default it moves the attribute up in the
    channelBox.
    Args:
            node(dagNode): The node the attributes belongs to.
            index_change(list): [oldIndex, newIndex].
            new_indexing(bool): New indexing of the attributes in the list.
            step_up(bool): newIndex = oldIndex + -1.
            step_down(bool): newIndex = oldIndex + 1.

    Return:
            list with dics: The rearranged attributes values as keys in a dic.
            Example:
                    [{'attrType': u'double',
                    'usdAttr': Attribute(u'null1.test_float'),
                    'index': 1, 'lock': False, 'defaultValue': 1.0,
                    'maxValue': 10.0, 'value': 0.0, 'minValue': 0.0,
                    'keyable': True, 'channelBox': False,
                    'output': [Attribute(u'null3.translateX')],
                    'input': [Attribute(u'null2.translateX')],
                    'hidden': False, 'enums': None}].
    """
    usd_attr = get_usd_attributes(node, index=True)
    op_value = 0
    if step_down:
        op_value = 1
        step_up = None
    if step_up:
        op_value = -1
        step_down = None
    if index_change:
        indexes = []
        for dic in usd_attr:
            indexes.append(dic["index"])
        if op_value:
            if index_change[0] + op_value >= 0:
                indexes.insert(
                    index_change[0] + op_value, indexes.pop(index_change[0])
                )
            else:
                logger.log(
                    level="error",
                    message="Negative newIndex not allowed",
                    func=re_arrange_usd_attributes_by_index,
                    logger=_LOGGER,
                )
                return
        else:
            indexes.insert(index_change[1], indexes.pop(index_change[0]))
        usd_attr = [usd_attr[x] for x in indexes]
    else:
        logger.log(
            level="error",
            message="You have to specifie the index_change",
            func=re_arrange_usd_attributes_by_index,
            logger=_LOGGER,
        )
    if new_indexing:
        for x in range(len(usd_attr)):
            usd_attr[x]["index"] = x
    return usd_attr


def re_arrange_usd_attributes_by_name(
    node, attribute_name=None, new_index=None, step_up=True, step_down=None
):
    """
    Rearrange a userdefined Attribute by name.
    By Default it moves the attribute up in the
    channelBox.
    Args:
            node(dagNode): The node the attributes belongs to.
            attribute_name(str): The name of the attribute.
            new_index(int): new position of the attribute.
            step_up(bool): new_index = oldIndex - 1.
            step_down(bool): new_index = oldIndex + 1.
    Return:
            list with dicts: The rearranged userdefined
            attributes.
    """
    usd_attr = get_usd_attributes(node=node, index=True)
    for x in range(len(usd_attr)):
        if usd_attr[x]["usdAttr"] == node.attr(attribute_name):
            old_index = usd_attr[x]["index"]
    if step_down:
        new_index = old_index + 1
        step_up = None
    if step_up:
        new_index = old_index - 1
        step_down = None
    index_change = [old_index, new_index]
    return re_arrange_usd_attributes_by_index(
        node=node, index_change=index_change, step_up=step_up, step_down=step_down
    )


@undo
def move_attribute_in_channel_box(
    node,
    attribute_name=None,
    exchange_attr_name=None,
    new_index=None,
    step_up=True,
    step_down=None,
):
    """
    Moves a selected user defined attribute in the channelBox
    by index or step by step.
    By Default it always takes the selected attribute in the
    channelBox and moves the attribute one step upwards.
    Args:
            node(dagNode): The node the attributes belongs to.
            attribute_name(str): The name of the attribute.
                                If None it takes the selected
                                attribute in the channelBox.
            exchange_attr_name(str): The name of the attribute
                                   to exchange with.
            new_index(int): new position of the attribute.
            step_up(bool): new_index = oldIndex - 1.
    """
    if not attribute_name:
        if len(pmc.channelBox("mainChannelBox", q=True, sma=True)) == 1:
            attribute_name = pmc.channelBox(
                "mainChannelBox", q=True, sma=True
            )[0]
        else:
            logger.log(
                level="error",
                message="more then one selection "
                "in the channelBox not supported",
                func=move_attribute_in_channel_box,
                logger=_LOGGER,
            )
            return
    if exchange_attr_name:
        step_up = None
        step_down = None
        usd_attr = get_usd_attributes(node=node, index=True)
        for attr_ in usd_attr:
            name = attr_["usd_attr"].split(".")[1]
            if name == exchange_attr_name:
                print attr_["usd_attr"]
                new_index = attr_["index"]
                print new_index
    usd_attr = re_arrange_usd_attributes_by_name(
        node=node,
        attribute_name=attribute_name,
        new_index=new_index,
        step_up=step_up,
        step_down=step_down,
    )

    def re_create_attr():
        """
        Executes the rebuild of the attributes.
        """
        if usd_attr:
            for x in usd_attr:
                x["usd_attr"].disconnect()
                x["usd_attr"].set(lock=False)
                x["usd_attr"].delete()
                if x["attrType"] == "string":
                    node.addAttr(
                        x["usd_attr"].split(".")[1],
                        dt=x["attrType"],
                        hidden=x["hidden"],
                        keyable=x["keyable"],
                        en=x["enums"],
                    )
                else:
                    node.addAttr(
                        x["usd_attr"].split(".")[1],
                        at=x["attrType"],
                        hidden=x["hidden"],
                        keyable=x["keyable"],
                        en=x["enums"],
                    )
                node.attr(x["usd_attr"].split(".")[1]).set(
                    x["value"],
                    lock=x["lock"],
                    keyable=x["keyable"],
                    channelBox=x["channelBox"],
                )
                if x["input"]:
                    x["input"][0].connect(x["usd_attr"])
                if x["output"]:
                    for out in x["output"]:
                        x["usd_attr"].connect(out)
            logger.log(
                level="info",
                message=attribute_name + " reordered in channelBox",
                logger=_LOGGER,
            )

    re_create_attr()


@undo
def transfer_attributes(
    source, target, output_connections=None, input_connections=None
):
    """
    Transfers the user defined attributes from a source object
    to a target object.
    By default its not recreating connections.
    Args:
            source(dagNode): The node with the source attributes.
            target(dagNode): The target node.
            output_connections(bool): Recreate output connections.
            input_connections(bool): Recreate input connections.
    Return:
            list with dicts: The user defined Attribute of the
            source object.
    """
    source_usd_attr = get_usd_attributes(node=source, index=True)
    if source_usd_attr:
        for attr_ in source_usd_attr:
            if attr_["attrType"] == "string":
                target.addAttr(
                    attr_["usdAttr"].split(".")[1],
                    dt=attr_["attrType"],
                    hidden=attr_["hidden"],
                    keyable=attr_["keyable"],
                    en=attr_["enums"],
                )
            else:
                target.addAttr(
                    attr_["usdAttr"].split(".")[1],
                    at=attr_["attrType"],
                    hidden=attr_["hidden"],
                    keyable=attr_["keyable"],
                    en=attr_["enums"],
                )
            target.attr(attr_["usdAttr"].split(".")[1]).set(
                attr_["value"],
                lock=attr_["lock"],
                keyable=attr_["keyable"],
                channelBox=attr_["channelBox"],
            )
            if input_connections:
                if attr_["input"]:
                    attr_["input"][0].connect(
                        pmc.PyNode(
                            str(attr_["usdAttr"]).replace(
                                str(source), str(target)
                            )
                        ),
                        force=True,
                    )
            if output_connections:
                if attr_["output"]:
                    for out in attr_["output"]:
                        pmc.PyNode(
                            str(attr_["usdAttr"]).replace(
                                str(source), str(target)
                            )
                        ).connect(out, force=True)
        logger.log(
            level="info",
            message="Attributes transfered from "
            + str(source)
            + " to "
            + str(target),
            logger=_LOGGER,
        )
        return source_usd_attr
    logger.log(
        level="error",
        message="No user defined attributes found for " + str(source),
        logger=_LOGGER,
    )
