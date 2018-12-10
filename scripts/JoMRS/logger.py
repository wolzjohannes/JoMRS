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
# Date:       2018 / 12 / 09

"""
JoMRS logger module. Module which contains
a standart to return and log informations.
"""

##########################################################
# GLOBAL
##########################################################
import os
import logging
import inspect
import datetime

VERSION = ['1', '0', '0']
DATE = ['2018', '12', '09']

logging.basicConfig(level=logging.INFO)


def getVersion(version=VERSION, date=DATE):
    """Get System Version and last update date.
    Args:
            version(list): The list with the version strings.
            date(list): The list with the date strings.
    Return:
            The version info as string.

    """
    return "JoMRS v{} Modular Rigging System | last update {}".format(".".join([i for i in version]), "/".join([x for x in date]))


def initialize_fileHandler(dir_path=os.path.dirname(os.path.realpath(__file__)), dateTime=datetime.datetime.now()):
    """Initialize the filehandler to write a log file for any logger.
    Args:
            dir_path(str): The dir path of the python package.
            datetime(int): The actual date.
    """
    fileName = '{}.log'.format(
        '-'.join([str(dateTime.year), str(dateTime.month), str(dateTime.day)]))
    fileHandlerPath = '{}/logFiles/{}'.format(dir_path, fileName)
    hdlr = logging.FileHandler(fileHandlerPath)
    formatter = logging.Formatter(
        '%(levelname)s:%(asctime)s:%(name)s:%(message)s')
    hdlr.setFormatter(formatter)
    hdlr.setLevel(logging.ERROR)
    logging.getLogger('').addHandler(hdlr)


def _runTime(func):
    """Gives the runTime of a function back
    Args:
            func(func): The function to pass through.
    Return:
            The result of the inner function.
    """
    startTime = datetime.datetime.now()
    result = func
    endTime = datetime.datetime.now()
    return endTime - startTime


def _functionName(func):
    """Gives the name of the function
    Args:
            func(func): The function to pass through.
    Return:
            The function as string.
    """
    return 'Calling the function: def {}()'.format(func.__name__)


def log(level='info', message='', func=None, logger=None):
    """Main logger function to costumize the python logging function.
    Args:
            level(str): The level of the log.
            message(str): The message to pass through.
            func(function): The function to pass through.
    """
    if not logger:
        logger = logging
    if level == 'info':
        if func:
            func_name = _functionName(func)
            logger.info("{} | {} | {}".format(
                message, func_name, str(inspect.getdoc(func))))
        else:
            logger.info(message)
    elif level == 'debug':
        if func:
            func_name = _functionName(func)
            run_time = _runTime(func)
            logger.debug("{} | {} | RUNTIME: {} | {}".format(
                message, func_name, run_time, str(inspect.getargspec(func))))
        else:
            logger.debug(message)
    elif level == 'warning':
        if func:
            func_name = _functionName(func)
            run_time = _runTime(func)
            logger.warning("Something unexpected happend : {} | {} | RUNTIME: {} | {}".format(
                message, func_name, run_time, str(inspect.getargspec(func))))
        else:
            logger.warning("Something unexpected happend : {}".format(message))
    elif level == 'error':
        if func:
            func_name = _functionName(func)
            run_time = _runTime(func)
            logger.error("Serious Shit : {} | {} | RUNTIME: {} | {}".format(
                message, func_name, run_time, str(inspect.getargspec(func))))
        else:
            logger.error("Serious Shit : {}".format(message))
    elif level == 'critical':
        if func:
            func_name = _functionName(func)
            run_time = _runTime(func)
            logger.critical("UPS you deleted the internet : {} | {} | RUNTIME: {} | {}".format(
                message, func_name, run_time, str(inspect.getargspec(func))))
        else:
            logger.critical("You deleted the internet : {}".format(message))


def functionName(func):
    """Gives the name of the function
    Args:
            func(func): The function to pass through.
    Return:
            The function as string.
    """
    return log(level='info', message=_functionName(func))


def runTimeWrapper(func):
    """Decorator to record the runtime of a function.
    Args:
            func(func): The function to pass through.
    Return:
            The inner function.
    """
    def inner(*args, **kwargs):
        startTime = datetime.datetime.now()
        result = func(*args, **kwargs)
        endTime = datetime.datetime.now()
        result = endTime - startTime
        log(level='info', message="RUNTIME: {}".format(result))
    return inner
