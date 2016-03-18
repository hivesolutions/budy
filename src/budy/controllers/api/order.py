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

import budy

from . import root

class OrderApiController(root.RootApiController):

    @appier.route("/api/orders", "GET", json = True)
    @appier.ensure(token = "admin")
    def list(self):
        object = appier.get_object(alias = True, find = True)
        products = budy.Order.find(
            eager = ("lines", "lines.product"),
            map = True,
            **object
        )
        return products

    @appier.route("/api/orders/<str:key>", "GET", json = True)
    def show(self, key):
        order = budy.Order.get(key = key)
        order.refresh_s(
            currency = self.currency,
            country = self.country
        )
        order = order.reload(
            eager = ("lines", "lines.product"),
            map = True
        )
        return order
