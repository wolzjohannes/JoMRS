"""Creates a node network to extract twist rotation of a transform to drive another
transform.

The network calculates the local rotation twist offset around a specified twist axis
relative to the local rest orientation.  This allows users to specify how much
twist they want to propagate to another transform.  Uses include driving an upper arm
twist joint from the shoulder and driving forearm twist joints from the wrist.

Since the network uses quaternions, partial twist values between 0.0 and 1.0 will see a
flip when the driver transform rotates past 180 degrees.

Example Usage
=============
The twist decomposition network can be accessed in the cmt menu::

    CMT > Rigging > Connect Twist Joint

Twist child of shoulder::

    shoulder
      |- twist_joint1
      |- twist_joint2
      |- elbow

    create_twist_decomposition(shoulder, twist_joint1, invert=True)
    create_twist_decomposition(shoulder, twist_joint2, invert=True, twist_weight=0.5)

Twist forearm from wrist::

    elbow
      |- twist_joint1
      |- twist_joint2
      |- wrist

    create_twist_decomposition(wrist, twist_joint1, invert=False, twist_weight=0.5)
    create_twist_decomposition(wrist, twist_joint2, invert=False)
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya

from cmt.ui.optionbox import OptionBox
from cmt.settings import DOCUMENTATION_ROOT
import cmt.shortcuts as shortcuts

logger = logging.getLogger(__name__)

# User defined attribute names used in the network
REST_MATRIX = "restMatrix"
TWIST_WEIGHT = "twistWeight"
TWIST_OUTPUT = "twistOutput"
INVERTED_TWIST_OUTPUT = "invertedTwistOutput"

HELP_URL = "{}/rig/twistdecomposition.html".format(DOCUMENTATION_ROOT)


def create_twist_decomposition(
    driver, driven, invert, twist_weight=1.0, twist_axis=None
):
    """Create a node network to drive a transforms rotation from the decomposed twist of
    another transform.

    :param driver: Driver transform
    :param driven: Driven transform
    :param invert: True to invert the twist
    :param twist_weight: 0-1 twist scalar
    :param twist_axis: Local twist axis on driver such as (1.0, 0.0, 0.0).  If not
        specified, the twist axis will be calculated as the vector to the first child.
        If the driver has no children, the twist axis will be (1.0, 0.0, 0.0).
    """
    if not _twist_network_exists(driver):
        _create_twist_decomposition_network(driver, twist_axis)
    if not cmds.objExists("{}.{}".format(driven, TWIST_WEIGHT)):
        cmds.addAttr(
            driven,
            ln=TWIST_WEIGHT,
            keyable=True,
            minValue=0,
            maxValue=1,
            defaultValue=twist_weight,
        )

    twist_attribute = _get_decomposed_twist_attribute(driver, invert, twist_axis)

    twist_slerp = cmds.createNode("quatSlerp", name="{}_twist_slerp".format(driven))
    cmds.connectAttr(
        "{}.{}".format(driven, TWIST_WEIGHT), "{}.inputT".format(twist_slerp)
    )
    cmds.setAttr("{}.input1QuatW".format(twist_slerp), 1)
    cmds.connectAttr(twist_attribute, "{}.input2Quat".format(twist_slerp))

    twist_euler = cmds.createNode("quatToEuler", name="{}_twist_euler".format(driven))
    cmds.connectAttr(
        "{}.outputQuat".format(twist_slerp), "{}.inputQuat".format(twist_euler)
    )
    cmds.connectAttr(
        "{}.rotateOrder".format(driven), "{}.inputRotateOrder".format(twist_euler)
    )
    cmds.connectAttr("{}.outputRotate".format(twist_euler), "{}.rotate".format(driven))
    logger.info(
        "Created twist decomposition network to drive {} from {}".format(driven, driver)
    )


def _twist_network_exists(driver):
    """Test whether the twist decomposition network already exists on driver.

    :param driver: Driver transform
    :return: True or False
    """
    has_twist_attribute = cmds.objExists("{}.{}".format(driver, TWIST_OUTPUT))
    if not has_twist_attribute:
        return False
    twist_node = cmds.listConnections("{}.{}".format(driver, TWIST_OUTPUT), d=False)
    return True if twist_node else False


def _create_twist_decomposition_network(driver, twist_axis):
    """Create the twist decomposition network for driver.

    :param driver: Driver transform
    :param twist_axis: Local twist axis on driver
    """
    # Connect message attributes to the decomposed twist nodes so we can reuse them
    # if the network is driving multiple nodes
    if not cmds.objExists("{}.{}".format(driver, TWIST_OUTPUT)):
        cmds.addAttr(driver, ln=TWIST_OUTPUT, at="message")
    if not cmds.objExists("{}.{}".format(driver, INVERTED_TWIST_OUTPUT)):
        cmds.addAttr(driver, ln=INVERTED_TWIST_OUTPUT, at="message")

    # Store the current local matrix of driver to be used as a frame of reference
    if not cmds.objExists("{}.{}".format(driver, REST_MATRIX)):
        cmds.addAttr(driver, ln=REST_MATRIX, at="matrix")
    rest_matrix = cmds.getAttr("{}.m".format(driver))
    cmds.setAttr("{}.restMatrix".format(driver), rest_matrix, type="matrix")
    # Get the local offset matrix which is the matrix from the world rest xform to
    # the current world xform
    world_rest_matrix = cmds.createNode(
        "multMatrix", name="{}_world_rest_matrix".format(driver)
    )
    for i, attr in enumerate(["parentMatrix[0]", REST_MATRIX]):
        cmds.connectAttr(
            "{}.{}".format(driver, attr), "{}.matrixIn[{}]".format(world_rest_matrix, i)
        )
    world_rest_inverse = cmds.createNode(
        "inverseMatrix", name="{}_world_rest_inverse".format(driver)
    )
    cmds.connectAttr(
        "{}.matrixSum".format(world_rest_matrix),
        "{}.inputMatrix".format(world_rest_inverse),
    )
    local_offset_matrix = cmds.createNode(
        "multMatrix", name="{}_local_offset_matrix".format(driver)
    )
    cmds.connectAttr(
        "{}.worldMatrix[0]".format(driver), "{}.matrixIn[0]".format(local_offset_matrix)
    )
    cmds.connectAttr(
        "{}.outputMatrix".format(world_rest_inverse),
        "{}.matrixIn[1]".format(local_offset_matrix),
    )
    # Transform the twist axis by the local offset matrix
    if twist_axis is None:
        twist_axis = _get_local_twist_axis(driver)
    local_twist_axis = cmds.createNode(
        "vectorProduct", name="{}_twist_axis".format(driver)
    )
    cmds.setAttr("{}.operation".format(local_twist_axis), 3)  # Vector Matrix Product
    cmds.setAttr("{}.input1".format(local_twist_axis), *twist_axis)
    cmds.connectAttr(
        "{}.matrixSum".format(local_offset_matrix), "{}.matrix".format(local_twist_axis)
    )
    cmds.setAttr("{}.normalizeOutput".format(local_twist_axis), True)
    # Get the angle between the rest and transformed twist axis to get the swing
    # rotation
    swing_euler = cmds.createNode("angleBetween", name="{}_swing_euler".format(driver))
    cmds.connectAttr(
        "{}.input1".format(local_twist_axis), "{}.vector1".format(swing_euler)
    )
    cmds.connectAttr(
        "{}.output".format(local_twist_axis), "{}.vector2".format(swing_euler)
    )
    # Convert the swing euler rotation to quaternion
    swing = cmds.createNode("eulerToQuat", name="{}_swing".format(driver))
    cmds.connectAttr("{}.euler".format(swing_euler), "{}.inputRotate".format(swing))
    # Remove the inverse swing from the local offset to be left with the twist
    swing_inverse = cmds.createNode(
        "quatInvert", name="{}_swing_inverse".format(driver)
    )
    cmds.connectAttr(
        "{}.outputQuat".format(swing), "{}.inputQuat".format(swing_inverse)
    )
    local_rotation = cmds.createNode(
        "decomposeMatrix", name="{}_local_rotation".format(driver)
    )
    cmds.connectAttr(
        "{}.matrixSum".format(local_offset_matrix),
        "{}.inputMatrix".format(local_rotation),
    )
    twist = cmds.createNode("quatProd", name="{}_twist".format(driver))
    cmds.connectAttr(
        "{}.outputQuat".format(local_rotation), "{}.input1Quat".format(twist)
    )
    cmds.connectAttr(
        "{}.outputQuat".format(swing_inverse), "{}.input2Quat".format(twist)
    )
    cmds.connectAttr("{}.message".format(twist), "{}.{}".format(driver, TWIST_OUTPUT))

    twist_inverse = cmds.createNode(
        "quatInvert", name="{}_twist_inverse".format(driver)
    )
    cmds.connectAttr(
        "{}.outputQuat".format(twist), "{}.inputQuat".format(twist_inverse)
    )
    cmds.connectAttr(
        "{}.message".format(twist_inverse),
        "{}.{}".format(driver, INVERTED_TWIST_OUTPUT),
    )


def _get_decomposed_twist_attribute(driver, invert, twist_axis):
    """Get the quaternion output attribute of the twist decomposition network.

    :param driver: Driver transform
    :param invert: True to get the inverted twist attribute
    :param twist_axis: Local twist axis of driver
    :return: The quaternion output attribute
    """
    attribute = INVERTED_TWIST_OUTPUT if invert else TWIST_OUTPUT
    node = cmds.listConnections("{}.{}".format(driver, attribute), d=False)
    if not node:
        # The network isn't connected so create it
        _create_twist_decomposition_network(driver, twist_axis)
        return _get_decomposed_twist_attribute(driver, invert, twist_axis)
    return "{}.outputQuat".format(node[0])


def _get_local_twist_axis(driver):
    """Procedurally calculate and return the local twist axis of driver.

    The twist axis will be the normalized vector to the first child.

    :param driver: Driver transform
    :return: Normalized (x, y, z) vector
    """
    children = cmds.listRelatives(driver, children=True, path=True)
    if not children:
        return 1.0, 0.0, 0.0

    child = children[0]
    p1 = cmds.xform(driver, q=True, ws=True, t=True)
    p1 = OpenMaya.MPoint(*p1)
    p2 = cmds.xform(child, q=True, ws=True, t=True)
    p2 = OpenMaya.MPoint(*p2)

    world_vector = (p2 - p1).normal()
    path = shortcuts.get_dag_path(driver)
    local_vector = world_vector * path.inclusiveMatrixInverse()
    return local_vector.x, local_vector.y, local_vector.z


def create_from_menu(*args, **kwargs):
    sel = cmds.ls(sl=True)
    if len(sel) != 2:
        raise RuntimeError("Select driver transform then driven transform.")
    driver, driven = sel
    kwargs = Options.get_kwargs()
    create_twist_decomposition(driver, driven, **kwargs)


def display_menu_options(*args, **kwargs):
    options = Options("Twist Decomposition Options", HELP_URL)
    options.show()


class Options(OptionBox):
    INVERT_WIDGET = "cmt_twist_invert"
    TWIST_WEIGHT_WIDGET = "cmt_twist_weight"
    TWIST_AXIS_ENABLE_WIDGET = "cmt_twist_auto_axis"
    TWIST_AXIS_WIDGET = "cmt_twist_axis"

    @classmethod
    def get_kwargs(cls):
        """Gets the function arguments either from the option box widgets or the saved
        option vars.  If the widgets exist, their values will be saved to the option
        vars.

        :return: A dictionary of the arguments to the create_twist_decomposition
        function."""
        kwargs = {}
        if cmds.floatSliderGrp(Options.TWIST_WEIGHT_WIDGET, exists=True):
            kwargs["twist_weight"] = cmds.floatSliderGrp(
                Options.TWIST_WEIGHT_WIDGET, q=True, value=True
            )
            cmds.optionVar(fv=(Options.TWIST_WEIGHT_WIDGET, kwargs["twist_weight"]))
        else:
            kwargs["twist_weight"] = cmds.optionVar(q=Options.TWIST_WEIGHT_WIDGET)

        if cmds.checkBoxGrp(Options.INVERT_WIDGET, exists=True):
            value = cmds.checkBoxGrp(Options.INVERT_WIDGET, q=True, v1=True)
            kwargs["invert"] = value
            cmds.optionVar(iv=(Options.INVERT_WIDGET, value))
        else:
            value = cmds.optionVar(q=Options.INVERT_WIDGET)
            kwargs["invert"] = value

        if cmds.checkBoxGrp(Options.TWIST_AXIS_ENABLE_WIDGET, exists=True):
            value = cmds.checkBoxGrp(Options.TWIST_AXIS_ENABLE_WIDGET, q=True, v1=True)
            if value:
                x = cmds.floatFieldGrp(Options.TWIST_AXIS_WIDGET, q=True, v1=True)
                y = cmds.floatFieldGrp(Options.TWIST_AXIS_WIDGET, q=True, v2=True)
                z = cmds.floatFieldGrp(Options.TWIST_AXIS_WIDGET, q=True, v3=True)
                kwargs["twist_axis"] = (x, y, z)
            else:
                kwargs["twist_axis"] = None
            cmds.optionVar(clearArray=Options.TWIST_AXIS_WIDGET)
            if kwargs["twist_axis"]:
                for v in kwargs["twist_axis"]:
                    cmds.optionVar(floatValueAppend=[Options.TWIST_AXIS_WIDGET, v])
        else:
            kwargs["twist_axis"] = cmds.optionVar(q=Options.TWIST_AXIS_WIDGET)

        return kwargs

    def create_ui(self):
        cmds.columnLayout(adj=True)

        for widget in [
            Options.INVERT_WIDGET,
            Options.TWIST_WEIGHT_WIDGET,
            Options.TWIST_AXIS_ENABLE_WIDGET,
            Options.TWIST_AXIS_WIDGET,
        ]:
            # Delete the widgets so we don't create multiple controls with the same name
            try:
                cmds.deleteUI(widget, control=True)
            except RuntimeError:
                pass
        invert_twist = cmds.optionVar(q=Options.INVERT_WIDGET)
        cmds.checkBoxGrp(
            Options.INVERT_WIDGET,
            numberOfCheckBoxes=1,
            label="Invert twist",
            v1=invert_twist,
        )

        twist_weight = cmds.optionVar(q=Options.TWIST_WEIGHT_WIDGET)
        cmds.floatSliderGrp(
            Options.TWIST_WEIGHT_WIDGET,
            label="Twist weight",
            field=True,
            minValue=0.0,
            maxValue=1.0,
            fieldMinValue=0.0,
            fieldMaxValue=1.0,
            value=twist_weight,
            step=0.1,
            precision=2,
        )

        specify_twist_axis = cmds.optionVar(q=Options.TWIST_AXIS_ENABLE_WIDGET)
        cmds.checkBoxGrp(
            Options.TWIST_AXIS_ENABLE_WIDGET,
            numberOfCheckBoxes=1,
            label="Specify twist axis ",
            v1=specify_twist_axis,
            cc=self.on_axis_enable_changed,
        )

        twist_axis = cmds.optionVar(q=Options.TWIST_AXIS_WIDGET)
        twist_axis = twist_axis if twist_axis else (1, 0, 0)
        cmds.floatFieldGrp(
            Options.TWIST_AXIS_WIDGET,
            numberOfFields=3,
            label="Twist axis ",
            v1=twist_axis[0],
            v2=twist_axis[1],
            v3=twist_axis[2],
            enable=specify_twist_axis,
        )

    def on_axis_enable_changed(self, value):
        cmds.floatFieldGrp(Options.TWIST_AXIS_WIDGET, e=True, enable=value)

    def on_apply(self):
        create_from_menu()

    def on_reset(self):
        cmds.floatSliderGrp(Options.TWIST_WEIGHT_WIDGET, e=True, value=1)
        cmds.checkBoxGrp(Options.INVERT_WIDGET, e=True, v1=True)
        cmds.checkBoxGrp(Options.TWIST_AXIS_ENABLE_WIDGET, e=True, v1=False)
        cmds.floatFieldGrp(Options.TWIST_AXIS_WIDGET, e=True, v1=1.0, v2=0.0, v3=0.0)

    def on_save(self):
        Options.get_kwargs()
