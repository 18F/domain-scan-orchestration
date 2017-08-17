# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals

import re

from ._base import VarNameSanitizer


class PythonVarNameSanitizer(VarNameSanitizer):
    __PYTHON_RESERVED_KEYWORDS = [
        "and", "del", "from", "not", "while",
        "as", "elif", "global", "or", "with",
        "assert", "else", "if", "pass", "yield",
        "break", "except", "import", "print",
        "class", "exec", "in", "raise",
        "continue", "finally", "is", "return",
        "def", "for", "lambda", "try",
    ]
    __PYTHON_BUILTIN_CONSTANTS = [
        "False", "True", "None", "NotImplemented", "Ellipsis", "__debug__",
    ]

    __RE_INVALID_VAR_NAME = re.compile("[^a-zA-Z0-9_]")
    __RE_INVALID_VAR_NAME_HEAD = re.compile("^[^a-zA-Z]+")

    @property
    def reserved_keywords(self):
        return (
            self.__PYTHON_RESERVED_KEYWORDS + self.__PYTHON_BUILTIN_CONSTANTS)

    @property
    def _invalid_var_name_head_re(self):
        return self.__RE_INVALID_VAR_NAME_HEAD

    @property
    def _invalid_var_name_re(self):
        return self.__RE_INVALID_VAR_NAME


def validate_python_var_name(var_name):
    """
    :param str var_name: Name to validate.
    :raises pathvalidate.NullNameError: If the ``var_name`` is empty.
    :raises pathvalidate.InvalidCharError: If the ``var_name`` is invalid as
        `Python identifier
        <https://docs.python.org/3/reference/lexical_analysis.html#identifiers>`__.
    :raises pathvalidate.InvalidReservedNameError:
        If the ``var_name`` is equals to
        `Python reserved keywords
        <https://docs.python.org/3/reference/lexical_analysis.html#keywords>`__
        or
        `Python built-in constants
        <https://docs.python.org/3/library/constants.html>`__.

    :Example:
        :ref:`example-validate-var-name`
    """

    PythonVarNameSanitizer(var_name).validate()


def sanitize_python_var_name(var_name, replacement_text=""):
    """
    Make a valid Python variable name from ``var_name``.

    To make a valid name:

    - Replace invalid characters for a Python variable name within
      the ``var_name`` with the ``replacement_text``
    - Delete invalid chars for the beginning of the variable name
    - Append underscore (``"_"``) at the tail of the name if sanitized name
      is one of the Python reserved names

    :param str filename: Name to sanitize.
    :param str replacement_text: Replacement text.
    :return: A replacement string.
    :rtype: str
    :raises ValueError: If ``var_name`` or ``replacement_text`` is invalid.

    :Example:
        :ref:`example-sanitize-var-name`

    .. seealso::
        :py:func:`.validate_python_var_name`
    """

    return PythonVarNameSanitizer(var_name).sanitize(replacement_text)
