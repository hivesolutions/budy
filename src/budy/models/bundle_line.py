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

class BundleLine(base.BudyBase):

    price = appier.field(
        type = float
    )

    currency = appier.field()

    country = appier.field()

    quantity = appier.field(
        type = float
    )

    total = appier.field(
        type = float
    )

    size = appier.field(
        type = int
    )

    scale = appier.field(
        type = int
    )

    attributes = appier.field()

    product = appier.field(
        type = appier.reference(
            "Product",
            name = "id"
        ),
        eager = True
    )

    def __init__(self, *args, **kwargs):
        base.BudyBase.__init__(self, *args, **kwargs)
        self.currency = kwargs.get("currency", None)
        self.country = kwargs.get("country", None)

    @classmethod
    def list_names(cls):
        return ["id", "quantity", "total", "currency", "product"]

    def pre_save(self):
        base.BudyBase.pre_save(self)
        self.calculate()
        self.measure()

    def calculate(self, currency = None, country = None, force = False):
        currency = currency or self.currency
        country = country or self.country
        self.total = self.quantity * self.get_price(
            currency = currency,
            country = country,
            force = force
        )

    def measure(self, currency = None, country = None, force = False):
        if self.size and self.scale and not force: return
        self.size, self.scale = self.get_size(
            currency = currency,
            country = country,
            force = force
        )

    def get_price(self, currency = None, country = None, force = False):
        is_dirty = self.is_dirty(currency = currency, country = country)
        if not is_dirty and not force: return self.price
        self.price = self.product.get_price(
            currency = currency,
            country = country,
            attributes = self.attributes
        )
        self.currency = currency
        self.country = country
        return self.price

    def get_size(self, currency = None, country = None, force = False):
        if not self.product: return None, None
        return self.product.get_size(
            currency = currency,
            country = country,
            attributes = self.attributes
        )

    def is_dirty(self, currency = None, country = None):
        is_dirty = not self.currency == currency
        is_dirty |= not self.country == country
        is_dirty |= not hasattr(self, "price") or self.price == None
        return is_dirty

    @appier.operation(name = "Calculate")
    def calculate_s(self):
        self.calculate(force = True)
        self.save()

    @appier.operation(name = "Measure")
    def measure_s(self):
        self.measure(force = True)
        self.save()
