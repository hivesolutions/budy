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

import appier

from . import base

class Voucher(base.BudyBase):

    key = appier.field(
        index = True,
        safe = True,
        immutable = True
    )

    amount = appier.field(
        type = float,
        index = True
    )

    percentage = appier.field(
        type = float,
        index = True
    )

    currency = appier.field(
        index = True
    )

    expiration = appier.field(
        type = int,
        index = True,
        meta = "datetime"
    )

    usage_count = appier.field(
        type = int,
        index = True
    )

    usage_limit = appier.field(
        type = int,
        index = True
    )

    @classmethod
    def validate(cls):
        return super(Voucher, cls).validate() + [
            appier.gte("amount", 0.0),

            appier.gte("percentage", 0.0),

            appier.gte("usage_count", 0),

            appier.gte("usage_limit", 0)
        ]

    @classmethod
    def list_names(cls):
        return ["created", "key", "amount", "percentage", "expiration", "enabled"]
