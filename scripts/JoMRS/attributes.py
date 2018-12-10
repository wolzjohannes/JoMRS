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
# Date:       2018 / 12 / 09

"""
JoMRS attributes module. Module for attributes handling.
"""
import logging
import pymel.core as pmc
import logger

moduleLogger = logging.getLogger(__name__ + '.py')


def undo(func_):
    def inner(*args, **kwargs):
        with pmc.UndoChunk():
            result = func_(*args, **kwargs)
            return result
    return inner

#####################################
# SETTERS AND ADD
#####################################


def addAttr(node, name, attrType, value=None, defaultValue=None,
            minValue=None, maxValue=None, keyable=True,
            hidden=False, writable=True, channelBox=True,
            lock=False, input=None, output=None):
    """
    Add attribute to a node.
    Args:
            node(dagNode): The node to add the attribute.
            name(str): Longname of the atribute.
            attrType(str): The type of the attribute.
            value(float or int): The value of the attribute.
            defaultValue(float or int): The default value of the attribute.
            minValue(float or int): The minimal value of the attribute.
            maxValue(float or int): The maximum value of the attribute.
            keyable(bool): Defines if the attribute is keyable.
            hidden(bool): Defines if the attribute is hidden.
            writable(bool): Defines if the attribute can get input connections.
            channelBox(bool): Defines if the attribute is in the channelbox.
            lock(bool): Lock/Unlock the atttibute.
            input(dagNode.attribute): Connects the attribute with the input.
            output(dagNode.attribute): Connects the attribute with the output.
    Return:
            str: The new created attributes name.

    """

    if node.hasAttr(name):
        logger.log(level='error', message=name +
                   ' attribute already exist', logger=moduleLogger)
        return

    dataDic = {}

    if attrType == 'string':
        dataDic['dataType'] = attrType
    else:
        dataDic['attributeType'] = attrType

    dataDic['keyable'] = keyable
    dataDic['hidden'] = hidden
    dataDic['writable'] = writable

    if minValue is not None:
        dataDic['minValue'] = minValue
    if maxValue is not None:
        dataDic['maxValue'] = maxValue
    if defaultValue is not None:
        dataDic['defaultValue'] = defaultValue

    node.addAttr(name, **dataDic)

    if not channelBox:
        node.attr(name).set(channelBox=False)
    if lock:
        node.attr(name).set(lock=True)
    if value:
        node.attr(value).set(value)
    if input:
        pmc.PyNode(input).connect(node.attr(name))
    if output:
        node.attr(name).connect(pmc.PyNode(output))

    return node.attr(name)


def addArrayAttribute(node, name, plugsName, values=None, keyable=True,
                      hidden=False, writable=True, channelBox=True,
                      lock=False):
    """
    Add a array attribute to the node.
    Args:
            node(dagNode): The node to add the attribute.
            name(str): Longname of the attribute.
            plugsName(list with str): Longnames of the child attributes.
            value(list with float or int): The value of the child attributes.
            keyable(bool): Defines if the child attributes are keyable.
            hidden(bool): Defines if the attribute are hidden.
            writable(bool): Defines if the attribute can get input connections.
            channelBox(bool): Defines if the child attributes are
                              in the channelbox.
            lock(bool): Lock/Unlock the child atttibutes.
    Return:
            list: The attributes name and the names of the child attributes.
    """

    if node.hasAttr(name):
        logger.log(level='error', message=name +
                   ' attribute already exist', logger=moduleLogger)
        return

    dataDic = {}

    dataDic['attributeType'] = 'float3'

    dataDic['keyable'] = keyable
    dataDic['hidden'] = hidden
    dataDic['writable'] = writable

    dataChildsDic = {}

    dataChildsDic['attributeType'] = 'float'
    dataChildsDic['parent'] = name

    node.addAttr(name, **dataDic)

    for plug in plugsName:
        node.addAttr(plug, **dataChildsDic)
    if values:
        for x in range(len(values)):
            node.attr(plugsName[x]).set(values[x])
    for plug_ in plugsName:
        node.attr(plug_).set(lock=lock, keyable=keyable, channelBox=True)
        if not channelBox:
            node.attr(plug_).set(lock=lock, keyable=False, channelBox=False)

    result = [node.attr(name)]
    result.extend([node.attr(plug__) for plug__ in plugsName])
    return result


def addEnumAttribute(node, name, enum, value=0, keyable=True,
                     hidden=False, writable=True, channelBox=True, lock=False):
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
            lock(bool): Lock/Unlock the atttibute.

    Return:
            dic: A dic with the enum and their index.
                 Inclusive the attribute name.

    """

    if node.hasAttr(name):
        logger.log(level='error', message=name +
                   ' attribute already exist', logger=moduleLogger)
        return

    enumDic = {}
    dataDic = {}

    dataDic['attributeType'] = 'enum'

    dataDic['en'] = ':'.join(enum)
    dataDic['keyable'] = keyable
    dataDic['hidden'] = hidden
    dataDic['writable'] = writable

    node.addAttr(name, **dataDic)

    node.attr(name).set(lock=lock, keyable=keyable,
                        channelBox=True, value=value)
    if not channelBox:
        node.attr(name).set(lock=lock, keyable=False, channelBox=False)

    for x in range(len(enum)):
        enumDic['index_' + str(x)] = enum[x]

    enumDic['attributeName'] = name

    return enumDic


def addSeparatorAttr(node, name):
    """
    Function to add a separator attribute.
    Args:
            node(dagNode): The node to add the attribute.
            name(str): Longname of the attribute.
    """
    if name:
        addEnumAttribute(node=node, name=name, enum='#######',
                         keyable=False, lock=True)
        return
    logger.log(level='error', message='no attributes name specified',
               logger=moduleLogger)
    return


def lockAndHideAttributes(node, lock=True, hide=True, attributes=None):
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
    defaultAttr = ["tx", "ty", "tz", "ro", "rx", "ry", "rz",
                   "sx", "sy", "sz", "visibility"]
    result = []
    if attributes:
        if not isinstance(attributes, list):
            attributes = [attributes]
    else:
        attributes = defaultAttr
    for attr_ in attributes:
        node.attr(attr_).set(lock=lock)
        if hide:
            node.attr(attr_).set(keyable=False, channelBox=False)
        result.append(node.attr(attr_))
    return result


def setNonKeyableAttribute(node, keyable=None, attributes=None):
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
    defaultAttr = ["tx", "ty", "tz", "ro", "rx", "ry", "rz",
                   "sx", "sy", "sz", "visibility"]
    result = []
    if attributes:
        if not isinstance(attributes, list):
            attributes = [attributes]
    else:
        attributes = defaultAttr
    for attr_ in attributes:
        node.attr(attr_).set(keyable=keyable)
        result.append(node.attr(attr_))
    return result

#####################################
# GETTERS AND CUSTOMS
#####################################


def getUsdAttributes(node, index=None):
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
                    'usdAttr': Attribute(u'null1.test_float'),
                    'index': 1, 'lock': False, 'defaultValue': 1.0,
                    'maxValue': 10.0, 'value': 0.0, 'minValue': 0.0,
                    'keyable': True, 'channelBox': False,
                    'output': [Attribute(u'null3.translateX')],
                    'input': [Attribute(u'null2.translateX')],
                    'hidden': False, 'enums': None}]
    """
    result = []
    usdAttr = node.listAttr(ud=True)
    for x in range(len(usdAttr)):
        attrDic = {}
        attrDic['usdAttr'] = usdAttr[x]
        attrDic['attrType'] = usdAttr[x].get(typ=True)
        attrDic['value'] = usdAttr[x].get()
        if attrDic['attrType'] != 'double' or attrDic['attrType'] != 'long':
            attrDic['minValue'] = None
            attrDic['maxValue'] = None
            attrDic['defaultValue'] = None
        else:
            attrDic['minValue'] = usdAttr[x].getMin()
            attrDic['maxValue'] = usdAttr[x].getMax()
            attrDic['defaultValue'] = pmc.addAttr(str(usdAttr[x]),
                                                  query=True, dv=True)
        attrDic['hidden'] = usdAttr[x].isHidden()
        attrDic['keyable'] = usdAttr[x].isKeyable()
        attrDic['channelBox'] = usdAttr[x].isInChannelBox()
        attrDic['lock'] = usdAttr[x].isLocked()
        attrDic['input'] = usdAttr[x].connections(s=True, d=False, p=True)
        attrDic['output'] = usdAttr[x].connections(s=False, d=True, p=True)
        attrDic['enums'] = None
        if attrDic['attrType'] == 'enum':
            attrDic['enums'] = usdAttr[x].getEnums()
        if index:
            attrDic['index'] = x
        result.append(attrDic)
    return result


def reArrangeUsdAttributesByIndex(node, indexChange=None,
                                  newIndexing=True, stepUp=True,
                                  stepDown=None):
    """
    Rearrange the userdefined Attributes by index.
    By Default it moves the attribute up in the
    channelBox.
    Args:
            node(dagNode): The node the attributes belongs to.
            indexChange(list): [oldIndex, newIndex].
            newIndexing(bool): New indexing of the attributes in the list.
            stepUp(bool): newIndex = oldIndex + -1.
            stepDown(bool): newIndex = oldIndex + 1.

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
    usdAttr = getUsdAttributes(node, index=True)
    opValue = 0
    if stepDown:
        opValue = 1
        stepUp = None
    if stepUp:
        opValue = -1
        stepDown = None
    if indexChange:
        indexes = []
        for dic in usdAttr:
            indexes.append(dic['index'])
        if opValue:
            if indexChange[0] + opValue >= 0:
                indexes.insert(indexChange[0] + opValue,
                               indexes.pop(indexChange[0]))
            else:
                logger.log(level='error',
                           message='Negative newIndex not allowed',
                           func=reArrangeUsdAttributesByIndex,
                           logger=moduleLogger)
                return
        else:
            indexes.insert(indexChange[1], indexes.pop(indexChange[0]))
        usdAttr = [usdAttr[x] for x in indexes]
    else:
        logger.log(level='error',
                   message='You have to specifie the indexChange',
                   func=reArrangeUsdAttributesByIndex,
                   logger=moduleLogger)
    if newIndexing:
        for x in range(len(usdAttr)):
            usdAttr[x]['index'] = x
    return usdAttr


def reArrangeUsdAttributesByName(node, attributeName=None,
                                 newIndex=None, stepUp=True,
                                 stepDown=None):
    """
    Rearrange a userdefined Attribute by name.
    By Default it moves the attribute up in the
    channelBox.
    Args:
            node(dagNode): The node the attributes belongs to.
            attributeName(str): The name of the attribute.
            newIndex(int): new position of the attibute.
            stepUp(bool): newIndex = oldIndex - 1.
            stepDown(bool): newIndex = oldIndex + 1.
    Return:
            list with dicts: The rearranged userdefined
            attributes.
    """
    usdAttr = getUsdAttributes(node=node, index=True)
    for x in range(len(usdAttr)):
        if usdAttr[x]['usdAttr'] == node.attr(attributeName):
            oldIndex = usdAttr[x]['index']
    if stepDown:
        newIndex = oldIndex + 1
        stepUp = None
    if stepUp:
        newIndex = oldIndex - 1
        stepDown = None
    indexChange = [oldIndex, newIndex]
    return reArrangeUsdAttributesByIndex(node=node, indexChange=indexChange,
                                         stepUp=stepUp, stepDown=stepDown)


@undo
def moveAttributeInChannelBox(node, attributeName=None,
                              exchangeAttrName=None,
                              newIndex=None,
                              stepUp=True,
                              stepDown=None):
    """
    Moves a selected user defined attribute in the channelBox
    by index or step by step.
    By Default it always takes the selected attribute in the
    channelBox and moves the attribute one step upwards.
    Args:
            node(dagNode): The node the attributes belongs to.
            attributeName(str): The name of the attribute.
                                If None it takes the selected
                                attribute in the channelBox.
            exchangeAttrName(str): The name of the attribute
                                   to exchange with.
            newIndex(int): new position of the attibute.
            stepUp(bool): newIndex = oldIndex - 1.
    """
    if not attributeName:
        if len(pmc.channelBox('mainChannelBox', q=True, sma=True)) == 1:
            attributeName = pmc.channelBox('mainChannelBox',
                                           q=True, sma=True)[0]
        else:
            logger.log(level='error',
                       message='more then one selection '
                               'in the channelBox not supported',
                       func=moveAttributeInChannelBox,
                       logger=moduleLogger)
            return
    if exchangeAttrName:
        stepUp = None
        stepDown = None
        usdAttr = getUsdAttributes(node=node, index=True)
        for attr_ in usdAttr:
            name = attr_['usdAttr'].split('.')[1]
            if name == exchangeAttrName:
                print attr_['usdAttr']
                newIndex = attr_['index']
                print newIndex
    usdAttr = reArrangeUsdAttributesByName(node=node,
                                           attributeName=attributeName,
                                           newIndex=newIndex,
                                           stepUp=stepUp,
                                           stepDown=stepDown)

    def reCreateAttr():
        """
        Executes the rebuild of the attributes.
        """
        if usdAttr:
            for x in usdAttr:
                x['usdAttr'].disconnect()
                x['usdAttr'].set(lock=False)
                x['usdAttr'].delete()
                if x['attrType'] == 'string':
                    node.addAttr(x['usdAttr'].split('.')[1],
                                 dt=x['attrType'], hidden=x['hidden'],
                                 keyable=x['keyable'], en=x['enums'])
                else:
                    node.addAttr(x['usdAttr'].split('.')[1],
                                 at=x['attrType'], hidden=x['hidden'],
                                 keyable=x['keyable'], en=x['enums'])
                node.attr(x['usdAttr']
                          .split('.')[1]).set(x['value'], lock=x['lock'],
                                              keyable=x['keyable'],
                                              channelBox=x['channelBox'])
                if x['input']:
                    x['input'][0].connect(x['usdAttr'])
                if x['output']:
                    for out in x['output']:
                        x['usdAttr'].connect(out)
            logger.log(level='info',
                       message=attributeName + ' reordered in channelBox',
                       logger=moduleLogger)
    reCreateAttr()


@undo
def transferAttributes(source, target, outputConnections=None,
                       inputConnections=None):
    """
    Transfers the userdefined attributes from a source object
    to a target object.
    By default its not recreating connections.
    Args:
            source(dagNode): The node with the source attributes.
            target(dagNode): The target node.
            outputConnections(bool): Recreate output connections.
            inputConnections(bool): Recreate input connections.
    Return:
            list with dicts: The userdefined Attribute of the
            source object.
    """
    sourceUsdAttr = getUsdAttributes(node=source, index=True)
    if sourceUsdAttr:
        for attr_ in sourceUsdAttr:
            if attr_['attrType'] == 'string':
                target.addAttr(attr_['usdAttr'].split('.')[1],
                               dt=attr_['attrType'], hidden=attr_['hidden'],
                               keyable=attr_['keyable'], en=attr_['enums'])
            else:
                target.addAttr(attr_['usdAttr'].split('.')[1],
                               at=attr_['attrType'], hidden=attr_['hidden'],
                               keyable=attr_['keyable'], en=attr_['enums'])
            target.attr(attr_['usdAttr'].split('.')[1]).set(attr_['value'],
                                                            lock=attr_['lock'],
                                                            keyable=attr_
                                                            ['keyable'],
                                                            channelBox=attr_
                                                            ['channelBox'])
            if inputConnections:
                if attr_['input']:
                    attr_['input'][0].connect(pmc.PyNode(str(attr_['usdAttr'])
                                              .replace(str(source),
                                              str(target))), force=True)
            if outputConnections:
                if attr_['output']:
                    for out in attr_['output']:
                        pmc.PyNode(str(attr_['usdAttr']).replace(str(source),
                                   str(target))).connect(out, force=True)
        logger.log(level='info',
                   message='Attributes transfered from ' + str(source) +
                   ' to ' + str(target), logger=moduleLogger)
        return sourceUsdAttr
    logger.log(level='error',
               message='No user defined attributes found for ' +
               str(source), logger=moduleLogger)
