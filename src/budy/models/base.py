#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Budy
# Copyright (c) 2008-2016 Hive Solutions Lda.
#
# This file is part of Hive Budy.
#
# Hive Budy is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Budy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Budy. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2016 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import csv

import appier
import appier_extras

class BudyBase(appier_extras.admin.Base):

    @classmethod
    def _csv_import(
        cls,
        file,
        callback,
        strict = False,
        delimiter = ",",
        escapechar = "\"",
        quoting = csv.QUOTE_MINIMAL
    ):
        _file_name, mime_type, data = file
        is_csv = mime_type in ("text/csv", "application/vnd.ms-excel")
        if not is_csv and strict:
            raise appier.OperationalError(
                message = "Invalid mime type '%s'" % mime_type
            )
        data = data.decode("utf-8")
        buffer = appier.legacy.StringIO(data)
        csv_reader = csv.reader(
            buffer,
            delimiter = delimiter,
            escapechar = escapechar,
            quoting = quoting
        )
        _header = next(csv_reader)
        for line in csv_reader: callback(line)
