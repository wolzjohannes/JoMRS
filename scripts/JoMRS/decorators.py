# Copyright (c) 2022 Johannes Wolz

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Author:     Johannes Wolz / Rigging TD
# Date:       2022 / 08 / 08

"""
Helpful decorators module.
"""

# Import python standart import
from functools import wraps
import logging

# Import Maya specific modules
import pymel.core as pmc

##########################################################
# GLOBAL
##########################################################

_LOGGER = logging.getLogger(__name__ + ".py")
_LOGGER.setLevel(0)

##########################################################
# CLASSES
##########################################################


class Decorators(object):
    def __init__(self):
        """
        Decorator class. Inherits decorators methods which can be useful in
        other packages.
        """
        self.debug = True
        self.logger = _LOGGER

    def x_timer(self, func):
        """
        Decorator which gives you back the execution time of an function
        in maya. Output can only been seen in debug mode. For that you need
        to set the self.debug class variable to True.

        Args:
            func(python object): The function to track the execution time for.

        Return:
            Func: Returns the wrapped function.

        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            start = pmc.timerX()
            result = func(*args, **kwargs)
            total_time = pmc.timerX(st=start)
            if self.debug:
                self.logger.setLevel(logging.DEBUG)
            self.logger.debug(
                "Func/Method: {}(). Executed in [{}]".format(
                    func_name, total_time
                )
            )
            return result

        return wrapper

    def undo(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with pmc.UndoChunk():
                result = func(*args, **kwargs)
            return result
        return wrapper
