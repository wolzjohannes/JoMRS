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
# Date:       2018 / 12 / 19

"""
JoMRS maya utils module. Utilities helps
to create maya behaviours.
"""

###############
# GLOBALS
# TO DO:
# config file for valid strings. For projects modifiactions
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


def constraint(typ='parent', source=None, target=None,
               maintainOffset=True, axes=['X', 'Y', 'Z']):
    """
    Create contraints. By default it creates a parentConstraint
    with maintain offset.
    Args:
            typ(str): The constraint type.
            source(dagnode): The source node.
            target(dagnode): The target node.
            maintainOffset(bool): If the constraint should keep
            the offset of the target.
            axes(list): The axes to contraint as strings.
    Return:
            list: The created constraint.
    """
    result = []
    skipAxes = ['x', 'y', 'z']
    if typ == 'parent':
        result = pmc.parentConstraint(source, target, mo=maintainOffset,
                                      skipRotate=skipAxes,
                                      skipTranslate=skipAxes)
        for ax in axes:
            result.attr('constraintTranslate' +
                        ax.upper()).connect(target.attr('translate' +
                                                        ax.upper()))
            result.attr('constraintRotate' +
                        ax.upper()).connect(target.attr('rotate' +
                                                        ax.upper()))
    if typ == 'point':
        result = pmc.pointConstraint(source, target, mo=maintainOffset,
                                     skip=skipAxes)
        for ax in axes:
            result.attr('constraintTranslate' +
                        ax.upper()).connect(target.attr('translate' +
                                                        ax.upper()))
    if typ == 'orient':
        result = pmc.orientConstraint(source, target, mo=maintainOffset,
                                      skip=skipAxes)
        for ax in axes:
            result.attr('constraintRotate' +
                        ax.upper()).connect(target.attr('rotate' +
                                                        ax.upper()))
    if typ == 'scale':
        result = pmc.scaleConstraint(source, target, mo=maintainOffset,
                                     skip=skipAxes)
        for ax in axes:
            result.attr('constraintScale' +
                        ax.upper()).connect(target.attr('scale' +
                                                        ax.upper()))
    return result


def constraint_UI_node_(constraint=None, source=None):
    """
    Create a contraint UI node to uncycle the constraint graph.
    Args:
            constraint(constraintNode): The constraint to work with.
            source(dagnode): The source node.
    Return:
            tuple: The created UI node.
    """
    attributes = ['translate', 'rotate', 'scale']
    axes = ['X', 'Y', 'Z']
    if source and constraint:
        if not isinstance(source, list):
            source = [source]
        constraint_UI = pmc.createNode('transform', n='{}{}'.format(
                                       str(constraint), '_UI_GRP'))
        constraint.addChild(constraint_UI)
        constraint_UI.visibility.set(lock=True,
                                     channelBox=False,
                                     keyable=False)
        for attr_ in attributes:
            for axe in axes:
                constraint_UI.attr(attr_ + axe).set(lock=True,
                                                    channelBox=False,
                                                    keyable=False)
        for x in range(len(source)):
            longName = '{}_{}'.format(str(source[x]), 'W' + str(x))
            constraint_UI.addAttr(longName, at='float', min=0, max=1, hxv=True,
                                  hnv=True, k=True)
            constraint_UI.attr(longName).set(1)
            constraint_UI.attr(longName).connect(
                constraint.target[x].targetWeight,
                force=True)
        for udAttr in constraint.listAttr(ud=True):
            pmc.deleteAttr(udAttr)
    else:
        logger.log(level='error',
                   message='source and constraint needed for'
                   ' constraint_UI_node', logger=moduleLogger)
    return constraint_UI


def no_pivots_no_rotateOrder_(constraint):
    """
    Disconnect the connections to the pivot plugs of a constraint.
    Args:
            constraint(PyNode): The specified constraint.
    """
    exceptions = []
    try:
        constraint.constraintRotatePivot.disconnect()
    except Exception as e:
        exceptions.append(e)
    try:
        constraint.constraintRotateTranslate.disconnect()
    except Exception as e:
        exceptions.append(e)
    try:
        constraint.constraintRotateOrder.disconnect()
    except Exception as e:
        exceptions.append(e)
    if exceptions:
        logger.log(level='warning', message=exceptions, logger=moduleLogger)


def no_constraint_cycle(constraint=None, source=None):
    """
    Disconnect the parentInverseMatrix connection from the constraint.
    And if the source node has a parent it plugs in the wolrdInverse Matrix
    plug of the parent.
    Args:
            constraint(constraintNode): The constraint to work with.
            source(dagnode): The source node.
    Return:
            tuple: The constraint UI node.
    """
    if not isinstance(source[0], list):
        source = [source]
    parent = source[0].getParent()
    if parent:
        constraint.constraintParentInverseMatrix.disconnect()
        parent.worldInverseMatrix.connect(constraint.
                                          constraintParentInverseMatrix)
    return constraint_UI_node_(constraint=constraint,
                               source=source)


def create_constraint(typ='parent', source=None, target=None,
                      maintainOffset=True, axes=['X', 'Y', 'Z'],
                      no_cycle=False, no_pivots=False, no_parent_influ=False):
    """
    Create constraints with a lot more functionality.
    By default it creates a parentConstraint.
    Args:
            typ(str): The constraint type.
            source(dagnode): The source node.
            target(dagnode): The target node.
            maintainOffset(bool): If the constraint should keep
            the offset of the target.
            axes(list): The axes to contraint as strings.
            no_cycle(bool): It creates a constraint_UI_node under
            the parent constraint. And disconnect inner cycle
            connections of the contraint.
            no_pivots(bool): Disconnect the pivot plugs.
            no_parent_influ(bool): Disconnect the constraintParentInverseMatrix
            plug. So that the parent transformation of the source node
            influnce the source node.
    Return:
            list: The constraint node, constraint_UI_node
    """
    result = []
    constraint_ = constraint(typ=typ, source=source, target=target,
                             maintainOffset=maintainOffset, axes=axes)
    result.append(constraint_)
    if no_cycle:
        con_UI_node = no_constraint_cycle(constraint=constraint_,
                                          source=source)
        result.append(con_UI_node)
    if no_pivots:
        no_pivots_no_rotateOrder_(constraint=constraint_)
    if no_parent_influ:
        constraint_.constraintParentInverseMatrix.disconnect()
    return result


def aimConstraint_(source=None, target=None, maintainOffset=True,
                   axes=['X', 'Y', 'Z'], aimAxes=[1, 0, 0],
                   upAxes=[0, 1, 0], worldUpType='object',
                   killUpVecObj=None, parentUpVecObj=None,
                   worldUpObject=None, worldUpVector=[0, 1, 0]):
    """
    Create a aimConstraint.
    By default it creates a object as upVector.
    Args:
            source(dagnode): The source node.
            target(dagnode): The target node.
            maintainOffset(bool): If the constraint should keep
            the offset of the target.
            axes(list): The axes to contraint as strings.
            aimAxes(list): The axes to aim for.
            ['x','y','z'] = [1,1,1]
            upAxes(list): The axes to the up vector.
            ['x','y','z'] = [1,1,1]
            worldUpType(string): The type for the up vector.
            Valid: none, scene, vector, object, objectrotation.
            killUpVecObj(bool): Kills the up vector transform.
            parentUpVecObj(dagnode): The parent for the up vector.
            worldUpObject(dagnode): The up vector transform node.
            worldUpVector(list): The axes for the world up vector.
            ['x','y','z'] = [1,1,1]

    Return:
            list: The aim constraint, the upVector locator node.
    """
    skipAxes = ['x', 'y', 'z']
    if worldUpType == 'object':
        worldUpObject = pmc.spaceLocator(n=str(source) + '_upVec_0_LOC')
        pmc.delete(pmc.parentConstraint(source, worldUpObject, mo=False))
        pmc.move(upAxes[0] * 5, upAxes[1] * 5, upAxes[2] * 5,
                 worldUpObject, ws=True)
        con = pmc.aimConstraint(target, source, mo=maintainOffset,
                                aim=aimAxes, skip=skipAxes, u=upAxes,
                                worldUpType=worldUpType,
                                worldUpObject=worldUpObject)
    elif worldUpType == 'objectrotation':
        con = pmc.aimConstraint(target, source, mo=maintainOffset,
                                aim=aimAxes, skip=skipAxes, u=upAxes,
                                worldUpType=worldUpType,
                                worldUpObject=worldUpObject)
    elif worldUpType == 'vector':
        con = pmc.aimConstraint(target, source, mo=maintainOffset,
                                aim=aimAxes, skip=skipAxes, u=upAxes,
                                worldUpType=worldUpType,
                                worldUpVector=worldUpVector)
    else:
        con = pmc.aimConstraint(target, source, mo=maintainOffset,
                                aim=aimAxes, skip=skipAxes, u=upAxes,
                                worldUpType=worldUpType)
    for ax in axes:
        con.attr('constraintRotate' +
                 ax.upper()).connect(source.attr('rotate' +
                                     ax.upper()))
    if killUpVecObj:
        pmc.delete(worldUpObject)
        return [con]
    if parentUpVecObj:
        pmc.parent(worldUpObject, parentUpVecObj)
    return [con, worldUpObject]


def create_aimConstraint(source=None, target=None, maintainOffset=True,
                         axes=['X', 'Y', 'Z'], aimAxes=[1, 0, 0],
                         upAxes=[0, 1, 0], worldUpType='object',
                         killUpVecObj=None, parentUpVecObj=None,
                         worldUpObject=None, worldUpVector=[0, 1, 0],
                         no_cycle=False, no_pivots=False,
                         no_parent_influ=False):
    """
    Create a aimConstraint with advanced options
    By default it creates a object as upVector.
    Args:
            source(dagnode): The source node.
            target(dagnode): The target node.
            maintainOffset(bool): If the constraint should keep
            the offset of the target.
            axes(list): The axes to contraint as strings.
            aimAxes(list): The axes to aim for.
            ['x','y','z'] = [1,1,1]
            upAxes(list): The axes to the up vector.
            ['x','y','z'] = [1,1,1]
            worldUpType(string): The type for the up vector.
            Valid: none, scene, vector, object, objectrotation.
            killUpVecObj(bool): Kills the up vector transform.
            parentUpVecObj(dagnode): The parent for the up vector.
            worldUpObject(dagnode): The up vector transform node.
            worldUpVector(list): The axes for the world up vector.
            ['x','y','z'] = [1,1,1]
            no_cycle(bool): It creates a constraint_UI_node under
            the constraint. And disconnect inner cycle connections
            of the contraint.
            no_pivots(bool): Disconnect the pivot plugs.
            no_parent_influ(bool): Disconnect the constraintParentInverseMatrix
            plug. So that the parent transformation of the source node
            influnce the source node.

    Return:
            list: The aim constraint, the upVector locator node,
            the constraint_UI_node.
    """
    result = aimConstraint_(source=source, target=target,
                            maintainOffset=maintainOffset,
                            axes=axes, aimAxes=aimAxes,
                            upAxes=upAxes, worldUpType=worldUpType,
                            killUpVecObj=killUpVecObj,
                            parentUpVecObj=parentUpVecObj,
                            worldUpObject=worldUpObject,
                            worldUpVector=worldUpVector)
    if no_cycle:
        con_UI_node = no_constraint_cycle(constraint=result[0], source=source)
        result.append(con_UI_node)
    if no_pivots:
        no_pivots_no_rotateOrder_(constraint=result[0])
    if no_parent_influ:
        result[0].constraintParentInverseMatrix.disconnect()
    return result
