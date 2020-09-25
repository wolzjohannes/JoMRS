import pymel.core as pmc
import components.main as main
import components.single_control.create as create

#selected = main.selected()
global_op = create.Main('global', 'M', 0)
global_op._init_operator()

root_op = create.Main('root', 'M', 0, main_operator_node=global_op.main_op_nd)
root_op._init_operator()
root_op.main_op_nd.translate.set(0, 10, 0)
root_op.set_control_shape('sphere')

L_arm_op = create.Main(name='arm', side='L', index=0, main_operator_node=root_op.main_op_nd)
L_arm_op._init_operator()
L_arm_op.main_op_nd.translate.set(10, 5, 0)
L_arm_op.set_control_shape('pyramide')

R_arm_op = create.Main(name='arm', side='R', index=0, main_operator_node=root_op.main_op_nd)
R_arm_op._init_operator()
R_arm_op.main_op_nd.translate.set(-10, 5, 0)
R_arm_op.set_control_shape('pyramide')