# Python imports
import glob
import sys
import os
import shutil
import getpass

# Maya imports
import maya.cmds as cmds
import maya.mel as mel
import maya.utils as mut


def JoMRS_startup():
    os.environ['JoMRS'] = '/Users/natalijohanneswolz/Projects/JoMRS'
    JoMRS = os.environ['JoMRS'] 
    JoMRS_maya_tools = os.path.join (JoMRS)
    script_path = mel.eval( 'getenv "PHYTONPATH"')
    new_script_path = []

    for path in glob.glob(JoMRS_maya_tools + '/scripts/*'):
        modified_path = os.path.normpath (path).replace ('\\', '/')
        sys.path.insert(0, modified_path)
        script_path = ":".join( (script_path, modified_path) )
        new_script_path = script_path
    script_path = mel.eval( 'getenv "PYTHONPATH"')
    script_path += new_script_path
    os.environ["PYTHONPATH"] = script_path
    print "JoMRS_LOAD_OK"

JoMRS_startup()
