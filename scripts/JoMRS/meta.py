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
TAG = 'node_type'
NODEID = 'meta_node'
##########################################################
# CLASSES
##########################################################


import pymel.core as pmc
from pymel.internal.factories import virtualClasses

class MetaClass(pmc.nt.Network):
    """ this is an example of how to create your own subdivisions of existing nodes. """
    @classmethod
    def list(cls,*args,**kwargs):
        """ Returns all instances the node in the scene """

        kwargs['type'] = cls.__melnode__
        return [ node for node in pmc.ls(*args,**kwargs) if isinstance(node,
                                                                       cls)]
    @classmethod
    def _isVirtual( cls, obj, name, tag=TAG, tag_string=NODEID):
        """PyMEL code should not be used inside the callback, only API and maya.cmds. """
        fn = pmc.api.MFnDependencyNode(obj)
        try:
            if fn.hasAttribute(tag):
                plug = fn.findPlug(tag)
                if plug.asString() == tag_string:
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
    def _postCreateVirtual(cls, newNode, tag=TAG, tag_string=NODEID):
        """ This is called before creation, pymel/cmds allowed."""
        newNode.addAttr('myName', dt='string')

        newNode.addAttr(tag, dt='string')
        newNode.attr(tag).set(tag_string)

        newNode.addAttr('myFloat', at='float')
        newNode.myFloat.set(.125)

        newNode.addAttr('myConnection', at='message')

virtualClasses.register( MetaClass, nameRequired=False )
