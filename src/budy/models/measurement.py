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

class Measurement(base.BudyBase):

    name = appier.field(
        index = True,
        default = True
    )

    value = appier.field(
        type = int,
        index = True
    )

    quantity_hand = appier.field(
        type = commons.Decimal,
        index = True
    )

    quantity_reserved = appier.field(
        type = commons.Decimal,
        index = True
    )

    price = appier.field(
        type = commons.Decimal,
        index = True
    )

    taxes = appier.field(
        type = commons.Decimal,
        index = True,
        initial = commons.Decimal(0.0)
    )

    currency = appier.field(
        index = True
    )

    product = appier.field(
        type = appier.reference(
            "Product",
            name = "id"
        )
    )

    @classmethod
    def validate(cls):
        return super(Measurement, cls).validate() + [
            appier.not_null("name"),
            appier.not_empty("name"),

            appier.not_null("value"),

            appier.gte("price", 0.0),

            appier.gte("taxes", 0.0),

            appier.not_null("product")
        ]

    @classmethod
    def list_names(cls):
        return ["id", "name", "value"]

    @classmethod
    def order_name(self):
        return ["id", -1]

    @classmethod
    def from_omni(
        cls,
        merchandise,
        sub_product = None,
        inventory_line = None,
        name = "size",
        currency = "EUR",
        force = False
    ):
        from . import product
        sub_product = sub_product or merchandise
        parent = sub_product["product"]
        object_id = sub_product["object_id"]
        modify_date = merchandise["modify_date"]
        company_product_code = merchandise["company_product_code"]

        # verifies if an inventory line has been provided, if that's the case
        # it's possible to determine a proper modification date for the sub product
        # taking into account also the modification date of its inventory line
        if inventory_line:
            modify_date_line = inventory_line["modify_date"]
            if modify_date_line > modify_date: modify_date = modify_date_line

        _product = product.Product.get(
            product_id = parent["company_product_code"],
            raise_e = False
        )
        if not _product: return None

        value = company_product_code.split("-", 1)[1]
        value = int(value)

        measurement = cls.get(
            product = _product.id,
            name = name,
            value = value,
            raise_e = False
        )
        if not measurement: measurement = cls()

        measurement.name = name
        measurement.value = value
        measurement.currency = currency
        measurement.product = _product
        measurement.meta = dict(
            object_id = object_id,
            modify_date = modify_date
        )
        if "stock_on_hand" in merchandise or force:
            measurement.quantity_hand = merchandise.get("stock_on_hand", 0.0)
        if "retail_price" in merchandise or force:
            measurement.price = merchandise.get("retail_price", 0.0)
        if "price" in merchandise or force:
            base_price = measurement.price if hasattr(measurement, "price") else 0.0
            base_price = base_price or 0.0
            measurement.taxes = base_price - merchandise.get("price", 0.0)
        return measurement

    def get_price(
        self,
        currency = None,
        country = None,
        attributes = None
    ):
        return self.price

    def get_taxes(
        self,
        currency = None,
        country = None,
        attributes = None
    ):
        return self.taxes

    def get_currency(self, currency = None):
        return currency

    def get_size(self, currency = None, country = None, attributes = None):
        return None, None

    @property
    def quantity(self):
        return self.quantity_hand

    @appier.operation(name = "Fix")
    def fix_s(self):
        if not self.exists(): return
        self._fix_value_s()

    @appier.operation(name = "Duplicate", factory = True)
    def duplicate_s(self):
        cls = self.__class__
        measurement = cls(
            product = self.product.id,
            name = self.name,
            value = self.value,
            quantity_hand = self.quantity_hand,
            price = self.price,
            currency = self.currency,
            meta = self.meta
        )
        measurement.save()
        self.product.measurements.append(measurement)
        self.product.save()
        return measurement

    def _fix_value_s(self):
        self.value = int(self.value)
        self.save()

    def _fix_invalid_s(self):
        is_valid = hasattr(self, "parent") and not self.parent == None
        if is_valid: return
        self.delete()
