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
Module for python unittest via mayapy. Has to be executed from commandline.
"""

import os
import platform
import argparse
import subprocess
import tempfile
import shutil
import uuid


##########################################################
# GLOBALS
##########################################################

DIRPATH = os.path.dirname(os.path.realpath(__file__))
JOMRS = os.path.dirname(DIRPATH.split("scripts")[0])

##########################################################
# FUNCTIONS
##########################################################


def get_maya_location(maya_version):
    """
    Get the location where Maya is installed.
    Args:
            maya_version(str:) The maya version number.
    Return:
            The path to where Maya is installed.
    """
    if "MAYA_LOCATION" in os.environ.keys():
        return os.environ["MAYA_LOCATION"]
    if platform.system() == "Windows":
        return "C:/Program Files/Autodesk/Maya{0}".format(maya_version)
    elif platform.system() == "Darwin":
        return "/Applications/Autodesk/maya{0}/Maya.app/Contents".format(
            maya_version
        )
    else:
        location = "/usr/autodesk/maya{0}".format(maya_version)
        if maya_version < 2018:
            # Starting Maya 2018, the default install directory name changed.
            location += "-x64"
        return location


def mayapy(maya_version):
    """
    Get the mayapy executable path.
    Args:
            maya_version(str:) The maya version number.
    Return:
            The mayapy executable path.
    """
    python_exe = "{0}/bin/mayapy".format(get_maya_location(maya_version))
    if platform.system() == "Windows":
        python_exe += ".exe"
    return python_exe


def create_clean_maya_app_dir(directory=None):
    """
    Creates a copy of the clean Maya preferences
    so we can create predictable results.
    Args:
            directory(str): The directory for the clean app dir.
    Return:
            The path to the clean MAYA_APP_DIR folder.
    """
    app_dir = os.path.join(DIRPATH, "clean_maya_app_dir")
    temp_dir = tempfile.gettempdir()
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    dst = (
        directory
        if directory
        else os.path.join(
            temp_dir, "maya_app_dir{0}".format(str(uuid.uuid4()))
        )
    )
    if os.path.exists(dst):
        shutil.rmtree(dst, ignore_errors=False, onerror=remove_read_only)
    shutil.copytree(app_dir, dst)
    return dst


def remove_read_only(func, path, exc):
    """
    Called by shutil.rmtree when it encounters a readonly file.
    Args:
            func(function).
            path(str).
            exc().
    """
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise RuntimeError("Could not remove {0}".format(path))


def main(default_maya_version=2018):
    """
    Runs the maya unit test via mayapy.
    It calls the mayaunitest.py and pass it to mayapy with clean maya prefs.
    Args:
                default_maya_version(int): The maya version.
    Return:
                The clean maya_app_dir directory.
    """
    parser = argparse.ArgumentParser(
        description="Runs unit tests for a Maya module"
    )
    parser.add_argument(
        "-m",
        "--maya",
        help="Maya version",
        type=int,
        default=default_maya_version,
    )
    parser.add_argument(
        "-mad",
        "--maya-app-dir",
        help="Just create a clean MAYA_APP_DIR and exit",
    )
    pargs = parser.parse_args()
    mayaunittest = os.path.join(DIRPATH, "mayaunittest.py")
    cmd = [mayapy(pargs.maya), mayaunittest]
    if not os.path.exists(cmd[0]):
        raise RuntimeError(
            "Maya {0} is not installed on this system.".format(pargs.maya)
        )
    app_directory = pargs.maya_app_dir
    maya_app_dir = create_clean_maya_app_dir(app_directory)
    if app_directory:
        return
    # Create clean prefs and env
    os.environ["MAYA_APP_DIR"] = maya_app_dir
    os.environ["MAYA_SCRIPT_PATH"] = os.path.join(JOMRS, "scripts", "JoMRS")
    os.environ["MAYA_MODULE_PATH"] = ""
    os.environ["JoMRS"] = JOMRS
    os.environ["PYTHONPATH"] = os.path.join(JOMRS, "scripts", "JoMRS")
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        pass
    finally:
        shutil.rmtree(maya_app_dir)


if __name__ == "__main__":
    main()
