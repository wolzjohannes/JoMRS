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
# Base code from Chad Vernon cmt_master.
# Author:     Johannes Wolz / Rigging TD
# Date:       2019 / 08 / 12

"""
Module for python unittest for maya.
"""
import os
import logging
import logger
import unittest
import sys

##########################################################
# GLOBALS
##########################################################

module_logger = logging.getLogger(__name__ + ".py")

##########################################################
# FUNCTIONS
##########################################################

def get_module_tests_path():
    """
    Generator function to get the unittest directory path
    Return:
                Path to unittest directory.
    """
    path = "{0}/scripts/JoMRS/tests".format(os.environ["JoMRS"])
    if os.path.exists(path):
            return path
    else:
        logger.log(level='error', message="Directory for unittest not "
                                          "exist", logger=module_logger)

def get_tests(directory=None, test=None, test_suite=None):

    if directory is None:
        directory = get_module_tests_path()

    if test_suite is None:
        test_suite = unittest.TestSuite()

    if test:
        dir_add_to_syspath = [p for p in [directory] if add_to_syspath(p)]
        discovered_suite = unittest.TestLoader().loadTestsFromName(test)
        if discovered_suite.countTestCases():
            test_suite.addTests(discovered_suite)
    else:
        # Find all tests to run
        dir_add_to_syspath = []
        for p in [directory]:
            discovered_suite = unittest.TestLoader().discover(p)
            if discovered_suite.countTestCases():
                test_suite.addTests(discovered_suite)

    # Remove the added paths.
    for path in dir_add_to_syspath:
        sys.path.remove(path)

    return test_suite

def add_to_syspath(path):
    """
    Add the specified path to the system path.
     Args:
            path(str) Path to add.
    Return:
            True if path was added. Return false if path does not exist or
            path was already in sys.path
    """
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)
        return True
    return False

def run_tests_from_commandline():
    """Runs the tests in Maya standalone mode.

    This is called when running cmt/bin/runmayatests.py from the commandline.
    """
    import maya.standalone

    maya.standalone.initialize()


if __name__ == "__main__":
    run_tests_from_commandline()