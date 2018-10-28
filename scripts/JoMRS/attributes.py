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
# Date:       2018 / 10 / 12

"""
JoMRS attributes module. Module for attributes handling.
"""

import pymel.core as pmc
import pymel.core.datatypes as pmcDT
import logger

moduleLogger = logging.getLogger(__name__ + '.py')

def addAttr(node,name,attrType,defaultValue=None,minVaue=None,max=None,keyable=True,displayable=True,channelBox=True,input=None,output=None):
    if node.hasAttr(name):
        logger.log(level='error',message=name+' attribute already exist',logger=moduleLogger)
        return

    dataDic = {}

    if attrType == 'string':
        dataDic['dataType'] = attrType
    else:
        dataDic['attributeType'] = attrType
    if minValue:
        dataDic['minValue'] = minVaue

