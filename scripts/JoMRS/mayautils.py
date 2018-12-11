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
# Date:       2018 / 12 / 11

"""
JoMRS maya utils module. Utilities helps
to create maya behaviours.
"""

###############
# GLOBALS
## TO DO:
## config file for valid strings. For projects modifiactions
###############
import pymel.core as pmc
import attributes
import strings
import logging
import logger

moduleLogger = logging.getLogger(__name__ + '.py')


def create_bufferGRP(node):
    """
    Create a buffer transform for transform node and parent
    the node under buffer group.
    If the node already has parent. It will parent the node
    under the buffer and the buffer under the parent.
    Args:
            node(dagnode): A transform node.
    Return:
            tuple: The created buffer dagnode.
    """
    parent = node.getParent()
    name = strings.string_checkup(str(node) + '_buffer_GRP', moduleLogger)
    bufferGRP = pmc.createNode('transform', n=name)
    pmc.delete(pmc.parentConstraint(node, bufferGRP, mo=False))
    bufferGRP.addChild(node)
    if parent:
        parent.addChild(bufferGRP)
    return bufferGRP


def create_splineIK(name, startJNT=None, endJNT=None, parent=None,
                    curveParent=None, curve=None, snap=True,
                    sticky=False, weight=1, poWeight=1):
    """
    Create a splineIK.
    Args:
            name(str): The spline IK name. You should follow the
            JoMRS naming convention. If not it will throw some
            warnings.
            startJNT(dagNode): The start joint of the chain.
            endJNT(dagNode): The end joint of the chain.
            parent(dagNode): The parent for the IK_handle.
            snap(bool): Enable/Disalbe snap option of the IK.
            sticky(bool): Enable/Disalbe stickieness option of the IK.
            weight(float): Set handle weight.
            poWeight(float): Set the poleVector weight.
    Return:
            list(dagnodes): the ik Handle, the effector,
            the spline ik curve shape.
    """
    result = []
    data = {}
    name = strings.string_checkup(name, moduleLogger)
    data['n'] = name
    data['solver'] = 'ikSplineSolver'
    data['createCurve'] = False
    data['sj'] = startJNT
    data['ee'] = endJNT
    if curve is not None:
        data['c'] = curve
    else:
        data['createCurve'] = True
    ikHandle = pmc.ikHandle(**data)
    pmc.rename(ikHandle[1], str(endJNT) + '_EFF')
    result.extend(ikHandle)
    if curve:
        pmc.rename(curve, str(curve) + '_CRV')
        shape = curve.getShape()
        result.append(shape)
    else:
        pmc.rename(ikHandle[2], str(ikHandle[2] + '_CRV'))
        shape = pmc.PyNode(ikHandle[2]).getShape()
        result[2] = shape
    if parent:
        parent.addChild(result[0])
    if curveParent:
        curveParent.addChild(result[2].getParent())
    result[2].getParent().visibility.set(0)
    attributes.lockAndHideAttributes(result[2].getParent())
    result[0].visibility.set(0)
    if snap is False:
        result[0].snapEnable.set(0)
    if sticky:
        result[0].stickiness.set(1)
    result[0].attr('weight').set(weight)
    result[0].attr('poWeight').set(poWeight)
    logger.log(level='info', message='Spline IK "' + name + '" created',
               logger=moduleLogger)
    return result


def create_IK(name, solver='ikSCsolver', startJNT=None, endJNT=None,
              parent=None, snap=True, sticky=False,
              weight=1, poWeight=1):
    """
    Create a IK. Default is a single chain IK.
    Args:
            name(str): The spline IK name. You should follow
            name(str): The IK name. You should follow
            the JoMRS naming convention. If not it will throw some
            warnings.
            solver(str): The solver of the IK.
            startJNT(dagNode): The start joint of the chain.
            endJNT(dagNode): The end joint of the chain.
            parent(dagNode): The parent for the IK_handle.
            snap(bool): Enable/Disalbe snap option of the IK.
            sticky(bool): Enable/Disalbe stickieness option of the IK.
            weight(float): Set handle weight.
            poWeight(float): Set the poleVector weight.
    Return:
            list(dagnodes): the ik Handle, the effector,
            the spline ik curve shape.
    """
    data = {}
    name = strings.string_checkup(name, moduleLogger)
    data['n'] = name
    data['solver'] = solver
    data['sj'] = startJNT
    data['ee'] = endJNT
    ikHandle = pmc.ikHandle(**data)
    pmc.rename(ikHandle[1], str(endJNT) + '_EFF')
    if parent:
        parent.addChild(ikHandle[0])
    ikHandle[0].visibility.set(0)
    if snap is False:
        ikHandle[0].snapEnable.set(0)
    if sticky:
        ikHandle[0].stickiness.set(1)
    ikHandle[0].attr('weight').set(weight)
    ikHandle[0].attr('poWeight').set(poWeight)
    logger.log(level='info', message=solver + ' "' + name + '" created',
               logger=moduleLogger)
    return ikHandle
