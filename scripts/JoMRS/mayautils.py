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
JoMRS maya utils module. Utilities helps
to create maya behaviours.
"""
###############
# TO DO:
# config file for valid strings. For projects modifications
# check if all strings follow the JoMRS string handling
# match position function.
###############

import pymel.core as pmc
import pymel.core.datatypes as dt
import attributes
import strings
import logging
import logger
import constants
import meta
import uuid

##########################################################
# GLOBAL
##########################################################

_LOGGER = logging.getLogger(__name__ + ".py")

##########################################################
# FUNCTIONS
##########################################################


def create_buffer_grp(node, name=None):
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
    if not name:
        name = name + "_buffer_GRP"
    else:
        name = str(node) + "_buffer_GRP"
    buffer_grp = pmc.createNode("transform", n=name)
    buffer_grp.setMatrix(node.getMatrix(worldSpace=True), worldSpace=True)
    buffer_grp.addChild(node)
    if parent:
        parent.addChild(buffer_grp)
    return buffer_grp


def space_locator_on_position(node, buffer_grp=True):
    """
    Create a spaceLocator on the position of a node.
    Args:
            node(dagnode): The match transform node.
            buffer_grp(bool): Create a buffer group for the locator.
    Return:
            list: The buffer group, the locator node.
    """
    result = []
    name = strings.string_checkup(str(node) + "_0_LOC", _LOGGER)
    loc = pmc.spaceLocator(n=name)
    loc.setMatrix(node.getMatrix(worldSpace=True), worldSpace=True)
    result.append(loc)
    if buffer_grp:
        buffer_grp = create_buffer_grp(loc)
        result.insert(0, buffer_grp)
    return result


def create_spline_ik(
    name,
    start_jnt=None,
    end_jnt=None,
    parent=None,
    curve_parent=None,
    curve=None,
    snap=True,
    sticky=False,
    weight=1,
    po_weight=1,
):
    """
    Create a splineIK.
    Args:
            name(str): The spline IK name. You should follow the
            JoMRS naming convention. If not it will throw some
            warnings.
            start_jnt(dagNode): The start joint of the chain.
            end_jnt(dagNode): The end joint of the chain.
            parent(dagNode): The parent for the IK_handle.
            snap(bool): Enable/Disalbe snap option of the IK.
            sticky(bool): Enable/Disalbe stickieness option of the IK.
            weight(float): Set handle weight.
            po_weight(float): Set the poleVector weight.
    Return:
            list(dagnodes): the ik Handle, the effector,
            the spline ik curve shape.
    """
    result = []
    data = {}
    name = strings.string_checkup(name, _LOGGER)
    data["n"] = name
    data["solver"] = "ikSplineSolver"
    data["createCurve"] = False
    data["sj"] = start_jnt
    data["ee"] = end_jnt
    if curve is not None:
        data["c"] = curve
    else:
        data["createCurve"] = True
    ik_handle = pmc.ikHandle(**data)
    pmc.rename(ik_handle[1], str(end_jnt) + "_EFF")
    result.extend(ik_handle)
    if curve:
        pmc.rename(curve, str(curve) + "_CRV")
        shape = curve.getShape()
        result.append(shape)
    else:
        pmc.rename(ik_handle[2], str(ik_handle[2] + "_CRV"))
        shape = pmc.PyNode(ik_handle[2]).getShape()
        result[2] = shape
    if parent:
        parent.addChild(result[0])
    if curve_parent:
        curve_parent.addChild(result[2].getParent())
    result[2].getParent().visibility.set(0)
    attributes.lock_and_hide_attributes(result[2].getParent())
    result[0].visibility.set(0)
    if snap is False:
        result[0].snapEnable.set(0)
    if sticky:
        result[0].stickiness.set(1)
    result[0].attr("weight").set(weight)
    result[0].attr("po_weight").set(po_weight)
    logger.log(
        level="info", message='Spline IK "' + name + '" created', logger=_LOGGER
    )
    return result


def create_IK(
    name,
    solver="ikSCsolver",
    start_jnt=None,
    end_jnt=None,
    parent=None,
    snap=True,
    sticky=False,
    weight=1,
    po_weight=1,
):
    """
    Create a IK. Default is a single chain IK.
    Args:
            name(str): The IK name. You should follow
            the JoMRS naming convention. If not it will throw some
            warnings.
            solver(str): The solver of the IK.
            start_jnt(dagNode): The start joint of the chain.
            end_jnt(dagNode): The end joint of the chain.
            parent(dagNode): The parent for the IK_handle.
            snap(bool): Enable/Disalbe snap option of the IK.
            sticky(bool): Enable/Disalbe stickieness option of the IK.
            weight(float): Set handle weight.
            po_weight(float): Set the poleVector weight.
    Return:
    """
    data = {}
    name = strings.string_checkup(name, _LOGGER)
    data["n"] = name
    data["solver"] = solver
    data["sj"] = start_jnt
    data["ee"] = end_jnt
    ik_handle = pmc.ikHandle(**data)
    pmc.rename(ik_handle[1], str(end_jnt) + "_EFF")
    if parent:
        parent.addChild(ik_handle[0])
    ik_handle[0].visibility.set(0)
    if snap is False:
        ik_handle[0].snapEnable.set(0)
    if sticky:
        ik_handle[0].stickiness.set(1)
    ik_handle[0].attr("weight").set(weight)
    ik_handle[0].attr("po_weight").set(po_weight)
    logger.log(
        level="info", message=solver + ' "' + name + '" created', logger=_LOGGER
    )
    return ik_handle


def constraint(
    typ="parent",
    source=None,
    target=None,
    maintain_offset=True,
    axes=["X", "Y", "Z"],
):
    """
    Create contraints. By default it creates a parentConstraint
    with maintain offset.
    Args:
            typ(str): The constraint type.
            source(dagnode): The source node.
            target(dagnode): The target node.
            maintain_offset(bool): If the constraint should keep
            the offset of the target.
            axes(list): The axes to contraint as strings.
    Return:
            list: The created constraint.
    """
    result = []
    skip_axes = ["x", "y", "z"]
    if typ == "parent":
        result = pmc.parentConstraint(
            target,
            source,
            mo=maintain_offset,
            skipRotate=skip_axes,
            skipTranslate=skip_axes,
        )
        for ax in axes:
            result.attr("constraintTranslate" + ax.upper()).connect(
                source.attr("translate" + ax.upper())
            )
            result.attr("constraintRotate" + ax.upper()).connect(
                source.attr("rotate" + ax.upper())
            )
    if typ == "point":
        result = pmc.pointConstraint(
            target, source, mo=maintain_offset, skip=skip_axes
        )
        for ax in axes:
            result.attr("constraintTranslate" + ax.upper()).connect(
                source.attr("translate" + ax.upper())
            )
    if typ == "orient":
        result = pmc.orientConstraint(
            target, source, mo=maintain_offset, skip=skip_axes
        )
        for ax in axes:
            result.attr("constraintRotate" + ax.upper()).connect(
                source.attr("rotate" + ax.upper())
            )
    if typ == "scale":
        result = pmc.scaleConstraint(
            target, source, mo=maintain_offset, skip=skip_axes
        )
        for ax in axes:
            result.attr("constraintScale" + ax.upper()).connect(
                source.attr("scale" + ax.upper())
            )
    return result


def constraint_ui_node_(constraint=None, target=None):
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
        constraint_ui = pmc.creatNode(
            "transform", n="{}{}".format(str(constraint), "_UI_GRP")
        )
        constraint.addChild(constraint_ui)
        attributes.lock_and_hide_attributes(node=constraint_ui)
        for x in range(len(target)):
            long_name = "{}_{}".format(str(target[x]), "W" + str(x))
            attributes.add_attr(
                node=constraint_ui,
                name=long_name,
                attr_type="float",
                minValue=0,
                maxValue=1,
                keyable=True,
            )
            constraint_ui.attr(long_name).set(1)
            constraint_ui.attr(long_name).connect(
                constraint.target[x].targetWeight, force=True
            )
        for ud_attr in constraint.listAttr(ud=True):
            pmc.deleteAttr(ud_attr)
    else:
        logger.log(
            level="error",
            message="source and constraint needed for" " constraint_UI_node",
            logger=_LOGGER,
        )
    return constraint_ui


def no_pivots_no_rotate_order_(constraint):
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
        logger.log(level="warning", message=exceptions, logger=_LOGGER)


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
        parent.worldInverseMatrix.connect(
            constraint.constraintParentInverseMatrix
        )
    return constraint_ui_node_(constraint=constraint, target=target)


def create_constraint(
    typ="parent",
    source=None,
    target=None,
    maintain_offset=True,
    axes=["X", "Y", "Z"],
    no_cycle=False,
    no_pivots=False,
    no_parent_influ=False,
):
    """
    Create constraints with a lot more functionality.
    By default it creates a parentConstraint.
    Args:
            typ(str): The constraint type.
            source(dagnode): The source node.
            target(dagnode): The target node.
            maintain_offset(bool): If the constraint should keep
            the offset of the target.
            axes(list): The axes to contraint as strings.
            no_cycle(bool): It creates a constraint_UI_node under
            the parent constraint. And disconnect inner cycle
            connections of the contraint.
            no_pivots(bool): Disconnect the pivot plugs.
            no_parent_influ(bool): Disconnect the
            constraintParentInverseMatrix
            plug. So that the parent transformation of the source node
            influnce the source node.
    Return:
            list: The constraint node, constraint_UI_node
    """
    result = []
    constraint_ = constraint(
        typ=typ,
        source=source,
        target=target,
        maintain_offset=maintain_offset,
        axes=axes,
    )
    result.append(constraint_)
    if no_cycle:
        con_ui_node = no_constraint_cycle(
            constraint=constraint_, source=source, target=target
        )
        result.append(con_ui_node)
    if no_pivots:
        no_pivots_no_rotate_order_(constraint=constraint_)
    if no_parent_influ:
        constraint_.constraintParentInverseMatrix.disconnect()
    return result


def aim_constraint_(
    source=None,
    target=None,
    maintain_offset=True,
    axes=["X", "Y", "Z"],
    aim_axes=[1, 0, 0],
    up_axes=[0, 1, 0],
    world_up_type="object",
    kill_up_vec_obj=None,
    parent_up_vec_obj=None,
    world_up_object=None,
    world_up_vector=[0, 1, 0],
):
    """
    Create a aimConstraint.
    By default it creates a object as upVector.
    Args:
            source(dagnode): The source node.
            target(dagnode): The target node.
            maintain_offset(bool): If the constraint should keep
            the offset of the target.
            axes(list): The axes to contraint as strings.
            aim_axes(list): The axes to aim for.
            ['x','y','z'] = [1,1,1]
            up_axes(list): The axes to the up vector.
            ['x','y','z'] = [1,1,1]
            world_up_type(string): The type for the up vector.
            Valid: none, scene, vector, object, objectrotation.
            kill_up_vec_obj(bool): Kills the up vector transform.
            parent_up_vec_obj(dagnode): The parent for the up vector.
            world_up_object(dagnode): The up vector transform node.
            world_up_vector(list): The axes for the world up vector.
            ['x','y','z'] = [1,1,1]

    Return:
            list: The aim constraint, the upVector locator node.
    """
    skip_axes = ["x", "y", "z"]
    temp = []
    if world_up_type == "object":
        if not world_up_object:
            world_up_object = pmc.spaceLocator(n=str(source) + "_upVec_0_LOC")
            world_up_object_buffer = pmc.group(
                world_up_object, n=str(world_up_object) + "_buffer_GRP"
            )
            temp.append(world_up_object_buffer)
            pmc.delete(
                pmc.parentConstraint(source, world_up_object_buffer, mo=False)
            )
            world_up_object.translate.set(v * 5 for v in up_axes)
        con = pmc.aimConstraint(
            target,
            source,
            mo=maintain_offset,
            aim=aim_axes,
            skip=skip_axes,
            u=up_axes,
            worldUpType=world_up_type,
            worldUpObject=world_up_object,
        )
    elif world_up_type == "objectrotation":
        con = pmc.aimConstraint(
            target,
            source,
            mo=maintain_offset,
            aim=aim_axes,
            skip=skip_axes,
            u=up_axes,
            worldUpType=world_up_type,
            worldUpObject=world_up_object,
        )
    elif world_up_type == "vector":
        con = pmc.aimConstraint(
            target,
            source,
            mo=maintain_offset,
            aim=aim_axes,
            skip=skip_axes,
            u=up_axes,
            worldUpType=world_up_type,
            worldUpVector=world_up_vector,
        )
    else:
        con = pmc.aimConstraint(
            target,
            source,
            mo=maintain_offset,
            aim=aim_axes,
            skip=skip_axes,
            u=up_axes,
            worldUpType=world_up_type,
        )
    for ax in axes:
        con.attr("constraintRotate" + ax.upper()).connect(
            source.attr("rotate" + ax.upper())
        )
    temp.append(world_up_object)
    if kill_up_vec_obj:
        pmc.delete(temp)
        return [con]
    if parent_up_vec_obj:
        pmc.parent(temp[0], parent_up_vec_obj)
    return [con, temp[:]]


def create_aim_constraint(
    source=None,
    target=None,
    maintain_offset=True,
    axes=["X", "Y", "Z"],
    aim_axes=[1, 0, 0],
    up_axes=[0, 1, 0],
    world_up_type="object",
    kill_up_vec_obj=None,
    parent_up_vec_obj=None,
    world_up_object=None,
    world_up_vector=[0, 1, 0],
    no_cycle=False,
    no_pivots=False,
    no_parent_influ=False,
):
    """
    Create a aimConstraint with advanced options
    By default it creates a object as upVector.
    Args:
            source(dagnode): The source node.
            target(dagnode): The target node.
            maintain_offset(bool): If the constraint should keep
            the offset of the target.
            axes(list): The axes to contraint as strings.
            aim_axes(list): The axes to aim for.
            ['x','y','z'] = [1,1,1]
            up_axes(list): The axes to the up vector.
            ['x','y','z'] = [1,1,1]
            world_up_type(string): The type for the up vector.
            Valid: none, scene, vector, object, objectrotation.
            kill_up_vec_obj(bool): Kills the up vector transform.
            parent_up_vec_obj(dagnode): The parent for the up vector.
            world_up_object(dagnode): The up vector transform node.
            world_up_vector(list): The axes for the world up vector.
            ['x','y','z'] = [1,1,1]
            no_cycle(bool): It creates a constraint_UI_node under
            the constraint. And disconnect inner cycle connections
            of the contraint.
            no_pivots(bool): Disconnect the pivot plugs.
            no_parent_influ(bool): Disconnect the
            constraintParentInverseMatrix
            plug. So that the parent transformation of the source node
            influnce the source node.

    Return:
            list: The aim constraint, the upVector locator node,
            the constraint_UI_node.
    """
    result = aim_constraint_(
        source=source,
        target=target,
        maintain_offset=maintain_offset,
        axes=axes,
        aim_axes=aim_axes,
        up_axes=up_axes,
        world_up_type=world_up_type,
        kill_up_vec_obj=kill_up_vec_obj,
        parent_up_vec_obj=parent_up_vec_obj,
        world_up_object=world_up_object,
        world_up_vector=world_up_vector,
    )
    if no_cycle:
        con_ui_node = no_constraint_cycle(
            constraint=result[0], target=target, source=source
        )
        result.append(con_ui_node)
    if no_pivots:
        no_pivots_no_rotate_order_(constraint=result[0])
    if no_parent_influ:
        result[0].constraintParentInverseMatrix.disconnect()
    return result


def decompose_matrix_constraint(
    source,
    target,
    translation=True,
    rotation=True,
    scale=True,
    target_plug=None,
):
    """
    Create decompose matrix constraint.
    Args:
            source(dagnode): The source node.
            target(dagnode): The target node.
            translation(bool): Envelope to connect the translation.
            rotation(bool): Envelope to connect the rotation.
            scale(bool): Envelope to connect the scale.
            target_plug(string): Target plug for world matrix connection.
            If none will take "worldMatrix[0]" as default.
    Return:
            tuple: Created decompose matrix node.
    """
    decomp = pmc.createNode("decomposeMatrix", n=str(source) + "_0_DEMAND")
    if not target_plug:
        target_plug = "worldMatrix[0]"
    target.attr(target_plug).connect(decomp.inputMatrix)
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


def matrix_constraint_ui_grp_(source):
    """
    Creates the the UI node for the matrix constraint
    and parent it under a specified node.
    Args:
            source(dagnode): The source node.
            parent(dagnode): The parent for the UI GRP.
    Return:
            tuple: The UI_GRP node.
    """
    ui_grp = pmc.creatNode(
        "transform", n=str(source) + "_matrixConstraint_UI_GRP"
    )
    attributes.add_attr(node=ui_grp, name="offset_matrix", attr_type="matrix")
    attributes.lock_and_hide_attributes(node=ui_grp)
    source.addChild(ui_grp)
    return ui_grp


def mult_matrix_setup_(source, target, maintainOffset=None):
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
    mul_ma_nd = pmc.creatNode("multMatrix", n=str(source) + "_0_MUMAND")
    target.worldMatrix[0].connect(mul_ma_nd.matrixIn[1])
    if parent:
        parent.worldInverseMatrix[0].connect(mul_ma_nd.matrixIn[2])
    else:
        source.parentInverseMatrix[0].connect(mul_ma_nd.matrixIn[2])
    if maintainOffset:
        ui_grp = matrix_constraint_ui_grp_(source=source)
        ui_grp.offset_matrix.set(calculate_matrix_offset_(target, source))
        ui_grp.offset_matrix.connect(mul_ma_nd.matrixIn[0])
    return mul_ma_nd


def create_matrix_constraint(
    source,
    target,
    translation=True,
    rotation=True,
    scale=True,
    maintain_offset=None,
):
    """
    Creates the matrix constraint.
    Args:
            source(dagnode): The source node.
            target(dagnode): The target node.
            translation(bool): Connect/Disconnect the translation channel.
            rotation(bool): Connect/Disconnect the rotation channel.
            scale(bool): Connect/Disconnect the scale channel.
            maintainOffste(bool): Enable/Disable the maintain_offset option.
    """
    axis = ["X", "Y", "Z"]
    decomp_mat_nd = pmc.creatNode(
        "decomposeMatrix", n=str(source) + "_0_DEMAND"
    )
    mul_ma_nd = mult_matrix_setup_(
        source=source, target=target, maintainOffset=maintain_offset
    )
    mul_ma_nd.matrixSum.connect(decomp_mat_nd.inputMatrix)
    if translation:
        for axe in axis:
            decomp_mat_nd.attr("outputTranslate" + axe).connect(
                source.attr("translate" + axe)
            )
    if rotation:
        for axe in axis:
            decomp_mat_nd.attr("outputRotate" + axe).connect(
                source.attr("rotate" + axe)
            )
    if scale:
        for axe in axis:
            decomp_mat_nd.attr("outputScale" + axe).connect(
                source.attr("scale" + axe)
            )


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


def descendants(root_node, reverse=None, typ="transform"):
    """
    Gets the descendants of a hierarchy.
    By default it starts with the root_node and goes down.
    Args:
            root_node(dagnode): The root of the hierarchy.
            reverse(bool): Reverse the order of the output.
            typ(str): The typ to search for.
    Return:
            list: The descendant nodes.
    """
    result = []
    descendants = root_node.getChildren(ad=True, type=typ)
    if not reverse:
        for descendant in descendants:
            result.insert(0, descendant)
        result.insert(0, root_node)
    else:
        result = descendants
        result.append(root_node)
    return result


def get_descendants_from_parent(node, reverse=None, typ="transform"):
    """
    Get all descendants from parent of given node.
    By Default it takes the parent of the given node and goes down the
    hierarchy.
    Args:
            node(dagnode): The source node.
            reverse(bool): Reverse the order of the output.
            typ(str): The typ to search for.
    Return:
            list: The descendant nodes.
    """
    if node.getParent():
        return descendants(node.getParent(), reverse=reverse, typ=typ)
    else:
        raise IndexError("{} has no parent node".format(str(node)))


def custom_orient_joint(source, target, aim_axes=[1, 0, 0], up_axes=[0, 1, 0]):
    """
    Orient a joint based on aimConstraint technic.
    By default it orients the x axes
    with the y axes as up vector.
    Args:
            source(dagnode): The joint to orient.
            target(dagnode): The transform as orient target.
            aim_axes(list): The aim axes. [1, 1, 1] = [x, y, z]
            up_axes(list): The aim axes. [1, 1, 1] = [x, y, z]
    Return:
            tuple: The orientated joint.
    """
    if source.nodeType() == "joint":
        up_object = space_locator_on_position(source, buffer_grp=True)
        up_object[1].translate.set(v * 5 for v in up_axes)
        source.rotate.set(0, 0, 0)
        source.jointOrient.set(0, 0, 0)
        pmc.delete(
            create_aim_constraint(
                source=source,
                target=target,
                maintain_offset=False,
                aim_axes=aim_axes,
                up_axes=up_axes,
                world_up_type="object",
                world_up_object=up_object[1],
                kill_up_vec_obj=False,
            )[0]
        )
        pmc.delete(up_object)
        source.jointOrient.set(source.rotate.get())
        source.rotate.set(0, 0, 0)
        return source
    else:
        logger.log(
            level="error",
            message="The source node must be a joint",
            logger=_LOGGER,
        )


def custom_orient_joint_hierarchy(
    root_jnt=None, aim_axes=[1, 0, 0], up_axes=[0, 1, 0]
):
    """
    Orient a joint hierarchy based on a aimConstraint technic.
    By default it orients the x axes
    with the y axes as up vector.
    Args:
            root_jnt(dagnode): The root_node of the hierarchy.
            aim_axes(list): The aim axes. [1, 1, 1] = [x, y, z]
            up_axes(list): The aim axes. [1, 1, 1] = [x, y, z]
    Return:
            list: The hierarchy.
    """
    hierarchy = descendants(root_node=root_jnt, reverse=True, typ="joint")
    if len(hierarchy) > 1:
        temp = hierarchy[:]
        for jnt in hierarchy:
            pmc.parent(jnt, w=True)
        for jnt_ in hierarchy:
            if len(temp) > 1:
                custom_orient_joint(
                    temp[1], temp[0], aim_axes=aim_axes, up_axes=up_axes
                )
                temp[1].addChild(temp[0])
                temp.remove(temp[0])
        hierarchy[0].rotate.set(0, 0, 0)
        hierarchy[0].jointOrient.set(0, 0, 0)
        return hierarchy
    else:
        logger.log(
            level="error",
            message="It must be a hierarchy for a proper orient",
            logger=_LOGGER,
        )


def default_orient_joint(node, aim_axes="xyz", up_axes="yup"):
    """
    Orient a joint in a hierarchy.
    By default it orients the x axes
    with the y axes as up vector.
    Args:
            node(dagnode): A node in the hierarchy.
            aim_axes(str): Valid is xyz, yzx, zxy,
            zyx, yxz, xzy, none.
            up_axes(str): Valid is xup, xdown, yup, ydown,
            zup, zdown, none.
    """
    if node.nodeType() == "joint":
        try:
            node.orientJoint(val=aim_axes, secondaryAxisOrient=up_axes)
        except:
            logger.log(
                level="error",
                message="Joint not in hierarchy. Or"
                " rotate channels has values.",
                logger=_LOGGER,
            )
    else:
        logger.log(
            level="error", message="Node has to be a joint", logger=_LOGGER
        )


def default_orient_joint_hierarchy(root_node, aim_axes="xyz", up_axes="yup"):
    """
    Orient a joint hierarchy.
    By default it orients the x axes
    with the y axes as up vector.
    Args:
            root_node(dagnode): The root_node of the hierarchy.
            aim_axes(str): Valid is xyz, yzx, zxy,
            zyx, yxz, xzy, none.
            up_axes(str): Valid is xup, xdown, yup, ydown,
            zup, zdown, none.
    Return:
            list: The hierarchy.
    """
    hierarchy = descendants(root_node=root_node, reverse=True, typ="joint")
    for jnt in hierarchy[1:]:
        default_orient_joint(node=jnt, aim_axes=aim_axes, up_axes=up_axes)
    hierarchy[0].jointOrient.set(0, 0, 0)


def create_joint(
    name="M_BND_0_JNT",
    typ="BND",
    node=None,
    orient_match_rotation=True,
    match_matrix=None,
):
    """
    Create a joint node with a specific typ.
    By Default it creates a 'BND' joint and match the jointOrient with
    the rotation of a node.
    Args:
            name(str): The name of the node. Try to use the JoMRS
            naming convention. If not it will throw a warning.
            typ(str): Typ of the joint. Valid is: [BND, DRV, FK, IK]
            node(dagnode): The node for transformation match.
            orient_match_rotation(bool): Enable the match of the joint
            orientation with the rotation of the node.
            match_matrix(matrix): The matrix to match
    Return:
            tuple: The created joint node.
    """
    name = strings.string_checkup(name, _LOGGER)
    data = [
        {"typ": "BND", "radius": 1, "overrideColor": 17},
        {"typ": "DRV", "radius": 2.5, "overrideColor": 18},
        {"typ": "FK", "radius": 1.5, "overrideColor": 4},
        {"typ": "IK", "radius": 2, "overrideColor": 6},
    ]
    jnt = pmc.createNode("joint", n=name)
    for util in data:
        if util["typ"] == typ:
            jnt.overrideEnabled.set(1)
            jnt.radius.set(util["radius"])
            jnt.overrideColor.set(util["overrideColor"])
    if node:
        jnt.setMatrix(node.getMatrix(worldSpace=True), worldSpace=True)
    if orient_match_rotation:
        jnt.jointOrient.set(jnt.rotate.get())
        jnt.rotate.set(0, 0, 0)
    if match_matrix:
        jnt.setMatrix(match_matrix, worldSpace=True)
    return jnt


def convert_to_skeleton(
    root_node=None,
    prefix="M_BND",
    suffix="JNT",
    typ="BND",
    buffer_grp=True,
    inverse_scale=True,
):
    """
    Convert a hierarchy of transform nodes into a joint skeleton.
    By default it is a BND joint hierarchy with a buffer group.
    The hierarchy has disconnected inverse scale plugs.
    Args:
            root_node(dagnode): The root_node of the transform
            hierarchy.
            prefix(str): The prefix of the joints.
            suffix(str): The suffix of the joints.
            typ(str): The joint types.
            buffer_grp(bool): Creates a buffer group for the
            hierarchy.
            inverse_scale(bool): Disconnect the inverse scale
            plugs of the joints.
    Return:
            list: The new created joint hierarchy.
    """
    result = []
    hierarchy = descendants(root_node=root_node)
    if hierarchy:
        for tra in range(len(hierarchy)):
            name = "{}_{}_{}".format(prefix, str(tra), suffix)
            name = strings.string_checkup(name, _LOGGER)
            jnt = create_joint(name=name, node=hierarchy[tra], typ=typ)
            result.append(jnt)
    temp = result[:]
    for node in hierarchy:
        if len(temp) > 1:
            temp[-2].addChild(temp[-1])
            temp.remove(temp[-1])
    if buffer_grp:
        buffer_grp = create_buffer_grp(node=result[0])
        result.insert(0, buffer_grp)
    if inverse_scale:
        for node in result:
            try:
                node.inverseScale.disconnect()
            except:
                continue
    return result


def create_motion_path(
    name="M_test_0_MPND",
    curve_shape=None,
    target=None,
    position=1,
    world_up_type="objectUp",
    up_vec_obj=None,
    aim_axes="x",
    up_axes="y",
    follow=True,
    world_up_vector=[0, 0, 1],
):
    """
    Create a motionPath node. By default the world_up_type is objectUp. The
    aim_axes is 'x' and the upAxes is 'y'. Follow mode is enabled.
    Args:
            name(str): The name of the node. Try to use the JoMRS
            naming convention. If not it will throw a warning.
            curve_shape(dagnode): The curve shape node for the motion path.
            target(dagnode): The node to attach on the curve.
            position(float): The position of the the target.
            world_up_type(str): The upvector mode for the node.
            Valis is: [sceneUp, objectUp, objectRotationUp, vector, normal]
            up_vec_obj(dagnode): The transform for the up vector.
            aim_axes(str): The aim axes. Valis is [x, y, z]
            up_axes(str): The up axes. Valis is [x, y, z]
            follow(bool): Enable the aim and up axes of the node.
            world_up_vector(list): The axes for the world up vector.
    Return:
            tuple: The created motion path node.
    """
    axes = ["X", "Y", "Z"]
    name = strings.string_checkup(name, _LOGGER)
    mpnd = pmc.creatNode("motionPath", n=name)
    mpnd.fractionMode.set(1)
    mpnd.uValue.set(position)
    curve_shape.worldSpace[0].connect(mpnd.geometryPath)
    if target:
        for axe in axes:
            mpnd.attr("rotate" + axe).connect(
                target.attr("rotate" + axe), force=True
            )
            mpnd.attr(axe.lower() + "Coordinate").connect(
                target.attr("translate" + axe), force=True
            )
    if follow:
        if aim_axes == "x":
            value = 0
        elif aim_axes == "y":
            value = 1
        elif aim_axes == "z":
            value = 2
        if up_axes == "x":
            value_ = 0
        elif up_axes == "y":
            value_ = 1
        elif up_axes == "z":
            value_ = 2
        if world_up_type == "sceneUp":
            value__ = 0
        elif world_up_type == "objectUp":
            value__ = 1
        elif world_up_type == "objectRotationUp":
            value__ = 2
        elif world_up_type == "vector":
            value__ = 3
        elif world_up_type == "normal":
            value__ = 4
        if value__ == 1 or value__ == 2:
            if up_vec_obj:
                up_vec_obj.worldMatrix.connect(mpnd.worldUpMatrix, force=True)
            else:
                logger.log(
                    level="error",
                    message="You need a upvector transform",
                    logger=_LOGGER,
                )
        if value__ == 2 or value__ == 3:
            mpnd.worldUpVectorX.set(world_up_vector[0])
            mpnd.worldUpVectorY.set(world_up_vector[1])
            mpnd.worldUpVectorZ.set(world_up_vector[2])
        mpnd.follow.set(1)
        mpnd.frontAxis.set(value)
        mpnd.upAxis.set(value_)
        mpnd.worldUpType.set(value__)
    else:
        mpnd.follow.set(0)
    return mpnd


def create_hierarchy(nodes=None, inverse_scale=None):
    """
    Create a hierarchy of nodes.
    Args:
            nodes(list): List of nodes.
            inverse_scale(bool): Disconnect the inverse scale
            plugs of the joints.
    Return:
            list: The list of nodes in the hierarchy.
    """
    temp = nodes[:]
    for number in range(len(temp)):
        if len(temp) > 1:
            temp[-2].addChild(temp[-1])
            temp.remove(temp[-1])
    if inverse_scale:
        for node in nodes:
            if node.nodeType() == "joint":
                node.inverseScale.disconnect()
            else:
                logger.log(
                    level="error",
                    message="Inverse scale option only" " available for joints",
                    logger=_LOGGER,
                )
    return nodes


def reduce_shape_nodes(node=None):
    """
    Reduce a transform to his true shape node.
    Args:
            node(dagnode): The transform with the shape node.
    Return:
            List: The true shape node of the transform.
    """
    search_pattern = "ShapeOrig|ShapeDeformed"
    shapes = node.getShapes()
    for shape in shapes:
        shape.intermediateObject.set(0)
        result = strings.search(search_pattern, str(shape))
        pmc.delete(result)
    return node.getShapes()


def create_joint_by_data(name, type_, side, index, matrix=None):
    """
    Create a joint by data.
    Args:
            name(str): Joint name.
            type_(str): Joint typ. Valid values are "BND", "DRV", "IK", "FK".
            side(str): Joint side. Valid values are "M", "R", "L".
            index(int): The index number.
            matrix(matrix): Matrix data to snap.
    Return:
            The new joint.
    """
    valid_sides = ["L", "R", "M"]
    valid_types = ["BND", "DRV", "FK", "IK"]
    if side not in valid_sides:
        raise AttributeError(
            'Chosen side is not valid. Valid values are ["L", "R", "M"]'
        )
    if type_ not in valid_types:
        raise AttributeError(
            "Chosen joint type is not valid. Valid values "
            'are ["BND", "DRV", "IK", "FK"]'
        )
    name = "{}_{}_{}_{}_JNT".format(side, type_, name, str(index))
    return create_joint(name=name, typ=type_, match_matrix=matrix)


def create_joint_skeleton_by_data_dic(data_list):
    """
    Create a joint skeleton by a data dictionary.
    Args:
            data_list(list): A List filled with dictionaries.

    Example:
            >>> create_joint_skeleton_by_data_dic([{'matrix': [1.0, 0.0, 0.0,
            >>> 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
            >>> , 'side': 'M', 'name': 'Test', 'typ': 'BND', 'index': 0},
            >>> {'matrix': [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0,
            >>> 1.0, 0.0, 3.0, 10.0, -3.6787579514, 1.0], 'side': 'M', 'name':
            >>> 'Test', 'typ': 'DRV', 'index': 1}])
    """
    temp = [
        create_joint_by_data(
            data["name"],
            data["typ"],
            data["side"],
            data["index"],
            data["matrix"],
        )
        for data in data_list
    ]
    create_hierarchy(temp)


def create_ref_transform(
    name, side, index, buffer_grp=False, match_matrix=None, child=None
):
    """
    Create a reference transform.
    Args:
            name(str): Name for the ref node.
            side(str): The side. Valid values are "M", "R", "L".
            index(int): The index number.
            buffer_grp(bool): Enable buffer grp.
            match_matrix(matrix): The match matrix.
            child(dagnode): Child of node.

    Example:
            >>> create_ref_transform('test', 'M', 0, True,
            >>> [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0,
            >>> 0.0, 0.0, 0.0, 1.0], pmc.PyNode('your_node'))

    Return:
            The new ref node.
    """
    valid_sides = ["L", "R", "M"]
    if side not in valid_sides:
        raise AttributeError(
            'Chosen side is not valid. Valid values are ["L", "R", "M"]'
        )
    name = "{}_REF_{}_{}_GRP".format(side, name, str(index))
    name = strings.string_checkup(name, logger_=_LOGGER)
    ref_trs = pmc.createNode("transform", n=name)
    if match_matrix:
        ref_trs.setMatrix(match_matrix, worldSpace=True)
    if buffer_grp:
        create_buffer_grp(node=ref_trs)
    if child:
        ref_trs.addChild(child)
    return ref_trs


##########################################################
# CLASSES
##########################################################


class ContainerNode(object):
    """
    Wrapper for the maya container node. JoMRS expansion.
    """

    def __init__(self, name=None, icon=None, container_node=None,
                 content_root_node=False):
        """
        Init creation of the container node.

        Args:
            name(str): Container node name.
            icon(str): Path to the icon file.
            container_node(pmc.PyNode()): A container node to pass.
            content_root_node(bool): Enable/Disable content root node creation.

        """
        self.meta_nd = None
        self.meta_nd_name = constants.CONTAINER_META_NODE_NAME
        self.container_meta_nd = None
        self.container_attr_list = []
        self.container = container_node
        self.name = name
        self.icon = icon
        self.container_content = {}
        self.meta_node = None
        self.container_content_root = None
        self.content_root_node = content_root_node
        self.container_meta_nd_attr = {
            "name": constants.CONTAINER_META_ND_ATTR_NAME,
            "attrType": "message",
            "keyable": False,
            "channelBox": False,
        }
        self.container_attr_list.append(self.container_meta_nd_attr)
        if content_root_node:
            self.container_content_root_name = "M_content_root_0_GRP"
        if self.container:
            self.get_meta_nd()

    def create_container(self, meta_nd=True):
        """
        Create the actual container node with a icon.

        Args:
            meta_nd(bool): Enable/Disable meta node creation.

        """
        self.container = pmc.nt.Container(n=self.name)
        self.container.iconName.set(self.icon)
        if self.content_root_node:
            self.container_content_root = pmc.createNode(
                "transform", n=self.container_content_root_name
            )
            self.container.addNode(
                self.container_content_root, ish=True, ihb=True, iha=True, inc=True
            )
        for attr_ in self.container_attr_list:
            attributes.add_attr(node=self.container, **attr_)
        if meta_nd:
            self.meta_nd = meta.ContainerMetaNode(n=self.meta_nd_name)
            self.meta_nd.rename(
                strings.normalize_suffix_1(self.meta_nd.name(), _LOGGER)
            )
            self.meta_nd.add_container_node(self.container)
            self.container.addNode(self.meta_nd)
            self.set_uuid()

    def create_transform(self, name):
        """
        Create a simple transform as container part.

        Args:
            name(str): Transform name.

        """
        self.container_content[name] = pmc.createNode("transform", n=name)
        self.container.addNode(
            self.container_content[name], ish=True, ihb=True, iha=True, inc=True
        )
        if self.content_root_node:
            self.container_content_root.addChild(self.container_content[name])

    def create_container_content_from_list(self, list):
        """
        Create the transform container content from list
        
        Args:
            list(list): List of string.

        Returns:
            False if fail.

        """
        for str_ in list:
            if not isinstance(str_, str):
                logger.log(
                    "error",
                    "Only string as list content allowed.",
                    self.create_container_content_from_list(),
                    logger=_LOGGER,
                )
                return False
            self.create_transform(str_)

    def get_container_content(self):
        """
        Get the container nodes and store them in a dictionary.
        """
        container_nodes = self.container.getNodeList()
        for node in container_nodes:
            self.container_content[node.nodeName()] = node

    def add_node_to_container_content(self, node, content_name):
        """
        Add node to container content

        Args:
            node(pmc.PyNode()): The node to add.
            content_name(str): The content node.

        """
        self.container.addNode(node, ish=True, ihb=True, iha=True, inc=True)
        self.container_content.get(content_name).addChild(node)

    def set_uuid(self, uuid_=None):
        """
        Set the JoMRS uuid string

        Args:
            uuid_(str): The uuid string

        """
        if not uuid_:
            uuid_ = "{}-{}".format(
                str(uuid.uuid4()), constants.CONTAINER_UUID_SUFFIX
            )
        self.meta_nd.set_uuid(uuid_)

    def get_uuid(self):
        """
        Get the JoMRS uuid from meta

        Returns:
            String: The given uuid.

        """
        return self.meta_nd.get_uuid()

    def get_meta_nd(self):
        """
        Get the meta node.

        Returns:
            pmc.PyNode(): The connected meta node. None if not found

        """
        try:
            self.meta_nd = self.container.attr(
                constants.CONTAINER_META_ND_ATTR_NAME
            ).get()
            return self.meta_nd
        except:
            return
