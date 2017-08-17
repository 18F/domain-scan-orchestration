# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals

import copy

import enum
from typepy import is_empty_sequence
from typepy.type import String

from six.moves import zip

from ._common import (
    NOT_STRICT_TYPE_MAPPING,
    DefaultValue,
)
from ._dataproperty import (
    DataProperty,
    ColumnDataProperty,
)
from ._dataproperty_converter import DataPropertyConverter
from ._logger import logger


@enum.unique
class MatrixFormatting(enum.Enum):
    # raise exception if the matrix is not properly formatted
    EXCEPTION = 1 << 1

    # trim to the minimum size column
    TRIM = 1 << 2

    # Append None values to columns so that it is the same as the maximum
    # column size.
    FILL_NONE = 1 << 3

    HEADER_ALIGNED = 1 << 4


class DataPropertyExtractor(object):
    """
    .. py:attribute:: quoting_flags

        Configurations to add double quote to for each items in a matrix,
        where |Typecode| of table-value is |True| in the ``quote_flag_table``
        mapping table. ``quote_flag_table`` should be a dictionary.
        And is ``{ Typecode : bool }``. Defaults to:

        .. code-block:: json
            :caption: The default values

            {
                Typecode.BOOL: False,
                Typecode.DATETIME: False,
                Typecode.DICTIONARY: False,
                Typecode.INFINITY: False,
                Typecode.INTEGER: False,
                Typecode.IP_ADDRESS: False,
                Typecode.LIST: False,
                Typecode.NAN: False,
                Typecode.NULL_STRING: False,
                Typecode.NONE: False,
                Typecode.REAL_NUMBER: False,
                Typecode.STRING: False,
            }
    """

    @property
    def header_list(self):
        return self.__header_list

    @header_list.setter
    def header_list(self, x):
        if self.__header_list == x:
            return

        self.__header_list = x
        self.__clear_cache()

    @property
    def data_matrix(self):
        return self.__data_matrix

    @data_matrix.setter
    def data_matrix(self, x):
        self.__data_matrix = x
        self.__clear_cache()

    @property
    def default_type_hint(self):
        return self.__default_type_hint

    @default_type_hint.setter
    def default_type_hint(self, x):
        if self.__default_type_hint == x:
            return

        self.__default_type_hint = x
        self.__clear_cache()

    @property
    def col_type_hint_list(self):
        return self.__col_type_hint_list

    @col_type_hint_list.setter
    def col_type_hint_list(self, x):
        if self.__col_type_hint_list == x:
            return

        self.__col_type_hint_list = x
        self.__clear_cache()

    @property
    def strip_str_header(self):
        return self.__strip_str_header

    @strip_str_header.setter
    def strip_str_header(self, x):
        if self.__strip_str_header == x:
            return

        self.__strip_str_header = x
        self.__clear_cache()

    @property
    def strip_str_value(self):
        return self.__strip_str_value

    @strip_str_value.setter
    def strip_str_value(self, x):
        if self.__strip_str_value == x:
            return

        self.__strip_str_value = x
        self.__clear_cache()

    @property
    def min_column_width(self):
        return self.__min_col_ascii_char_width

    @min_column_width.setter
    def min_column_width(self, x):
        if self.__min_col_ascii_char_width == x:
            return

        self.__min_col_ascii_char_width = x
        self.__clear_cache()

    @property
    def float_type(self):
        return self.__float_type

    @float_type.setter
    def float_type(self, x):
        if self.__float_type == x:
            return

        self.__float_type = x
        self.__clear_cache()

    @property
    def datetime_format_str(self):
        return self.__datetime_format_str

    @datetime_format_str.setter
    def datetime_format_str(self, x):
        if self.__datetime_format_str == x:
            return

        self.__datetime_format_str = x
        self.__clear_cache()

    @property
    def strict_type_mapping(self):
        return self.__strict_type_mapping

    @strict_type_mapping.setter
    def strict_type_mapping(self, x):
        if self.__strict_type_mapping == x:
            return

        self.__strict_type_mapping = x
        self.__clear_cache()

    @property
    def east_asian_ambiguous_width(self):
        return self.__east_asian_ambiguous_width

    @east_asian_ambiguous_width.setter
    def east_asian_ambiguous_width(self, x):
        if self.__east_asian_ambiguous_width == x:
            return

        self.__east_asian_ambiguous_width = x
        self.__clear_cache()

    @property
    def type_value_mapping(self):
        return self.__type_value_mapping

    @type_value_mapping.setter
    def type_value_mapping(self, x):
        if self.__type_value_mapping == x:
            return

        self.__type_value_mapping = x
        self.__clear_cache()

    @property
    def const_value_mapping(self):
        return self.__const_value_mapping

    @const_value_mapping.setter
    def const_value_mapping(self, x):
        if self.__const_value_mapping == x:
            return

        self.__const_value_mapping = x
        self.__clear_cache()

    @property
    def quoting_flags(self):
        return self.__quoting_flags

    @quoting_flags.setter
    def quoting_flags(self, x):
        if self.__quoting_flags == x:
            return

        self.__quoting_flags = x
        self.__clear_cache()

    @property
    def datetime_formatter(self):
        return self.__datetime_formatter

    @datetime_formatter.setter
    def datetime_formatter(self, x):
        if self.__datetime_formatter == x:
            return

        self.__datetime_formatter = x
        self.__clear_cache()

    @property
    def matrix_formatting(self):
        return self.__matrix_formatting

    @matrix_formatting.setter
    def matrix_formatting(self, x):
        if self.__matrix_formatting == x:
            return

        self.__matrix_formatting = x
        self.__clear_cache()

    def __init__(self):
        self.__header_list = []
        self.__data_matrix = []
        self.__default_type_hint = None
        self.__col_type_hint_list = None

        self.__strip_str_header = None
        self.__strip_str_value = None
        self.__min_col_ascii_char_width = 0
        self.__float_type = None
        self.__datetime_format_str = DefaultValue.DATETIME_FORMAT
        self.__strict_type_mapping = copy.deepcopy(
            DefaultValue.STRICT_LEVEL_MAPPING)
        self.__east_asian_ambiguous_width = 1

        self.__type_value_mapping = copy.deepcopy(
            DefaultValue.TYPE_VALUE_MAPPING)
        self.__const_value_mapping = copy.deepcopy(
            DefaultValue.CONST_VALUE_MAPPING)
        self.__quoting_flags = copy.deepcopy(DefaultValue.QUOTING_FLAGS)
        self.__datetime_formatter = None

        self.__matrix_formatting = MatrixFormatting.TRIM

        self.__clear_cache()

    def __clear_cache(self):
        self.__update_dp_converter()
        self.__dp_matrix_cache = None
        self.__dp_cache_zero = self.__to_dataproperty_raw(0)
        self.__dp_cache_one = self.__to_dataproperty_raw(1)
        self.__dp_cache_true = self.__to_dataproperty_raw(True)
        self.__dp_cache_false = self.__to_dataproperty_raw(False)
        self.__dp_cache_mapping = {
            None: self.__to_dataproperty_raw(None),
            "": self.__to_dataproperty_raw(""),
        }

    def to_dataproperty(self, data):
        self.__update_dp_converter()

        return self.__to_dataproperty(data, strip_str=self.strip_str_value)

    def to_dataproperty_list(self, data_list):
        if is_empty_sequence(data_list):
            return []

        self.__update_dp_converter()

        return [
            self.__to_dataproperty(data, strip_str=self.strip_str_value)
            for data in data_list
        ]

    def to_col_dataproperty_list(self, previous_column_dp_list=None):
        logger.debug(
            "to_col_dataproperty_list: prev_col_count={}, "
            "mismatch_process={}".format(
                len(previous_column_dp_list)
                if previous_column_dp_list else None,
                self.matrix_formatting))

        col_dp_list = self.__get_col_dp_list_base()

        try:
            dp_matrix = self.to_dataproperty_matrix()
        except TypeError as e:
            logger.debug(e)
            return col_dp_list

        for col_idx, value_dp_list in enumerate(zip(*dp_matrix)):
            try:
                col_dp_list[col_idx]
            except IndexError:
                col_dp_list.append(ColumnDataProperty(
                    column_index=col_idx, min_width=self.min_column_width,
                    datetime_format_str=self.datetime_format_str,
                    east_asian_ambiguous_width=self.east_asian_ambiguous_width
                ))

            col_dp = col_dp_list[col_idx]
            col_dp.begin_update()

            try:
                col_dp.merge(previous_column_dp_list[col_idx])
            except (TypeError, IndexError):
                pass

            for value_dp in value_dp_list:
                col_dp.update_body(value_dp)

            col_dp.end_update()

            logger.debug("  {:s}".format(str(col_dp)))

        return col_dp_list

    def to_dataproperty_matrix(self):
        if self.__dp_matrix_cache:
            return self.__dp_matrix_cache

        self.__update_dp_converter()
        self.__dp_matrix_cache = list(zip(*[
            self.__to_dataproperty_list(
                data_list, type_hint=self.__get_col_type_hint(col_idx),
                strip_str=self.strip_str_value)
            for col_idx, data_list
            in enumerate(zip(*self.__to_dataproperty_matrix()))
        ]))

        return self.__dp_matrix_cache

    def to_header_dataproperty_list(self):
        self.__update_dp_converter()

        return self.__to_dataproperty_list(
            self.header_list, type_hint=String,
            strip_str=self.strip_str_header,
            strict_type_mapping=NOT_STRICT_TYPE_MAPPING)

    def __get_col_type_hint(self, col_idx):
        try:
            return self.col_type_hint_list[col_idx]
        except (TypeError, IndexError):
            return self.default_type_hint

    def __to_dataproperty(
            self, data, type_hint=None, strip_str=None,
            strict_type_mapping=None):
        try:
            if data in self.__dp_cache_mapping:
                return self.__dp_cache_mapping.get(data)
        except TypeError:
            # unhashable type
            pass

        if data == 0:
            if str(data) != "False":
                return self.__dp_cache_zero

            return self.__dp_cache_false
        if data == 1:
            if str(data) != "True":
                return self.__dp_cache_one

            return self.__dp_cache_true

        return self.__to_dataproperty_raw(
            data,
            type_hint=type_hint,
            strip_str=strip_str,
            strict_type_mapping=strict_type_mapping)

    def __to_dataproperty_raw(
            self, data, type_hint=None, strip_str=None,
            strict_type_mapping=None):
        dp = DataProperty(
            data,
            type_hint=(
                type_hint if type_hint is not None else self.default_type_hint
            ),
            strip_str=strip_str,
            float_type=self.float_type,
            datetime_format_str=self.datetime_format_str,
            strict_type_mapping=(
                strict_type_mapping
                if type_hint is not None else self.strict_type_mapping),
            east_asian_ambiguous_width=self.east_asian_ambiguous_width
        )

        return self.__dp_converter.convert(dp)

    def __to_dataproperty_list(
            self, data_list, type_hint=None, strip_str=None,
            strict_type_mapping=None):
        if is_empty_sequence(data_list):
            return []

        return [
            self.__to_dataproperty(
                data=data, type_hint=type_hint, strip_str=strip_str,
                strict_type_mapping=strict_type_mapping)
            for data in data_list
        ]

    def __to_dataproperty_matrix(self):
        header_col_size = len(self.header_list) if self.header_list else 0
        col_size_list = [
            len(data_list) for data_list in self.data_matrix
        ]

        if self.header_list:
            min_col_size = min([header_col_size] + col_size_list)
            max_col_size = max([header_col_size] + col_size_list)
        elif col_size_list:
            min_col_size = min(col_size_list)
            max_col_size = max(col_size_list)
        else:
            min_col_size = 0
            max_col_size = 0

        if self.matrix_formatting == MatrixFormatting.EXCEPTION:
            if min_col_size != max_col_size:
                raise ValueError(
                    "nonuniform column size: min={}, max={}".format(
                        min_col_size, max_col_size))

            return self.data_matrix

        if self.matrix_formatting == MatrixFormatting.HEADER_ALIGNED:
            if header_col_size > 0:
                format_col_size = header_col_size
            else:
                format_col_size = max_col_size
        elif self.matrix_formatting == MatrixFormatting.TRIM:
            format_col_size = min_col_size
        elif self.matrix_formatting == MatrixFormatting.FILL_NONE:
            format_col_size = max_col_size
        else:
            raise ValueError(
                "unknown matrix formatting: {}".format(self.matrix_formatting))

        return [
            self.data_matrix[row_idx][:format_col_size] +
            [None] * (format_col_size - col_size)
            for row_idx, col_size in enumerate(col_size_list)
        ]

    def __get_col_dp_list_base(self):
        header_dp_list = self.to_header_dataproperty_list()
        col_dp_list = []

        for col_idx, header_dp in enumerate(header_dp_list):
            col_dp = ColumnDataProperty(
                column_index=col_idx, min_width=self.min_column_width,
                datetime_format_str=self.datetime_format_str,
                east_asian_ambiguous_width=self.east_asian_ambiguous_width)
            col_dp.update_header(header_dp)
            col_dp_list.append(col_dp)

        return col_dp_list

    def __update_dp_converter(self):
        self.__dp_converter = DataPropertyConverter(
            type_value_mapping=self.type_value_mapping,
            const_value_mapping=self.const_value_mapping,
            quoting_flags=self.quoting_flags,
            datetime_formatter=self.datetime_formatter,
            datetime_format_str=self.datetime_format_str,
            float_type=self.float_type,
            strict_type_mapping=self.strict_type_mapping)
