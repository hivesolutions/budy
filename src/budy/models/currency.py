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

class Currency(base.BudyBase):

    iso = appier.field(
        default = True,
        index = True
    )

    decimal_places = appier.field(
        type = int,
        index = True
    )

    @classmethod
    def validate(cls):
        return super(Currency, cls).validate() + [
            appier.not_null("iso"),
            appier.not_empty("iso"),
            appier.string_eq("iso", 3),

            appier.not_null("decimal_places"),
            appier.gte("decimal_places", 0)
        ]

    @classmethod
    def list_names(cls):
        return ["iso", "decimal_places"]

    @classmethod
    def create_s(cls, iso, decimal_places, invalidate = True):
        if invalidate and hasattr(cls, "_currencies"): delattr(cls, "_currencies")
        currency = cls(iso = iso, decimal_places = decimal_places)
        currency.save()

    @classmethod
    def round(cls, value, currency, decimal_places = 5):
        currencies = cls.get_currencies()
        currency = currencies.get(currency, {})
        decimal_places = currency.get("decimal_places", decimal_places)
        return round(value, decimal_places)

    @classmethod
    def get_currencies(cls):
        if hasattr(cls, "_currencies"): return cls._currencies
        currencies = cls.find(map = True)
        cls._currencies = dict([(value["iso"], value) for value in currencies])
        return cls._currencies

    @classmethod
    @appier.operation(
        name = "Import CSV",
        parameters = (
            ("CSV File", "file", "file"),
            ("Empty source", "empty", bool, True)
        )
    )
    def import_csv_s(cls, file, empty):

        def callback(line):
            iso, decimal_places = line
            decimal_places = int(decimal_places)
            currency = cls(
                iso = iso,
                decimal_places = decimal_places
            )
            currency.save()

        if empty: cls.delete_c()
        cls._csv_import(file, callback)
