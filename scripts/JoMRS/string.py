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
# Date:       2018 / 10 / 11

"""
JoMRS string module. Module for string handling and naming conventions.
"""

##########################################################

##########################################################

import re
import logging
import logger
reload(logger)

moduleLogger = logging.getLogger(__name__ + '.py')


def normalizePrefix(string):
    """
    Normalize the string start. It cut offs the first letter and
    put a '_' inbetween.
    Args:
            string(str): The string you want to normalize the start.
    Return:
            The string with the normalized start.
    """
    string = str(string)

    if not re.match("[0-9]", string):
        if not re.match("^[lrmnLRMN]_", string):
            newString = string[0].upper() + '_' + string[1:]
            return newString
        return string
    logger.log(level='warning', message='Prefix has a number',
               logger=moduleLogger)
    return string


def replaceInvalidPrefix(string):
    """
    Replace invalid side start characters of a string and replace it.
    Args:
            string(str): The string you want to prepare.
    Return:
            The string with the new replaced start character.
    """
    string = str(string)

    if re.match("^[MRL]_", string):
        return string
    if not re.match("^[MRL]_", string):
        logger.log(
            level='warning', message='Prefix should specifide a side',
            logger=moduleLogger)
    rePattern = re.compile(
        "_[lrmn]+_|_[LRMN]+_|^[lrmnLRMN]_+|_[lrmnLRMN][0-9]+_|^[0-9][lrmnLRMN]_+|^[lrmnLRMN][0-9]_|_[0-9][lrmnLRMN]_")
    reMatch = re.search(rePattern, string)
    if reMatch:
        instance = reMatch.group(0)
        # try to find if a number exist besides the character and remove it.
        instance_ = re.search("[0-9]", instance)
        if instance_:
            instance_ = instance_.group(0)
            if instance.find(instance_) != -1:
                instance__ = instance.replace(instance_, '')
                string = string.replace(instance, instance__)
                instance = instance__
        # remove the instance of [lrmnLRMN] and so on.
        # And put it at the beginning of the string.
        string = string.replace(instance, '_')
        if re.search('[Rr]', instance):
            string = 'R{}'.format(string)
        elif re.search('[Ll]', instance):
            string = 'L{}'.format(string)
        elif re.search('[MmNn]', instance):
            string = 'M{}'.format(string)
        if not re.match("^[MRL]_", string):
            side = string[0]
            string = '{}_{}'.format(side, string[1:])
    return string


def replaceHashWithPadding(string, index):
    """
    Replace the symbol '#' with a number count. Starts with the index.
    Args:
            string(str): The srting to work with.
            index(int): The index to replace.
    Return:
            The new created string.
    """
    if string.count("#") == 0:
        string += "#"

    digit = str(index)
    while len(digit) < string.count("#"):
        digit = "0" + digit

    return re.sub("#+", digit, string)


def normalizeSuffix(string):
    """
    Replace numbers in the suffix with a ''.
    And if the suffix is lowercase it will turn it uppercase.
    Args:
            string(str): The string to work with
    Return:
            The new created string.
    """
    if re.search("[A-Z]{1,}$", string):
        return string
    numbers = re.search("[0-9]{1,}$", string)
    if numbers:
        instance = numbers.group(0)
        string = string[0:string.find(instance)]
        logger.log(
            level='warning', message='Suffix should not have a number',
            logger=moduleLogger)
    lowerCase = re.search("[a-z]{1,}$", string)
    if lowerCase:
        instance_ = lowerCase.group(0)
        string = string[0:string.find(instance_)] + instance_.upper()
    return string


def normalizeNumbers(string):
    """
    Finds the numbers in the string and move them to the correct
    position in the string.
    Args:
            string(str): The string to work with.
    Return:
            The new created string.
    """
    if re.search("_[0-9]{1,}_[A-Za-z]{1,}$", string):
        return string
    numbers = re.search("_[0-9]{1,}_", string)
    if numbers:
        instance = numbers.group(0)
        stringEnd = string[string.find(
            instance) + len(instance):].split('_')[-1]
        string = string.replace(instance, '_')
        string = string.replace('_' + stringEnd, instance + stringEnd)
    return string
