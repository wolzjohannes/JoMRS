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
# Date:       2019 / 08 / 11

"""
Module for python unittest via mayapy
"""

import os
import platform
import argparse
import subprocess

##########################################################
# GLOBALS
##########################################################

DIRPATH = os.path.dirname(os.path.realpath(__file__))
JOMRS = os.environ['JoMRS']
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
    if 'MAYA_LOCATION' in os.environ.keys():
        return os.environ['MAYA_LOCATION']
    if platform.system() == 'Windows':
        return 'C:/Program Files/Autodesk/Maya{0}'.format(maya_version)
    elif platform.system() == 'Darwin':
        return '/Applications/Autodesk/maya{0}/Maya.app/Contents'.format(maya_version)
    else:
        location = '/usr/autodesk/maya{0}'.format(maya_version)
        if maya_version < 2018:
            # Starting Maya 2018, the default install directory name changed.
            location += '-x64'
        return location

def mayapy(maya_version):
    """Get the mayapy executable path.

    @param maya_version The maya version number.
    @return: The mayapy executable path.
    """
    python_exe = '{0}/bin/mayapy'.format(get_maya_location(maya_version))
    if platform.system() == 'Windows':
        python_exe += '.exe'
    return python_exe

def main(default=2018):
    parser = argparse.ArgumentParser(description='Runs unit tests for a Maya module')
    parser.add_argument('-m', '--maya',
                        help='Maya version',
                        type=int,
                        default=default)
    pargs = parser.parse_args()
    print pargs.maya
    cmd = [mayapy(pargs.maya)]
    print cmd
    if not os.path.exists(cmd[0]):
        raise RuntimeError('Maya {0} is not installed on this system.'.format(pargs.maya))
    subprocess.check_call(cmd)
    # try:
    #     subprocess.check_call(cmd)
    # except subprocess.CalledProcessError:
    #     pass
    # finally:
    #     shutil.rmtree(maya_app_dir)
    # parser.add_argument('-mad', '--maya-app-dir',
    #                     help='Just create a clean MAYA_APP_DIR and exit')
    # mayaunittest = os.path.join(CMT_ROOT_DIR, 'scripts', 'cmt', 'test', 'mayaunittest.py')

    # app_directory = pargs.maya_app_dir
    # maya_app_dir = create_clean_maya_app_dir(app_directory)
    # if app_directory:
    #     return
    # Create clean prefs
    # os.environ['MAYA_APP_DIR'] = maya_app_dir
    # Clear out any MAYA_SCRIPT_PATH value so we know we're in a clean env.
    # os.environ['MAYA_SCRIPT_PATH'] = ''
    # Run the tests in this module.
    # os.environ['MAYA_MODULE_PATH'] = CMT_ROOT_DIR

if __name__ == '__main__':
    print JOMRS
    main()