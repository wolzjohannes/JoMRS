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
# Date:       2019 / 07 / 02

"""
Meta creation module.
"""
##########################################################
# GLOBALS
#########################################################
NODEID = 'meta_node'
TYPE = 'meta_name'
BASETYPE = 'meta_class'
##########################################################
# CLASSES
##########################################################


import pymel.core as pmc
from pymel.internal.factories import virtualClasses

class MetaClass(pmc.nt.Network):
    """
    Creates a network node which works as MetaClass node.
    """
    @classmethod
    def list(cls,*args,**kwargs):
        """
        Returns all instances of the meta class notes in the scene.
        """

        kwargs['type'] = cls.__melnode__
        return [ node for node in pmc.ls(*args,**kwargs) if isinstance(node,
                                                                       cls)]
    @classmethod
    def _isVirtual( cls, obj, name, tag=NODEID):
        """"
        This actual creates the node. If a specific tag is found.
        If not it will create a default node.
        PyMEL code should not be used inside the callback,
        only API and maya.cmds.
        """
        fn = pmc.api.MFnDependencyNode(obj)
        try:
            if fn.hasAttribute(tag):
                plug = fn.findPlug(tag)
                if plug.asBool() == 1:
                    return True
                return True
        except:
            pass
        return False

    @classmethod
    def _preCreateVirtual(cls, **kwargs):
        """
        This is called before creation. Python allowed.
        """
        return kwargs

    @classmethod
    def _postCreateVirtual(cls, newNode, tag=NODEID,
                           type=TYPE, type_name=BASETYPE):
        """
        This is called after creation, pymel/cmds allowed.
        It will create a set of attributes. And the important check up tag for
        the meta node.
        """
        newNode.addAttr(tag, at='bool')
        newNode.attr(tag).set(1)
        newNode.addAttr(type, dt='string')
        newNode.attr(type).set(type_name)

virtualClasses.register( MetaClass, nameRequired=False )
