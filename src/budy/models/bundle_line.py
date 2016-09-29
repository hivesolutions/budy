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

import commons

import appier

from . import base

class BundleLine(base.BudyBase):

    price = appier.field(
        type = commons.Decimal
    )

    taxes = appier.field(
        type = commons.Decimal
    )

    currency = appier.field()

    country = appier.field()

    quantity = appier.field(
        type = commons.Decimal,
        initial = commons.Decimal(0.0)
    )

    total = appier.field(
        type = commons.Decimal,
        initial = commons.Decimal(0.0)
    )

    total_taxes = appier.field(
        type = commons.Decimal,
        initial = commons.Decimal(0.0)
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

    @classmethod
    def list_names(cls):
        return ["id", "quantity", "total", "currency", "product"]

    @classmethod
    def order_name(self):
        return ["id", -1]

    def pre_save(self):
        base.BudyBase.pre_save(self)
        self.calculate()
        self.measure()
        self.ensure_valid()

    def calculate(self, currency = None, country = None, force = False):
        currency = currency or self.currency
        country = country or self.country
        self.total_taxes = self.quantity * self.get_taxes(
            currency = currency,
            country = country,
            force = force
        )
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
        self.price = self.merchandise.get_price(
            currency = currency,
            country = country,
            attributes = self.attributes
        )
        self.taxes = self.merchandise.get_taxes(
            currency = currency,
            country = country,
            attributes = self.attributes
        )
        self.currency = self.merchandise.get_currency(currency = currency)
        self.country = country
        return self.price

    def get_taxes(self, currency = None, country = None, force = False):
        self.get_price(currency = currency, country = country, force = force)
        return self.taxes

    def get_size(self, currency = None, country = None, force = False):
        if not self.product: return None, None
        return self.product.get_size(
            currency = currency,
            country = country,
            attributes = self.attributes
        )

    def ensure_valid(self):
        appier.verify(self.is_valid())

    def try_valid(self):
        self.try_valid_quantity()

    def try_valid_quantity(self):
        if self.quantity < 0: self.quantity = 0
        if self.merchandise.quantity_hand == None: return
        self.quantity = self.quantity if\
            self.quantity <= self.merchandise.quantity_hand else\
            self.merchandise.quantity_hand

    def is_empty(self):
        return self.quantity == 0.0

    def is_dirty(self, currency = None, country = None):
        is_dirty = not self.currency == currency
        is_dirty |= not self.country == country
        is_dirty |= not hasattr(self, "price") or self.price == None
        is_dirty |= not hasattr(self, "taxes") or self.taxes == None
        return is_dirty

    def is_valid(self):
        is_valid = self.is_valid_quantity()
        is_valid &= self.is_valid_price()
        is_valid &= self.is_valid_size()
        return is_valid

    def is_valid_quantity(self, reload = True):
        if self.quantity < 0: return False
        merchandise = self.merchandise and self.merchandise.reload() if\
            reload else self.merchandise
        if not merchandise.quantity_hand == None and\
            self.quantity > merchandise.quantity_hand: return False
        return True

    def is_valid_price(self, reload = True):
        merchandise = self.merchandise and self.merchandise.reload() if\
            reload else self.merchandise
        if not merchandise.quantity_hand == None and\
            not merchandise.price == None and\
            not self.price == merchandise.price: return False
        return True

    def is_valid_size(self, reload = True):
        if not self.product.is_parent: return True
        return True if self.size else False

    @appier.operation(name = "Calculate")
    def calculate_s(self):
        self.calculate(force = True)
        self.save()

    @appier.operation(name = "Measure")
    def measure_s(self):
        self.measure(force = True)
        self.save()

    @property
    def merchandise(self, name = "size", strict = False):
        if not self.size: return self.product
        measurement = self.product.get_measurement(self.size, name = name)
        if measurement or strict: return measurement
        return self.product
