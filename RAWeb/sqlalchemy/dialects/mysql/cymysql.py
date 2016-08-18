# mysql/cymysql.py
# Copyright (C) 2005-2014 the SQLAlchemy authors and contributors <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""

.. dialect:: mysql+cymysql
    :name: CyMySQL
    :dbapi: cymysql
    :connectstring: mysql+cymysql://<username>:<password>@<host>/<dbname>[?<options>]
    :url: https://github.com/nakagami/CyMySQL

"""

from .mysqldb import MySQLDialect_mysqldb
from .base import (BIT, MySQLDialect)
from ... import util

class _cymysqlBIT(BIT):
    def result_processor(self, dialect, coltype):
        """Convert a MySQL's 64 bit, variable length binary string to a long.
        """

        def process(value):
            if value is not None:
                # Py2K
                v = 0L
                for i in map(ord, value):
                    v = v << 8 | i
                # end Py2K
                # Py3K
                #v = 0
                #for i in value:
                #    v = v << 8 | i
                return v
            return value
        return process


class MySQLDialect_cymysql(MySQLDialect_mysqldb):
    driver = 'cymysql'

    description_encoding = None
    supports_sane_rowcount = False

    colspecs = util.update_copy(
        MySQLDialect.colspecs,
        {
            BIT: _cymysqlBIT,
        }
    )

    @classmethod
    def dbapi(cls):
        return __import__('cymysql')

    def _get_server_version_info(self, connection):
        dbapi_con = connection.connection
        version = [int(v) for v in dbapi_con.server_version.split('.')]
        return tuple(version)

    def _detect_charset(self, connection):
        return connection.connection.charset

    def _extract_error_code(self, exception):
        return exception.errno

    def is_disconnect(self, e, connection, cursor):
        if isinstance(e, self.dbapi.OperationalError):
            return self._extract_error_code(e) in \
                        (2006, 2013, 2014, 2045, 2055)
        elif isinstance(e, self.dbapi.InterfaceError):
            # if underlying connection is closed,
            # this is the error you get
            return True
        else:
            return False

dialect = MySQLDialect_cymysql