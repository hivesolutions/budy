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
        name = "size",
        currency = "EUR",
        force = False
    ):
        from . import product
        sub_product = sub_product or merchandise
        parent = sub_product["product"]
        object_id = sub_product["object_id"]
        company_product_code = merchandise["company_product_code"]

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
        measurement.meta = dict(object_id = object_id)
        if "stock_on_hand" in merchandise or force:
            measurement.quantity_hand = merchandise.get("stock_on_hand", 0.0)
        if "retail_price" in merchandise or force:
            measurement.price = merchandise.get("retail_price", 0.0)
        return measurement

    def get_price(
        self,
        currency = None,
        country = None,
        attributes = None
    ):
        return self.price

    def get_currency(self, currency = None):
        return currency

    def get_size(self, currency = None, country = None, attributes = None):
        return None, None

    @property
    def quantity(self):
        return self.quantity_hand

    @appier.operation(name = "Fix Measurement")
    def fix_s(self):
        cls = self.__class__
        self._fix_value_s()
        self._fix_duplicates_s()

    @appier.operation(name = "Duplicate Measurement")
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

    def _fix_value_s(self):
        self.value = int(self.value)
        self.save()

    def _fix_duplicates_s(self):
        cls = self.__class__
        measurements = cls.find(
            product = self.product.id,
            name = self.name,
            value = self.value
        )
        if len(measurements) == 1: return
        for measurement in measurements[1:]:
            measurement.delete()
            parent = measurement.parent
            exists = measurement in parent.measurements
            if not exists: continue
            parent.measurements.remove(measurement)
            parent.save()
