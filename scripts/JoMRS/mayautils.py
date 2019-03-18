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
# Date:       2018 / 12 / 30

"""
JoMRS maya utils module. Utilities helps
to create maya behaviours.
"""
# GLOBALS
###############
# TO DO:
# config file for valid strings. For projects modifications
# check if all srings follow the JoMRS string handling
###############
import pymel.core as pmc
import pymel.core.datatypes as dt
import attributes
import strings
import logging
import logger

moduleLogger = logging.getLogger(__name__ + '.py')


def create_bufferGRP(node, name=None):
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
    if name:
        name = strings.string_checkup(name + '_buffer_GRP', moduleLogger)
    else:
        name = strings.string_checkup(str(node) + '_buffer_GRP', moduleLogger)
    bufferGRP = pmc.createNode('transform', n=name)
    pmc.delete(pmc.parentConstraint(node, bufferGRP, mo=False))
    bufferGRP.addChild(node)
    if parent:
        parent.addChild(bufferGRP)
    return bufferGRP


def spaceLocator_onPosition(node, bufferGRP=True):
    """
    Create a spaceLocator on the position of a node.
    Args:
            node(dagnode): The match transform node.
            bufferGRP(bool): Create a buffer group for the locator.
    Return:
            list: The buffer group, the locator node.
    """
    result = []
    name = strings.string_checkup(str(node) + '_0_LOC', moduleLogger)
    loc = pmc.spaceLocator(n=name)
    pmc.delete(pmc.parentConstraint(node, loc, mo=False))
    result.append(loc)
    if bufferGRP:
        bufferGRP = create_bufferGRP(loc)
        result.insert(0, bufferGRP)
    return result


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
        result = pmc.parentConstraint(target, source, mo=maintainOffset,
                                      skipRotate=skipAxes,
                                      skipTranslate=skipAxes)
        for ax in axes:
            result.attr('constraintTranslate' +
                        ax.upper()).connect(source.attr('translate' +
                                                        ax.upper()))
            result.attr('constraintRotate' +
                        ax.upper()).connect(source.attr('rotate' +
                                                        ax.upper()))
    if typ == 'point':
        result = pmc.pointConstraint(target, source, mo=maintainOffset,
                                     skip=skipAxes)
        for ax in axes:
            result.attr('constraintTranslate' +
                        ax.upper()).connect(source.attr('translate' +
                                                        ax.upper()))
    if typ == 'orient':
        result = pmc.orientConstraint(target, source, mo=maintainOffset,
                                      skip=skipAxes)
        for ax in axes:
            result.attr('constraintRotate' +
                        ax.upper()).connect(source.attr('rotate' +
                                                        ax.upper()))
    if typ == 'scale':
        result = pmc.scaleConstraint(target, source, mo=maintainOffset,
                                     skip=skipAxes)
        for ax in axes:
            result.attr('constraintScale' +
                        ax.upper()).connect(source.attr('scale' +
                                                        ax.upper()))
    return result


def constraint_UI_node_(constraint=None, target=None):
    """
    Create a contraint UI node to uncycle the constraint graph.
    Args:
            constraint(constraintNode): The constraint to work with.
            target(dagnode): The target node.
    Return:
            tuple: The created UI node.
    """
    if target and constraint:
        if not isinstance(target, list):
            target = [target]
        constraint_UI = pmc.createNode('transform', n='{}{}'.format(
                                       str(constraint), '_UI_GRP'))
        constraint.addChild(constraint_UI)
        attributes.lockAndHideAttributes(node=constraint_UI)
        for x in range(len(target)):
            longName = '{}_{}'.format(str(target[x]), 'W' + str(x))
            attributes.addAttr(node=constraint_UI, name=longName,
                               attrType='float', minValue=0,
                               maxValue=1, keyable=True)
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


def no_constraint_cycle(constraint=None, source=None, target=None):
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
    return constraint_UI_node_(constraint=constraint, target=target)


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
                                          source=source,
                                          target=target)
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
    temp = []
    if worldUpType == 'object':
        if not worldUpObject:
            worldUpObject = pmc.spaceLocator(n=str(source) + '_upVec_0_LOC')
            worldUpObjectBuffer = pmc.group(worldUpObject,
                                            n=str(worldUpObject) +
                                            '_buffer_GRP')
            temp.append(worldUpObjectBuffer)
            pmc.delete(pmc.parentConstraint(source, worldUpObjectBuffer,
                                            mo=False))
            worldUpObject.translate.set(v * 5 for v in upAxes)
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
    temp.append(worldUpObject)
    if killUpVecObj:
        pmc.delete(temp)
        return [con]
    if parentUpVecObj:
        pmc.parent(temp[0], parentUpVecObj)
    return [con, temp[:]]


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
        con_UI_node = no_constraint_cycle(constraint=result[0], target=target,
                                          source=source)
        result.append(con_UI_node)
    if no_pivots:
        no_pivots_no_rotateOrder_(constraint=result[0])
    if no_parent_influ:
        result[0].constraintParentInverseMatrix.disconnect()
    return result


def decompose_matrix_constraint(source, target, translation=True,
                                rotation=True, scale=True):
    """
    Create decompose matrix constraint.
    Args:
            source(dagnode): The source node.
            target(dagnode): The target node.
            translation(bool): Envelope to connect the translation.
            rotation(bool): Envelope to connect the rotation.
            scale(bool): Envelope to connect the scale.
    Return:
            tuple: Created decompose matrix node.
    """
    decomp = pmc.createNode('decomposeMatrix', n=str(source) +
                            '_0_DEMAND')
    target.worldMatrix[0].connect(decomp.inputMatrix)
    if translation:
        decomp.outputTranslate.connect(source.translate, force=True)
    if rotation:
        decomp.outputRotate.connect(source.rotate, force=True)
    if scale:
        decomp.outputScale.connect(source.scale, force=True)
    return decomp


def calculate_matrix_offset_(target, source):
    """
    Calculate the matrix offset of the source to the target.
    Args:
            target(dagnode): The target node.
            source(dagnode): The source node.
    Return:
            The offset matrix values from target to source.
    """
    tm = dt.Matrix(target.getMatrix(ws=True)).inverse()
    sm = dt.Matrix(source.getMatrix(ws=True))
    return sm.__mul__(tm)


def matrixConstraint_UI_GRP_(source):
    """
    Creates the the UI node for the matrix constraint
    and parent it under a specified node.
    Args:
            source(dagnode): The source node.
            parent(dagnode): The parent for the UI GRP.
    Return:
            tuple: The UI_GRP node.
    """
    UI_GRP = pmc.createNode('transform', n=str(source) +
                            '_matrixConstraint_UI_GRP')
    attributes.addAttr(node=UI_GRP, name='offset_matrix', attrType='matrix')
    attributes.lockAndHideAttributes(node=UI_GRP)
    source.addChild(UI_GRP)
    return UI_GRP


def multMatrix_setup_(source, target, maintainOffset=None):
    """
    Creates the multMatrix setup for further use.
    Args:
            source(dagnode): The source node.
            target(dagnode): The target node.
            maintainOffste(bool): Enable/Disable the maintainOffset option.
    Return:
            tuple: The created multMatrix node.
    """
    parent = source.getParent()
    mulMaND = pmc.createNode('multMatrix', n=str(source) + '_0_MUMAND')
    target.worldMatrix[0].connect(mulMaND.matrixIn[1])
    if parent:
        parent.worldInverseMatrix[0].connect(mulMaND.matrixIn[2])
    else:
        source.parentInverseMatrix[0].connect(mulMaND.matrixIn[2])
    if maintainOffset:
        UI_GRP = matrixConstraint_UI_GRP_(source=source)
        UI_GRP.offset_matrix.set(
            calculate_matrix_offset_(target, source))
        UI_GRP.offset_matrix.connect(mulMaND.matrixIn[0])
    return mulMaND


def create_matrixConstraint(source, target, translation=True,
                            rotation=True, scale=True, maintainOffset=None):
    """
    Creates the matrix constraint.
    Args:
            source(dagnode): The source node.
            target(dagnode): The target node.
            translation(bool): Connect/Disconnect the translation channel.
            rotation(bool): Connect/Disconnect the rotation channel.
            scale(bool): Connect/Disconnect the scale channel.
            maintainOffste(bool): Enable/Disable the maintainOffset option.
    """
    axis = ['X', 'Y', 'Z']
    decompMatND = pmc.createNode('decomposeMatrix', n=str(source) +
                                 '_0_DEMAND')
    mulMaND = multMatrix_setup_(source=source, target=target,
                                maintainOffset=maintainOffset)
    mulMaND.matrixSum.connect(decompMatND.inputMatrix)
    if translation:
        for axe in axis:
            decompMatND.attr('outputTranslate' +
                             axe).connect(source.attr('translate' + axe))
    if rotation:
        for axe in axis:
            decompMatND.attr('outputRotate' +
                             axe).connect(source.attr('rotate' + axe))
    if scale:
        for axe in axis:
            decompMatND.attr('outputScale' +
                             axe).connect(source.attr('scale' + axe))


def ancestors(node):
    """
    Return a list of ancestors, starting with the direct
    parent and ending with the top-level(root) parent.
    Args:
            node(dagnode): The last transform of a hierarchy.
    Return:
            list: The ancestors tranforms.
    """
    result = []
    parent = node.getParent()
    while parent is not None:
        result.append(parent)
        parent = parent.getParent()
    return result


def descendants(rootNode, reverse=None, typ='transform'):
    """
    Gets the descendants of a hierarchy.
    By default it starts with the rootNode and goes down.
    Args:
            rootNode(dagnode): The root of the hierarchy.
            reverse(bool): Reverse the order of the output.
            typ(str): The typ to search for.
    Return:
            list: The descendant nodes.
    """
    result = []
    descendants = rootNode.getChildren(ad=True, type=typ)
    if not reverse:
        for descendant in descendants:
            result.insert(0, descendant)
        result.insert(0, rootNode)
    else:
        result = descendants
        result.append(rootNode)
    return result


def custom_orientJoint(source, target, aimAxes=[1, 0, 0],
                       upAxes=[0, 1, 0]):
    """
    Orient a joint based on aimConstraint technic.
    By default it orients the x axes
    with the y axes as up vector.
    Args:
            source(dagnode): The joint to orient.
            target(dagnode): The transform as orient target.
            aimAxes(list): The aim axes. [1, 1, 1] = [x, y, z]
            upAxes(list): The aim axes. [1, 1, 1] = [x, y, z]
    Return:
            tuple: The orientated joint.
    """
    if source.nodeType() == 'joint':
        upObject = spaceLocator_onPosition(source, bufferGRP=True)
        upObject[1].translate.set(v * 5 for v in upAxes)
        source.rotate.set(0, 0, 0)
        source.jointOrient.set(0, 0, 0)
        pmc.delete(create_aimConstraint(source=source, target=target,
                                        maintainOffset=False,
                                        aimAxes=aimAxes, upAxes=upAxes,
                                        worldUpType='object',
                                        worldUpObject=upObject[1],
                                        killUpVecObj=False)[0])
        pmc.delete(upObject)
        source.jointOrient.set(source.rotate.get())
        source.rotate.set(0, 0, 0)
        return source
    else:
        logger.log(level='error', message='The source node must be a joint',
                   logger=moduleLogger)


def custom_orientJointHierarchy(rootJNT=None, aimAxes=[1, 0, 0],
                                upAxes=[0, 1, 0]):
    """
    Orient a joint hierarchy based on a aimConstraint technic.
    By default it orients the x axes
    with the y axes as up vector.
    Args:
            rootJNT(dagnode): The rootNode of the hierarchy.
            aimAxes(list): The aim axes. [1, 1, 1] = [x, y, z]
            upAxes(list): The aim axes. [1, 1, 1] = [x, y, z]
    Return:
            list: The hierarchy.
    """
    hierarchy = descendants(rootNode=rootJNT, reverse=True,
                            typ='joint')
    if len(hierarchy) > 1:
        temp = hierarchy[:]
        for jnt in hierarchy:
            pmc.parent(jnt, w=True)
        for jnt_ in hierarchy:
            if len(temp) > 1:
                custom_orientJoint(temp[1], temp[0],
                                   aimAxes=aimAxes, upAxes=upAxes)
                temp[1].addChild(temp[0])
                temp.remove(temp[0])
        hierarchy[0].rotate.set(0, 0, 0)
        hierarchy[0].jointOrient.set(0, 0, 0)
        return hierarchy
    else:
        logger.log(level='error',
                   message='It must be a hierarchy for a proper orient',
                   logger=moduleLogger)


def default_orientJoint(node, aimAxes='xyz', upAxes='yup'):
    """
    Orient a joint in a hierarchy.
    By default it orients the x axes
    with the y axes as up vector.
    Args:
            node(dagnode): A node in the hierarchy.
            aimAxes(str): Valid is xyz, yzx, zxy,
            zyx, yxz, xzy, none.
            upAxes(str): Valid is xup, xdown, yup, ydown,
            zup, zdown, none.
    """
    if node.nodeType() == 'joint':
        try:
            node.orientJoint(val=aimAxes, secondaryAxisOrient=upAxes)
        except:
            logger.log(level='error',
                       message='Joint not in hierarchy. Or'
                       ' rotate channels has values.',
                       logger=moduleLogger)
    else:
        logger.log(level='error', message='Node has to be a joint',
                   logger=moduleLogger)


def default_orientJointHierarchy(rootNode, aimAxes='xyz', upAxes='yup'):
    """
    Orient a joint hierarchy.
    By default it orients the x axes
    with the y axes as up vector.
    Args:
            rootJNT(dagnode): The rootNode of the hierarchy.
            aimAxes(str): Valid is xyz, yzx, zxy,
            zyx, yxz, xzy, none.
            upAxes(str): Valid is xup, xdown, yup, ydown,
            zup, zdown, none.
    Return:
            list: The hierarchy.
    """
    hierarchy = descendants(rootNode=rootNode, reverse=True,
                            typ='joint')
    for jnt in hierarchy[1:]:
        default_orientJoint(node=jnt, aimAxes=aimAxes, upAxes=upAxes)
    hierarchy[0].jointOrient.set(0, 0, 0)


def create_joint(name='M_BND_0_JNT', typ='BND', node=None,
                 orientMatchRotation=True):
    """
    Create a joint node with a specific typ.
    By Default it creates a 'BND' joint and match the jointOrient with
    the roatation of a node.
    Args:
            name(str): The name of the node. Try to use the JoMRS
            naming convention. If not it will throw a warning.
            typ(str): Typ of the joint. Valid is: [BND, DRV, FK, IK]
            node(dagnode): The node for transformation match.
            orientMatchRotation(bool): Enable the match of the joint
            orientation with the rotation of the node.
    Return:
            tuple: The created joint node.
    """
    name = strings.string_checkup(name, moduleLogger)
    data = [{'typ': 'BND', 'radius': 1, 'overrideColor': 17},
            {'typ': 'DRV', 'radius': 2.5, 'overrideColor': 18},
            {'typ': 'FK', 'radius': 1.5, 'overrideColor': 4},
            {'typ': 'IK', 'radius': 2, 'overrideColor': 6}]
    pmc.select(clear=True)
    JNT = pmc.joint(n=name)
    for util in data:
        if util['typ'] == typ:
            JNT.overrideEnabled.set(1)
            JNT.radius.set(util['radius'])
            JNT.overrideColor.set(util['overrideColor'])
    if node:
        pmc.delete(pmc.parentConstraint(node, JNT, mo=False))
    if orientMatchRotation:
        JNT.jointOrient.set(JNT.rotate.get())
        JNT.rotate.set(0, 0, 0)
    return JNT


def convert_to_skeleton(rootNode=None, prefix='M_BND', suffix='JNT',
                        typ='BND', bufferGRP=True, inverseScale=True):
    """
    Convert a hierarchy of transform nodes into a joint skeleton.
    By default it is a BND joint hierarchy with a buffer group.
    The hierarchy has disconnected inverse scale plugs.
    Args:
            rootNode(dagnode): The rootNode of the transform
            hierarchy.
            prefix(str): The prefix of the joints.
            suffix(str): The suffix of the joints.
            typ(str): The joint types.
            bufferGRP(bool): Creates a buffer group for the
            hierarchy.
            inverseScale(bool): Disconnect the inverse scale
            plugs of the joints.
    Return:
            list: The new created joint hierarchy.
    """
    result = []
    hierarchy = descendants(rootNode=rootNode)
    if hierarchy:
        for tra in range(len(hierarchy)):
            name = '{}_{}_{}'.format(prefix, str(tra), suffix)
            name = strings.string_checkup(name, moduleLogger)
            JNT = create_joint(name=name, node=hierarchy[tra], typ=typ)
            result.append(JNT)
    temp = result[:]
    for node in hierarchy:
        if len(temp) > 1:
            temp[-2].addChild(temp[-1])
            temp.remove(temp[-1])
    if bufferGRP:
        bufferGRP = create_bufferGRP(node=result[0])
        result.insert(0, bufferGRP)
    if inverseScale:
        for node in result:
            try:
                node.inverseScale.disconnect()
            except:
                continue
    return result


def create_motionPath(name='M_test_0_MPND', curveShape=None, target=None,
                      position=1, worldUpType='objectUp', upVecObj=None,
                      aimAxes='x', upAxes='y', follow=True,
                      worldUpVector=[0, 0, 1]):
    """
    Create a motionPath node. By default the worldUpType is objectUp. The
    aimAxes is 'x' and the upAxes is 'y'. Follow mode is enabled.
    Args:
            name(str): The name of the node. Try to use the JoMRS
            naming convention. If not it will throw a warning.
            curveShape(dagnode): The curve shape node for the motion path.
            target(dagnode): The node to attach on the curve.
            position(float): The position of the the target.
            worldUpType(str): The upvector mode for the node.
            Valis is: [sceneUp, objectUp, objectRotationUp, vector, normal]
            upVecObj(dagnode): The transform for the up vector.
            aimAxes(str): The aim axes. Valis is [x, y, z]
            upAxes(str): The up axes. Valis is [x, y, z]
            follow(bool): Enable the aim and up axes of the node.
            worldUpVector(list): The axes for the world up vector.
    Return:
            tuple: The created motion path node.
    """
    axes = ['X', 'Y', 'Z']
    name = strings.string_checkup(name, moduleLogger)
    MPND = pmc.createNode('motionPath', n=name)
    MPND.fractionMode.set(1)
    MPND.uValue.set(position)
    curveShape.worldSpace[0].connect(MPND.geometryPath)
    if target:
        for axe in axes:
            MPND.attr('rotate' + axe).connect(target.attr('rotate' + axe),
                                              force=True)
            MPND.attr(axe.lower() +
                      'Coordinate').connect(target.attr('translate' + axe),
                                            force=True)
    if follow:
        if aimAxes == 'x':
            value = 0
        elif aimAxes == 'y':
            value = 1
        elif aimAxes == 'z':
            value = 2
        if upAxes == 'x':
            value_ = 0
        elif upAxes == 'y':
            value_ = 1
        elif upAxes == 'z':
            value_ = 2
        if worldUpType == 'sceneUp':
            value__ = 0
        elif worldUpType == 'objectUp':
            value__ = 1
        elif worldUpType == 'objectRotationUp':
            value__ = 2
        elif worldUpType == 'vector':
            value__ = 3
        elif worldUpType == 'normal':
            value__ = 4
        if value__ == 1 or value__ == 2:
            if upVecObj:
                upVecObj.worldMatrix.connect(MPND.worldUpMatrix, force=True)
            else:
                logger.log(level='error',
                           message='You need a upvector transform',
                           logger=moduleLogger)
        if value__ == 2 or value__ == 3:
            MPND.worldUpVectorX.set(worldUpVector[0])
            MPND.worldUpVectorY.set(worldUpVector[1])
            MPND.worldUpVectorZ.set(worldUpVector[2])
        MPND.follow.set(1)
        MPND.frontAxis.set(value)
        MPND.upAxis.set(value_)
        MPND.worldUpType.set(value__)
    else:
        MPND.follow.set(0)
    return MPND


def create_hierarchy(nodes=None, inverseScale=None):
    """
    Create a hierarchy of nodes.
    Args:
            nodes(list): List of nodes.
            inverseScale(bool): Disconnect the inverse scale
            plugs of the joints.
    Return:
            list: The list of nodes in the hierarchy.
    """
    temp = nodes[:]
    for number in range(len(temp)):
        if len(temp) > 1:
            temp[-2].addChild(temp[-1])
            temp.remove(temp[-1])
    if inverseScale:
        for node in nodes:
            if node.nodeType() == 'joint':
                node.inverseScale.disconnect()
            else:
                logger.log(level='error',
                           message='Inverse scale option only'
                           ' available for joints',
                           logger=moduleLogger)
    return nodes


def reduce_shapeNodes(node=None):
    """
    Reduce a transform to his true shape node.
    Args:
            node(dagnode): The transform with the shape ndoe.
    Return:
            list: The true shape node of the transform.
    """
    searchPattern = 'ShapeOrig|ShapeDeformed'
    shapes = node.getShapes()
    for shape in shapes:
        shape.intermediateObject.set(0)
        result = strings.search(searchPattern, str(shape))
        pmc.delete(result)
    return node.getShapes()
