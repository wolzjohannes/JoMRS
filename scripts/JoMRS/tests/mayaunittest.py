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
# Date:       2019 / 08 / 17

"""
Module for python unittest for maya.

Example usage:
# test_sample.py.
from tests.mayaunittest import TestCase
class SampleTests(TestCase):
    def test_create_sphere(self):
        sphere = cmds.polySphere(n='mySphere')[0]
        self.assertEqual('mySphere', sphere)
#The file has to be placed here: scripts/JoMRS/tests

# To run just this test case in Maya
import tests.mayaunittest as unit
unit.run_tests(test='test_sample.SampleTests')

# To run an individual test in a test case
unit.run_tests(test='test_sample.SampleTests.test_create_sphere')

# To run all tests
unit.run_tests()
"""
import os
import logging
import logger
import unittest
import sys
import uuid
import tempfile
import shutil
import maya.cmds as cmds

##########################################################
# GLOBALS
##########################################################

module_logger = logging.getLogger(__name__ + ".py")
JoMRS_TESTING_VAR = "JoMRS_UNITTEST"

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
        logger.log(
            level="error",
            message="Directory for unittest not " "exist",
            logger=module_logger,
        )


def get_tests(directory=None, test=None, test_suite=None):
    """
    Get all unittests in a directory. By default it finds all test in the
    directory of this file.
    Args:
            directory(str): Optional directory to find a tes.
            test(str): The name of the unittest.
            test_suite(PyObject): The test suite.
    Return:
            The found tests as new test_suite.
    """

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


def run_tests(directories=None, test=None, test_suite=None):
    """
    Run all the tests in the given paths.
    Args:
            directories(gen or list): A generator or list of paths containing
            tests to run.
            test(str): Optional name of a specific test to run.
            test_suite(PyObject): Optional TestSuite to run. If omitted,
            a TestSuite will be generated.
    """
    if test_suite is None:
        test_suite = get_tests(directories, test)

    runner = unittest.TextTestRunner(verbosity=2, resultclass=TestResult)
    runner.failfast = False
    runner.buffer = Settings.buffer_output
    runner.run(test_suite)


def run_tests_from_commandline():
    """
    Runs the tests in Mayapy standalone mode.

    This is called when running tests/mayapyunittest.py from the commandline.
    """
    import maya.standalone
    maya.standalone.initialize()
    run_tests()


class Settings(object):
    """
    Contains options for running tests.
    """

    # Specifies where files generated during tests should be stored
    # Use a uuid subdirectory so tests that are running concurrently
    # such as on a build server
    # do not conflict with each other.
    temp_dir = os.path.join(
        tempfile.gettempdir(), "mayaunittest", str(uuid.uuid4())
    )

    # Controls whether temp files should be deleted after running all
    # tests in the test case
    delete_files = True

    # Specifies whether the standard output and standard error streams
    # are buffered during the test run.
    # Output during a passing test is discarded. Output is echoed normally
    # on test fail or error and is
    # added to the failure messages.
    buffer_output = True

    # Controls whether we should do a file new between each test case
    file_new = True

class TestCase(unittest.TestCase):
    """
    Base class for unit test cases run in Maya.

    Tests do not have to inherit from this TestCase but this derived TestCase
    contains convenience
    functions to load/unload plug-ins and clean up temporary files.
    """

    # Keep track of all temporary files that were created so
    # they can be cleaned up after all tests have been run
    files_created = []

    # Keep track of which plugins were loaded so we can unload
    # them after all tests have been run
    plugins_loaded = set()

    @classmethod
    def tearDownClass(cls):
        super(TestCase, cls).tearDownClass()
        cls.delete_temp_files()
        cls.unload_plugins()

    @classmethod
    def load_plugin(cls, plugin):
        """
        Load the given plug-in and saves it to be unloaded when the
        TestCase is finished.
        Args:
                plugin: Plug-in name.
        """
        cmds.loadPlugin(plugin, qt=True)
        cls.plugins_loaded.add(plugin)

    @classmethod
    def unload_plugins(cls):
        # Unload any plugins that this test case loaded
        for plugin in cls.plugins_loaded:
            cmds.unloadPlugin(plugin)
        cls.plugins_loaded = []

    @classmethod
    def delete_temp_files(cls):
        """
        Delete the temp files in the cache and clear the cache.
        """
        # If we don't want to keep temp files around for debugging purposes,
        # delete them when all tests in this TestCase have been run
        if Settings.delete_files:
            for f in cls.files_created:
                if os.path.exists(f):
                    os.remove(f)
            cls.files_create = []
            if os.path.exists(Settings.temp_dir):
                shutil.rmtree(Settings.temp_dir)

    @classmethod
    def get_temp_filename(cls, file_name):
        """
        Get a unique filepath name in the testing directory.
        The file will not be created, that is up to the caller.
        This file will be deleted when
        the tests are finished.
        Args:
                file_name(str): A partial path ex: 'directory/somefile.txt'
        Return:
                The full path to the temporary file.
        """
        temp_dir = Settings.temp_dir
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        base_name, ext = os.path.splitext(file_name)
        path = "{0}/{1}{2}".format(temp_dir, base_name, ext)
        count = 0
        while os.path.exists(path):
            # If the file already exists, add an incrememted number
            count += 1
            path = "{0}/{1}{2}{3}".format(temp_dir, base_name, count, ext)
        cls.files_created.append(path)
        return path

    def assertListAlmostEqual(self, first, second, places=7, msg=None, delta=None):
        """Asserts that a list of floating point values is almost equal.

        unittest has assertAlmostEqual and assertListEqual
        but no assertListAlmostEqual.
        """
        self.assertEqual(len(first), len(second), msg)
        for a, b in zip(first, second):
            self.assertAlmostEqual(a, b, places, msg, delta)

    def tearDown(self):
        if Settings.file_new and JoMRS_TESTING_VAR not in os.environ.keys():
            # If running tests without the custom runner,
            # like with PyCharm, the file new of the TestResult class isn't
            # used so call file new here
            cmds.file(f=True, new=True)

class TestResult(unittest.TextTestResult):
    """
    Customize the test result so we can do things like do a file new
    between each test and suppress script
    editor output.
    """

    def __init__(self, stream, descriptions, verbosity):
        super(TestResult, self).__init__(stream, descriptions, verbosity)
        self.successes = []

    def startTestRun(self):
        """Called before any tests are run."""
        super(TestResult, self).startTestRun()
        # Create an environment variable that specifies tests are
        # being run through the custom runner.
        os.environ[JoMRS_TESTING_VAR] = "1"

        ScriptEditorState.suppress_output()
        if Settings.buffer_output:
            # Disable any logging while running tests. By disabling
            # critical, we are disabling logging
            # at all levels below critical as well
            logging.disable(logging.CRITICAL)

    def stopTestRun(self):
        """Called after all tests are run."""
        if Settings.buffer_output:
            # Restore logging state
            logging.disable(logging.NOTSET)
        ScriptEditorState.restore_output()
        if Settings.delete_files and os.path.exists(Settings.temp_dir):
            shutil.rmtree(Settings.temp_dir)

        del os.environ[JoMRS_TESTING_VAR]

        super(TestResult, self).stopTestRun()

    def stopTest(self, test):
        """Called after an individual test is run.
        Args:
                test: TestCase that just ran."""
        super(TestResult, self).stopTest(test)
        if Settings.file_new:
            cmds.file(f=True, new=True)

    def addSuccess(self, test):
        """Override the base addSuccess method so we can store a list of the
        successful tests.
        Args:
                test: TestCase that successfully ran."""
        super(TestResult, self).addSuccess(test)
        self.successes.append(test)


class ScriptEditorState(object):
    """
    Provides methods to suppress and restore script editor output.
    """

    # Used to restore logging states in the script editor
    suppress_results = None
    suppress_errors = None
    suppress_warnings = None
    suppress_info = None

    @classmethod
    def suppress_output(cls):
        """Hides all script editor output."""
        if Settings.buffer_output:
            cls.suppress_results = cmds.scriptEditorInfo(
                q=True, suppressResults=True
            )
            cls.suppress_errors = cmds.scriptEditorInfo(
                q=True, suppressErrors=True
            )
            cls.suppress_warnings = cmds.scriptEditorInfo(
                q=True, suppressWarnings=True
            )
            cls.suppress_info = cmds.scriptEditorInfo(
                q=True, suppressInfo=True
            )
            cmds.scriptEditorInfo(
                e=True,
                suppressResults=True,
                suppressInfo=True,
                suppressWarnings=True,
                suppressErrors=True,
            )

    @classmethod
    def restore_output(cls):
        """Restores the script editor output settings to
        their original values."""
        if None not in {
            cls.suppress_results,
            cls.suppress_errors,
            cls.suppress_warnings,
            cls.suppress_info,
        }:
            cmds.scriptEditorInfo(
                e=True,
                suppressResults=cls.suppress_results,
                suppressInfo=cls.suppress_info,
                suppressWarnings=cls.suppress_warnings,
                suppressErrors=cls.suppress_errors,
            )


if __name__ == "__main__":
    run_tests_from_commandline()
