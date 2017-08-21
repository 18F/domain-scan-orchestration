#import imp
#import sys
#sys.modules["sqlite"] = imp.new_module("sqlite")
#sys.modules["sqlite3.dbapi2"] = imp.new_module("sqlite.dbapi2")
#import sqlite3
from pshtt import pshtt


def my_handler(event, context):
    options = {
        'user_agent': args['--user-agent'],
        'timeout': args['--timeout'],
        'preload_cache': args['--preload-cache'],
        'suffix_cache': args['--suffix-cache'],
        'cache': args['--cache'],
        'ca_file': args['--ca-file']
    }

    pshtt.inspect_domains(["www.google.com"], options)
    return {
        "message": "success"
    }