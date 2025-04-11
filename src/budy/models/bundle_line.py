#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Budy
# Copyright (c) 2008-2024 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2024 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import json
import commons

import appier

from . import base


class BundleLine(base.BudyBase):
    price = appier.field(
        type=commons.Decimal,
        observations="""The unit price for the item described by the
        current line, the total should be calculated using this value""",
    )

    taxes = appier.field(
        type=commons.Decimal,
        observations="""The amount of taxes paid per each item in the
        current line, this value is already included in the price value
        of the line""",
    )

    currency = appier.field(
        observations="""The currency in use for the line all the price
        related values for the line are considered to be represented
        under this given currency"""
    )

    country = appier.field()

    quantity = appier.field(type=commons.Decimal, initial=commons.Decimal(0.0))

    total = appier.field(type=commons.Decimal, initial=commons.Decimal(0.0))

    total_taxes = appier.field(type=commons.Decimal, initial=commons.Decimal(0.0))

    size = appier.field(type=int)

    size_s = appier.field()

    scale = appier.field(type=int)

    discounted = appier.field(
        type=bool,
        initial=False,
        index=True,
        observations="""If the product associated with the
        current line is a discounted one, meaning that the product
        price is affected by some discount""",
    )

    closed = appier.field(
        type=bool,
        initial=False,
        index=True,
        observations="""Simple flag that control if the line is
        closed meaning that calculated values (eg: totals) can no
        longer be re-calculated as the line is now frozen""",
    )

    attributes = appier.field(
        observations="""Additional metadata that define the given
        (bundle) line, this is typically used to store a JSON serialized
        string with extra fields"""
    )

    product = appier.field(
        type=appier.reference("Product", name="id"),
        eager=True,
        observations="""The product that this bundle line is
        associated with, this is the product that is going to
        be used for the calculation of the price""",
    )

    @classmethod
    def list_names(cls):
        return ["id", "quantity", "total", "currency", "product"]

    @classmethod
    def order_name(cls):
        return ["id", -1]

    @classmethod
    def is_abstract(cls):
        return True

    def pre_save(self):
        base.BudyBase.pre_save(self)
        self.calculate()
        self.measure()
        self.ensure_valid()

    def calculate(self, currency=None, country=None, force=False):
        if self.closed:
            return
        currency = currency or self.currency
        country = country or self.country
        self.total_taxes = self.quantity * self.get_taxes(
            currency=currency, country=country, force=force
        )
        self.total = self.quantity * self.get_price(
            currency=currency, country=country, force=force
        )
        self.discounted = self.merchandise.is_discounted

    def measure(self, currency=None, country=None, force=False):
        if self.closed:
            return
        if self.size and self.scale and not force:
            return
        self.size, self.scale = self.get_size(
            currency=currency, country=country, force=force
        )

    def close_s(self):
        self.closed = True
        self.save()

    def get_price(self, currency=None, country=None, force=False):
        is_dirty = self.is_dirty(currency=currency, country=country)
        if not is_dirty and not force:
            return self.price
        self.price = self.merchandise.get_price(
            currency=currency, country=country, attributes=self.attributes
        )
        self.taxes = self.merchandise.get_taxes(
            currency=currency, country=country, attributes=self.attributes
        )
        self.currency = self.merchandise.get_currency(currency=currency)
        self.country = country
        return self.price

    def get_taxes(self, currency=None, country=None, force=False):
        self.get_price(currency=currency, country=country, force=force)
        return self.taxes

    def get_size(self, currency=None, country=None, force=False):
        if not self.product:
            return None, None
        return self.product.get_size(
            currency=currency, country=country, attributes=self.attributes
        )

    def ensure_size_s(self):
        if not self.size:
            return
        if not hasattr(self.merchandise, "value_s"):
            return
        self.size_s = self.merchandise.value_s

    def ensure_valid(self):
        appier.verify(self.is_valid())

    def try_valid(self, bundle=None):
        fixed = False
        fixed |= self.try_valid_quantity(bundle=bundle)
        fixed |= self.try_valid_price(bundle=bundle)
        return fixed

    def try_valid_s(self, bundle=None):
        fixed = self.try_valid(bundle=bundle)
        if not fixed:
            return fixed
        self.save()
        return fixed

    def try_valid_quantity(self, bundle=None):
        fixed = False
        quantity = (
            bundle.merchandise_quantity(self.merchandise) if bundle else self.quantity
        )
        if quantity <= 0.0:
            quantity = 0.0
        if self.merchandise.quantity_hand == None:
            return fixed
        if quantity <= self.merchandise.quantity_hand:
            return fixed
        other_quantity = quantity - self.quantity
        self.quantity = max(
            min(self.quantity, self.merchandise.quantity_hand - other_quantity), 0
        )
        self.calculate(force=True)
        fixed |= True
        return fixed

    def try_valid_price(self, bundle):
        fixed = False
        if self.merchandise.is_price_provided:
            return fixed
        if self.merchandise.price == None:
            return fixed
        if self.merchandise.price == self.price:
            return fixed
        self.price = self.merchandise.price
        self.calculate(force=True)
        fixed |= True
        return fixed

    def is_empty(self):
        return self.quantity == 0.0

    def is_dirty(self, currency=None, country=None):
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

    def is_discountable(self, strict=False):
        if not self.merchandise.is_discountable:
            return False
        if strict and self.discounted:
            return False
        return True

    def is_valid_quantity(self, reload=True):
        if self.quantity < 0:
            return False
        merchandise = (
            self.merchandise and self.merchandise.reload()
            if reload
            else self.merchandise
        )
        if (
            not merchandise.quantity_hand == None
            and self.quantity > merchandise.quantity_hand
        ):
            return False
        return True

    def is_valid_price(self, reload=True):
        merchandise = (
            self.merchandise and self.merchandise.reload()
            if reload
            else self.merchandise
        )
        if (
            not merchandise.is_price_provided
            and not merchandise.price == None
            and not self.price == merchandise.price
        ):
            return False
        return True

    def is_valid_size(self, reload=True):
        if not self.product.is_parent:
            return True
        return True if self.size else False

    @appier.operation(name="Calculate")
    def calculate_s(self):
        self.calculate(force=True)
        self.save()

    @appier.operation(name="Measure")
    def measure_s(self):
        self.measure(force=True)
        self.save()

    @appier.operation(name="Recover product")
    def recover_s(self):
        from . import product

        self.product.resolve()
        if self.product.is_resolved():
            return

        if not self.attributes:
            return
        attributes = json.loads(self.attributes)

        product_id = attributes.get("product_id", None)
        if not product_id:
            return
        product_id_s = str(product_id)

        _product = product.Product.get(product_id=product_id_s)
        if not _product:
            return

        self.product = _product
        self.save(validate=False, pre_save=False)

    @property
    def merchandise(self, name="size", strict=False):
        if not self.size:
            return self.product
        if not hasattr(self.product, "get_measurement"):
            return self.product
        measurement = self.product.get_measurement(self.size, name=name)
        if measurement or strict:
            return measurement
        return self.product
