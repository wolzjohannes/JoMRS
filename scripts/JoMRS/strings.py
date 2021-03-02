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
# Date:       2021 / 03 / 02

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

##########################################################
# GLOBALS
##########################################################

_LOGGER = logging.getLogger(__name__ + ".py")


##########################################################
# FUNCTIONS
##########################################################


def normalize_prefix(string, logger_=_LOGGER):
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
            new_string = string[0].upper() + "_" + string[1:]
            return new_string
        return string
    logger.log(level="warning", message="Prefix has a number", logger=logger_)
    return string


def replace_invalid_prefix(string, logger_=_LOGGER):
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
        logger.log(
            level="warning",
            message='The string prefix "' + string + '" should specifie a side',
            logger=logger_,
        )
    numbers_match = re.match("^[0-9]", string)
    if numbers_match:
        number = "^" + numbers_match.group(0)
        string = string.replace(number, "")
        logger.log(
            level="warning",
            message="Prefix contains numbers" ". Numbers deleted",
            logger=logger_,
        )
    re_pattern = re.compile(
        "_[lrmn]+_|_[LRMN]+_|^[lrmnLRMN]_+"
        "|_[lrmnLRMN][0-9]+_|^[0-9][lrmnLRMN]_+"
        "|^[lrmnLRMN][0-9]_|_[0-9][lrmnLRMN]_"
    )
    re_match = re.search(re_pattern, string)
    if re_match:
        instance = re_match.group(0)
        # try to find if a number exist besides the character and remove it.
        instance_ = re.search("[0-9]", instance)
        if instance_:
            instance_ = instance_.group(0)
            if instance.find(instance_) != -1:
                instance__ = instance.replace(instance_, "")
                string = string.replace(instance, instance__)
                instance = instance__
        # remove the instance of [lrmnLRMN] and so on.
        # And put it at the beginning of the string.
        string = string.replace(instance, "_")
        if re.search("[Rr]", instance):
            string = "R{}".format(string)
        elif re.search("[Ll]", instance):
            string = "L{}".format(string)
        elif re.search("[MmNn]", instance):
            string = "M{}".format(string)
        if not re.match("^[MRL]_", string):
            side = string[0]
            string = "{}_{}".format(side, string[1:])
    return string


def replace_hash_with_padding(string, index):
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


def normalize_suffix_0(string, logger_=_LOGGER):
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
            level="warning",
            message='Suffix of string "'
            + string
            + '" should not have a number. Numbers removed from the suffix',
            logger=logger_,
        )
        instance = numbers.group(0)
        string = string[0 : string.find(instance)]
    lower_case = re.search("_[a-z]{1,}$", string)
    if lower_case:
        instance_ = lower_case.group(0)
        string = string[0 : string.find(instance_)] + instance_.upper()
    return string

def normalize_suffix_1(string, logger_=_LOGGER):
    """
    Replace numbers in the suffix with a '' and generate the correct count
    and put in the right place.
    Args:
            string(str): The string to work with
            a module.
            logger_(instance): The logging instance of
            a module.
    Return:
            The new created string.
    """
    numbers_end_string_regex = r"(\d+$)"
    count_regex = r"(_\d+_\D+)"
    match = re.search(numbers_end_string_regex, string)
    # If we find a number in the suffix of the string we delete it. And
    # generate the correct count and put in the correct place in the string.
    if match:
        logger.log(
            level="warning",
            message='Suffix of string "'
            + string
            + '" should not have a number. Numbers removed from the suffix',
            logger=logger_,
        )
        instance = match.groups()[0]
        string = re.sub(numbers_end_string_regex, "", string)
        count_match = re.search(count_regex, string)
        instance_ = count_match.groups()[0]
        count_list = [str_ for str_ in instance_.split('_') if str_]
        new_count = int(count_list[0]) + int(instance)
        new_count = '_{}_{}'.format(new_count, count_list[1])
        string = string.replace(instance_, new_count)
    return string


def numbers_check(string, logger_=_LOGGER):
    """
    Check the string for numbers at all and for the valid expression.

    Args:
        string(str): Given string.
        logger_(instance): The logging instance of
        a module.

    Return:
         Given String.

    """
    valid_regex_0 = r"\d"
    valid_regex_1 = r"_\d+_\d+_"
    valid_regex_2 = r"_\d+_"
    if not re.search(valid_regex_0, string):
        logger.log(
            level="warning",
            message='There are no numbers in the string "' + string + '"',
            logger=logger_,
        )
        return string
    if re.search(valid_regex_1, string):
        return string
    elif re.search(valid_regex_2, string):
        return string
    else:
        logger.log(
            level="warning",
            message='Numbers not in valid expression. Valid values are "_(['
            '0-9]+)_([0-9]+)_" or "_([0-9]+)_"',
            logger=logger_,
        )
        return string


def valid_suffix(string, logger_=_LOGGER):
    """
    Finds valid suffix in a string. If not it throw a warning message.
    Args:
            string(str): The string to check.
            logger_(instance): The logging instance of
            a module.
    Return:
            string: The passed string.
    """
    valid = (
        "_CRV|_HANDLE|_JNT|_GEO|_GRP|_CON|_MPND|_DEMAND|_MUMAND|_METAND"
        "|_CONST|_MULDOLINND|_TRS|_REVND|_SCND|_ANBEND|_ANBLND|_PABLND"
    )
    suffix_pattern = re.compile(valid)
    if not re.search(suffix_pattern, string):
        logger.log(
            level="warning",
            message='string "'
            + string
            + '" has no valid suffix.'
            + " Valid are "
            + valid,
            logger=logger_,
        )
    return string


def valid_string_separator(string, logger_=_LOGGER):
    """
    Finds valid separator in a string. If not it throw a warning message.
    Args:
            string(str): The string to check.
            logger_(instance): The logging instance of
            a module.
    Return:
            string: The passed string.
    """
    if not re.search("_", string):
        logger.log(
            level="warning",
            message='string "'
            + string
            + '" has no valid separator. Valid is "_"',
            logger=logger_,
        )
    return string


def string_checkup(string, logger_=_LOGGER):
    """
    String checkups.
    Args:
            string(str): The string to check.
            logger_(instance): The logging instance of
            a module.
    Return:
            string: The passed string.
    """
    string = valid_string_separator(string, logger_)
    string = replace_invalid_prefix(string, logger_)
    string = valid_suffix(string, logger_)
    string = numbers_check(string, logger_)
    string = normalize_suffix_0(string, logger_)
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


def search_and_replace(string, search, replace):
    """
    Search and replace a pattern in string.
    Args:
        string(str): String to search for.
        search(str): Search string.
        replace(str): Replace string.
        
    Return:
        list: The new created string.

    """
    if re.search(search, string):
        string_ = string.replace(search, replace)
        return string_


def regex_search_and_replace(string, regex, replace):
    """
    Search about a regular expression and replace it.

    Args:
        string(str): String to search for.
        regex(str): Regex string.
        replace(str): String for replacement.

    Return:
        String: New string.

    """
    return re.sub(regex, replace, string)


def normalize_string(string, logger_):
    """
    Normalize given string. Only letters accepted.

    Args:
        string(str): String to normalize.
        logger_(instance): The logging instance of
        a module.

    Return:
        String: Normalized string.

    """
    regex = r"[a-zA-Z]"
    invalid_regex = r"[\W_\d+]"
    search_pattern = re.search(invalid_regex, string)
    if search_pattern:
        logger.log(
            level="warning",
            message='"{}" String has invalid ' "characters".format(string),
            logger=logger_,
        )
    matches = re.finditer(regex, string, re.MULTILINE)
    return "".join(match.group() for match in matches)


def replace_index_numbers(string, replace):
    """
    Find the index numbers in the string. Will cut out all numbers with this
    ["a-zA-Z_00000_"] expression.

    Args:
        string(str): String to compile.
        replace(int): New index number.

    Returns:
        Compiled string.

    """
    regex = r"(\w_\d+_)"
    match = re.search(regex, string)
    instance = match.groups()[0]
    numbers = re.sub(r"[a-zA-Z]", "", instance)
    return regex_search_and_replace(string, numbers, '_{}_'.format(str(
        replace)))

def normalize_suffix_(string):
    numbers_end_string_regex = r"(\d+$)"
    count_regex = r"(_\d+_\D+)"
    match = re.search(numbers_end_string_regex, string)
    # If we find a number in the suffix of the string we delete it. And
    # generate the correct count and put in the correct place in the string.
    if match:
        instance = match.groups()[0]
        string = re.sub(numbers_end_string_regex, "", string)
        count_match = re.search(count_regex, string)
        instance_ = count_match.groups()[0]
        count_list = [str_ for str_ in instance_.split('_') if str_]
        new_count = int(count_list[0]) + int(instance)
        new_count = '_{}_{}'.format(new_count, count_list[1])
        string = string.replace(instance_, new_count)
        logger.log(
            level="warning",
            message='Suffix of string "'
            + string
            + '" should not have a number. Numbers removed from the suffix',
            logger=_LOGGER,
        )