**mbstrdecoder**

.. image:: https://badge.fury.io/py/mbstrdecoder.svg
    :target: https://badge.fury.io/py/mbstrdecoder

.. image:: https://img.shields.io/pypi/pyversions/mbstrdecoder.svg
   :target: https://pypi.python.org/pypi/mbstrdecoder

.. image:: https://img.shields.io/travis/thombashi/mbstrdecoder/master.svg?label=Linux
    :target: https://travis-ci.org/thombashi/mbstrdecoder

.. image:: https://img.shields.io/appveyor/ci/thombashi/mbstrdecoder/master.svg?label=Windows
    :target: https://ci.appveyor.com/project/thombashi/mbstrdecoder

.. image:: https://coveralls.io/repos/github/thombashi/mbstrdecoder/badge.svg?branch=master
    :target: https://coveralls.io/github/thombashi/mbstrdecoder?branch=master


.. contents:: Table of contents
   :backlinks: top
   :local:


Summary
=======
Python library for multi-byte character string decoder.


Installation
============

::

    pip install mbstrdecoder


Usage
=====

.. code:: python

    from __future__ import print_function
    from mbstrdecoder import MultiByteStrDecoder

    encoded_multibyte_text = u"マルチバイト文字".encode("utf-8")
    decoder = MultiByteStrDecoder(encoded_multibyte_text)

    print(encoded_multibyte_text)
    print(decoder.unicode_str)
    print(decoder.codec)

::

    b'\xe3\x83\x9e\xe3\x83\xab\xe3\x83\x81\xe3\x83\x90\xe3\x82\xa4\xe3\x83\x88\xe6\x96\x87\xe5\xad\x97'
    マルチバイト文字
    utf_8


Dependencies
============

Python 2.7+ or 3.3+

Test dependencies
-----------------

-  `pytest <https://pypi.python.org/pypi/pytest>`__
-  `pytest-runner <https://pypi.python.org/pypi/pytest-runner>`__
-  `tox <https://pypi.python.org/pypi/tox>`__


