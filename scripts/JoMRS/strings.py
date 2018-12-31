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
# Date:       2018 / 12 / 31

"""
JoMRS string module. Module for string handling and naming conventions.
"""

##########################################################
# To Do
# A config file for strings. For projects modifications.
##########################################################

import re
import logging
import logger

moduleLogger = logging.getLogger(__name__ + '.py')


def normalizePrefix(string, logger_=moduleLogger):
    """
    Normalize the string start. It cut offs the first letter and
    put a '_' inbetween.
    Args:
            string(str): The string you want to normalize the start.
            logger_(instance): The logging instance of
            a module.
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
               logger=logger_)
    return string


def replaceInvalidPrefix(string, logger_=moduleLogger):
    """
    Replace invalid side start characters of a string and replace it.
    Args:
            string(str): The string you want to prepare.
            logger_(instance): The logging instance of
            a module.
    Return:
            The string with the new replaced start character.
    """
    string = str(string)

    if re.match("^[MRL]_", string):
        return string
    if not re.match("^[MRL]_", string):
        logger.log(level='warning', message='The string prefix "' +
                   string + '" should specifie a side',
                   logger=logger_)
    numbersMatch = re.match("^[0-9]", string)
    if numbersMatch:
        number = '^' + numbersMatch.group(0)
        string = string.replace(number, '')
        logger.log(level='warning', message='Prefix contains numbers'
                   '. Numbers deleted',
                   logger=logger_)
    rePattern = re.compile("_[lrmn]+_|_[LRMN]+_|^[lrmnLRMN]_+"
                           "|_[lrmnLRMN][0-9]+_|^[0-9][lrmnLRMN]_+"
                           "|^[lrmnLRMN][0-9]_|_[0-9][lrmnLRMN]_")
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


def normalizeSuffix(string, logger_=moduleLogger):
    """
    Replace numbers in the suffix with a ''.
    And if the suffix is lowercase it will turn it uppercase.
    Args:
            string(str): The string to work with
            logger_(instance): The logging instance of
            a module.
    Return:
            The new created string.
    """
    if re.search("_[A-Z]{1,}$", string):
        return string
    numbers = re.search("[0-9]{1,}$", string)
    if numbers:
        logger.log(
            level='warning', message='Suffix of string "' + string +
            '" should not have a number. Numbers removed from the suffix',
            logger=logger_)
        instance = numbers.group(0)
        string = string[0:string.find(instance)]
    lowerCase = re.search("_[a-z]{1,}$", string)
    if lowerCase:
        instance_ = lowerCase.group(0)
        string = string[0:string.find(instance_)] + instance_.upper()
    return string


def normalizeNumbers(string, logger_=moduleLogger):
    """
    Finds the numbers in the string and move them to the correct
    position in the string.
    Args:
            string(str): The string to work with.
            logger_(instance): The logging instance of
            a module.
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
    else:
        logger.log(level='warning',
                   message='There are no numbers in the string "' +
                   string + '"', logger=logger_)
    return string


def valid_suffix(string, logger_=moduleLogger):
    """
    Finds valid suffix in a string. If not it throw a warning message.
    Args:
            string(str): The string to check.
            logger_(instance): The logging instance of
            a module.
    Return:
            string: The passed string.
    """
    valid = "_CRV|_HANDLE|_JNT|_GEO|_GRP|_CON|_MPND|_DEMAND|_MUMAND"
    suffixPattern = re.compile(valid)
    if not re.search(suffixPattern, string):
        logger.log(level='warning',
                   message='string "' + string + '" has no valid suffix.' +
                   ' Valid are ' + valid,
                   logger=logger_)
    return string


def valid_stringSeparator(string, logger_=moduleLogger):
    """
    Finds valid separator in a string. If not it throw a warning message.
    Args:
            string(str): The string to check.
            logger_(instance): The logging instance of
            a module.
    Return:
            string: The passed string.
    """
    if not re.search('_', string):
        logger.log(level='warning',
                   message='string "' + string +
                   '" has no valid separator. Valid is "_"',
                   logger=logger_)
    return string


def string_checkup(string, logger_=moduleLogger):
    """
    String checkups.
    Args:
            string(str): The string to check.
            logger_(instance): The logging instance of
            a module.
    Return:
            string: The passed string.
    """
    string = valid_stringSeparator(string, logger_)
    string = replaceInvalidPrefix(string, logger_)
    string = valid_suffix(string, logger_)
    string = normalizeNumbers(string, logger_)
    string = normalizeSuffix(string, logger_)
    return string


def search(pattern, string):
    """
    Search for a pattern in a string
    Args:
            pattern(str): The search pattern.
            string(str): The string to search for.
    Return:
            list: The result of the search.
    """
    result = []
    if re.search(pattern, string):
        result.append(string)
    return result
