#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Budy
# Copyright (c) 2008-2020 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2020 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import appier

import budy

from . import root

class CurrencyAPIController(root.RootAPIController):

    @appier.route("/api/currencies", "GET", json = True)
    def list(self):
        object = appier.get_object(alias = True, find = True)
        currencies = budy.Currency.find(
            find_i = True,
            find_t = "right",
            map = True,
            **object
        )
        return currencies

    @appier.route("/api/currencies/simple.csv", "GET")
    @appier.ensure(token = "admin")
    def simple_csv(self):
        object = appier.get_object(
            alias = True,
            find = True,
            limit = 0
        )
        currencies = budy.Currency.find(**object)

        currencies_s = [("iso", "decimal_places")]
        for currency in currencies:
            currency_s = (currency.iso, currency.decimal_places)
            currencies_s.append(currency_s)

        result = appier.serialize_csv(currencies_s, delimiter = ",")
        self.content_type("text/csv")
        return result
