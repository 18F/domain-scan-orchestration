Home-page: https://github.com/thombashi/typepy
Author: Tsuyoshi Hombashi
Author-email: tsuyoshi.hombashi@gmail.com
License: MIT License
Description: 
        typepy
        ========
        .. image:: https://badge.fury.io/py/typepy.svg
            :target: https://badge.fury.io/py/typepy
        
        .. image:: https://img.shields.io/travis/thombashi/typepy/master.svg?label=Linux
            :target: https://travis-ci.org/thombashi/typepy
        
        .. image:: https://img.shields.io/appveyor/ci/thombashi/typepy/master.svg?label=Windows
            :target: https://ci.appveyor.com/project/thombashi/typepy
        
        .. image:: https://coveralls.io/repos/github/thombashi/typepy/badge.svg?branch=master
            :target: https://coveralls.io/github/thombashi/typepy?branch=master
        
        .. image:: https://img.shields.io/github/stars/thombashi/typepy.svg?style=social&label=Star
           :target: https://github.com/thombashi/typepy
        
        
        Summary
        =========
        A Python library for variable type checker/validator/converter at a run time.
        
        
        Features
        ==========
        - checking a value type
        - validate a value for a type
        - convert a value from a type to the other type
        
        The correspondence between Python types and ``typepy`` classes are as follows:
        
        .. table:: Supported Types
        
            ====================  =======================================================================================================
            Python Type           typepy: Type Class
            ====================  =======================================================================================================
            ``bool``              `Bool <http://typepy.rtfd.io/en/latest/pages/reference/type.html#bool-type>`__
            ``datetime``          `DateTime <http://typepy.rtfd.io/en/latest/pages/reference/type.html#datetime-type>`__
            ``dict``              `Dictionary <http://typepy.rtfd.io/en/latest/pages/reference/type.html#dictionary-type>`__
            ``inf``               `Infinity <http://typepy.rtfd.io/en/latest/pages/reference/type.html#infinity-type>`__
            ``int``               `Integer <http://typepy.rtfd.io/en/latest/pages/reference/type.html#integer-type>`__
            ``list``              `List <http://typepy.rtfd.io/en/latest/pages/reference/type.html#list-type>`__
            ``float``             `RealNumber <http://typepy.rtfd.io/en/latest/pages/reference/type.html#real-number-type>`__
            ``NaN``               `Nan <http://typepy.rtfd.io/en/latest/pages/reference/type.html#nan-type>`__
            ``None``              `None <http://typepy.rtfd.io/en/latest/pages/reference/type.html#none-type>`__
            ``str`` (not null)    `String <http://typepy.rtfd.io/en/latest/pages/reference/type.html#string-type>`__
            ``str`` (null)        `NullString <http://typepy.rtfd.io/en/latest/pages/reference/type.html#null-string-type>`__
            ``str`` (IP address)  `IpAddress <http://typepy.rtfd.io/en/latest/pages/reference/type.html#ip-address-type>`__
            ====================  =======================================================================================================
        
        
        Usage
        =======
        Type Check Method
        ----------------------
        :Examples:
            .. code-block:: pycon
        
                >>> from typepy.type import Integer
                >>> Integer(1).is_type()
                True
                >>> Integer(1.1).is_type()
                False
        
        
        Type Validation Method
        --------------------------------------------
        :Examples:
            .. code-block:: pycon
        
                >>> from typepy.type import Integer
                >>> Integer(1).validate()
                >>> try:
                ...     Integer(1.1).validate()
                ... except TypeError as e:
                ...     print(e)
                ...
                invalid value type: expected=INTEGER, actual=<type 'float'>
        
        
        Type Conversion Methods
        --------------------------------------------
        
        convert method
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        :Examples:
            .. code-block:: pycon
        
                >>> from typepy.type import Integer
                >>> from typepy import TypeConversionError
                >>> Integer("1").convert()
                1
                >>> try:
                ...     Integer(1.1).convert()
                ... except TypeConversionError as e:
                ...     print(e)  # convert() raised TypeConversionError when conversion failed
                ...
                failed to convert from float to INTEGER
        
        try_convert method
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        :Examples:
            .. code-block:: pycon
        
                >>> from typepy.type import Integer
                >>> Integer("1").try_convert()
                1
                >>> print(Integer(1.1).try_convert())  # try_convert() returned None when conversion failed
                None
        
        force_convert
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        :Examples:
            .. code-block:: pycon
        
                >>> from typepy.type import Integer
                >>> Integer("1").force_convert()  # force_convert() forcibly convert the value
                1
                >>> Integer(1.1).force_convert()
                1
        
        
        For more information
        --------------------------------------------
        Type check/validate/convert results differed according to
        ``strict_level`` value which can pass to typepy classes constructors as an argument.
        More information can be found in the
        `API reference <http://typepy.rtfd.io/en/latest/pages/reference/index.html>`__.
        
        Installation
        ============
        
        ::
        
            pip install typepy
        
        Dependencies
        ============
        Python 2.7+ or 3.3+
        
        - `mbstrdecoder <https://github.com/thombashi/mbstrdecoder>`__
        - `python-dateutil <https://dateutil.readthedocs.io/en/stable/>`__
        - `pytz <https://pypi.python.org/pypi/pytz/>`__
        - `six <https://pypi.python.org/pypi/six/>`__
        
        Test dependencies
        -----------------
        - `pytest <http://pytest.org/latest/>`__
        - `pytest-runner <https://pypi.python.org/pypi/pytest-runner>`__
        - `tox <https://testrun.org/tox/latest/>`__
        
        
        Documentation
        ===============
        http://typepy.rtfd.io/
        
Keywords: library,type-checking,type-conversion,validator
Platform: UNKNOWN
Classifier: Development Status :: 3 - Alpha
Classifier: Intended Audience :: Developers
Classifier: Intended Audience :: Information Technology
Classifier: License :: OSI Approved :: MIT License
Classifier: Operating System :: OS Independent
Classifier: Programming Language :: Python :: 2
Classifier: Programming Language :: Python :: 2.7
Classifier: Programming Language :: Python :: 3
Classifier: Programming Language :: Python :: 3.3
Classifier: Programming Language :: Python :: 3.4
Classifier: Programming Language :: Python :: 3.5
Classifier: Programming Language :: Python :: 3.6
Classifier: Topic :: Software Development :: Libraries
Classifier: Topic :: Software Development :: Libraries :: Python Modules
