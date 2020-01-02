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

import commons

import appier

from . import base

class ExchangeRate(base.BudyBase):

    name = appier.field(
        default = True
    )

    base = appier.field(
        index = True
    )

    target = appier.field(
        index = True
    )

    rate = appier.field(
        type = commons.Decimal,
        index = True
    )

    @classmethod
    def validate(cls):
        return super(ExchangeRate, cls).validate() + [
            appier.not_null("base"),
            appier.not_empty("base"),

            appier.not_null("target"),
            appier.not_empty("target"),

            appier.not_null("rate"),
            appier.gte("rate", 0.0)
        ]

    @classmethod
    def list_names(cls):
        return ["base", "target", "rate"]

    @classmethod
    def create_s(cls, base, target, rate):
        exchange_rate = cls(
            base = base,
            target = target,
            rate = rate
        )
        exchange_rate.save()

    @classmethod
    def create_both_s(cls, base, target, rate):
        rate_r = commons.Decimal(1.0) / rate
        cls.create_s(base, target, rate)
        cls.create_s(target, base, rate_r)

    @classmethod
    def convert(cls, value, base, target, reversed = False, rounder = round):
        from . import currency
        if reversed: return cls.reverse(value, base, target, rounder = rounder)
        exchange_rate = cls.get(base = base, target = target)
        result = commons.Decimal(value) * exchange_rate.rate
        return currency.Currency.round(result, target, rounder = rounder)

    @classmethod
    def reverse(cls, value, base, target, rounder = round):
        from . import currency
        exchange_rate = cls.get(base = target, target = base)
        result = commons.Decimal(value) * (commons.Decimal(1.0) / exchange_rate.rate)
        return currency.Currency.round(result, target, rounder = rounder)

    @classmethod
    def has_rate(cls, base, target):
        exchange_rate = cls.get(
            base = base,
            target = target,
            raise_e = False
        )
        if not exchange_rate: return False
        if not exchange_rate.rate: return False
        return True

    @classmethod
    @appier.operation(
        name = "Import CSV",
        parameters = (
            ("CSV File", "file", "file"),
            ("Empty source", "empty", bool, False)
        )
    )
    def import_csv_s(cls, file, empty):

        def callback(line):
            base, target, rate = line
            rate = float(rate)
            exchange_rate = cls(
                base = base,
                target = target,
                rate = rate
            )
            exchange_rate.save()

        if empty: cls.delete_c()
        cls._csv_import(file, callback)
