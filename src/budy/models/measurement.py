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

import commons

import appier

from . import base
from . import currency as _currency


class Measurement(base.BudyBase):
    name = appier.field(index=True, default=True)

    value = appier.field(type=int, index=True)

    value_s = appier.field(index=True)

    weight = appier.field(
        type=commons.Decimal,
        index=True,
        observations="""The weight of the current measurement in
        a unit defined by convention (defined before-hand)""",
    )

    quantity_hand = appier.field(type=commons.Decimal, index=True)

    quantity_reserved = appier.field(type=commons.Decimal, index=True)

    price = appier.field(
        type=commons.Decimal,
        index=True,
        initial=commons.Decimal(0.0),
        observations="""Main retail price to be used for
        a possible sale transaction of the measurement (includes taxes)""",
    )

    price_compare = appier.field(
        type=commons.Decimal,
        index=True,
        initial=commons.Decimal(0.0),
        observations="""The price that is going to be used
        as the base for discount calculation purposes""",
    )

    taxes = appier.field(type=commons.Decimal, index=True, initial=commons.Decimal(0.0))

    currency = appier.field(index=True)

    product = appier.field(type=appier.reference("Product", name="id"))

    @classmethod
    def validate(cls):
        return super(Measurement, cls).validate() + [
            appier.not_null("name"),
            appier.not_empty("name"),
            appier.not_null("value"),
            appier.gte("price", 0.0),
            appier.gte("taxes", 0.0),
            appier.not_null("product"),
        ]

    @classmethod
    def list_names(cls):
        return ["id", "name", "value"]

    @classmethod
    def order_name(cls):
        return ["id", -1]

    @classmethod
    def from_omni(
        cls,
        merchandise,
        sub_product=None,
        inventory_line=None,
        inventory_lines=None,
        name="size",
        currency="EUR",
        strip=True,
        path=True,
        force=False,
    ):
        from . import product

        # tries to retrieve the various elements that are going to be used
        # for the proper construction of the measurement from an omni
        # sub product entity (as expected)
        sub_product = sub_product or merchandise
        parent = sub_product["product"]
        object_id = sub_product["object_id"]
        weight = sub_product["weight"]
        modify_date = merchandise["modify_date"]
        company_product_code = merchandise["company_product_code"]
        metadata = merchandise["metadata"] or dict()
        price_compare = metadata.get("compare_price") or None
        discount = metadata.get("discount") or None

        # verifies if an inventory line has been provided, if that's the case
        # it's possible to determine a proper modification date for the sub product
        # taking into account also the modification date of its inventory line
        if inventory_line:
            modify_date_line = inventory_line["modify_date"]
            if modify_date_line > modify_date:
                modify_date = modify_date_line

        # tries to retrieve the parent product for this measurement using the
        # associated company product code as reference if there's no such parent
        # product then it's not possible to continue with the import operation
        _product = product.Product.get(
            product_id=parent["company_product_code"], raise_e=False
        )
        if not _product:
            return None

        # in case the discount at a merchandise level is not defined
        # then tries to use the one coming from the (parent) product
        if discount == None:
            discount = _product.meta.get("discount", None)

        # creates the stocks list in case there are valid inventory lines being
        # passed on the current measurement update/creation
        stocks = None if inventory_lines == None else []

        # iterates over the complete set of available inventory lines to build the
        # associated stock dictionary with the information on the stock point, this
        # is going to be added to the list of stocks to the measurement
        for inventory_line in inventory_lines if inventory_lines else []:
            stock_on_hand = inventory_line.get("stock_on_hand", 0)
            stock_reserved = inventory_line.get("stock_reserved", 0)
            stock_in_transit = inventory_line.get("stock_in_transit", 0)
            retail_price = inventory_line.get("retail_price", {}).get("value", 0.0)
            functional_unit = inventory_line.get("functional_unit", None)

            is_valid = functional_unit and functional_unit.get("status") == 1
            if not is_valid:
                continue

            stock_m = dict(
                store_id=functional_unit["object_id"],
                store_name=functional_unit["name"],
                stock_on_hand=stock_on_hand,
                stock_reserved=stock_reserved,
                stock_in_transit=stock_in_transit,
                retail_price=retail_price,
            )
            stocks.append(stock_m)

        # splits the provided company product code into its base part
        # and the sub code part (to be used as the measure value)
        value = company_product_code.split("-", 1)[1]

        # sets the string based value of the measurement as the raw
        # value of company product code split (as expected) note that
        # the strip flag controls if extra zeroes to the left should
        # be removed from the value (avoids extra values)
        value_s = value.lstrip("0") if strip else value

        # tries converts the value into an integer value, falling back
        # to the absolute hash value of it in case there's an error
        try:
            value = int(value)
        except ValueError:
            value = cls._hash(value)

        # tries to retrieve a measurement that is considered to be equivalent
        # to the one described by the associated subproduct in case it does
        # not exists creates a new instance that is going to be populate
        measurement = cls.get(
            product=_product.id, name=name, value=value, raise_e=False
        )
        if not measurement:
            measurement = cls()

        measurement.name = name
        measurement.value = value
        measurement.value_s = value_s
        measurement.weight = weight
        measurement.price_compare = price_compare
        measurement.currency = currency
        measurement.product = _product

        meta = dict(
            object_id=object_id,
            company_product_code=company_product_code,
            modify_date=modify_date,
            discount=discount,
        )
        if hasattr(measurement, "meta") and measurement.meta:
            measurement.meta.update(meta)
        else:
            measurement.meta = meta
        if not stocks == None:
            measurement.meta["stocks"] = stocks

        if "stock_on_hand" in merchandise or force:
            measurement.quantity_hand = merchandise.get("stock_on_hand", 0.0)
        if "retail_price" in merchandise or force:
            # "grabs" the retail price from the original merchandise entity
            # from Omni to be used as the base calculus
            retail_price = merchandise.get("retail_price", 0.0)

            # stores the "original" retail price in the measurement's metadata
            # storage may be needed latter for update operations
            measurement.meta["retail_price"] = retail_price

        if "price" in merchandise or force:
            # "grabs" the (untaxed) price from the original merchandise entity
            # from Omni to be used as the base calculus
            untaxed_price = merchandise.get("price", 0.0)

            # stores the "original" untaxed price in the measurement's metadata
            # storage may be needed latter for update operations
            measurement.meta["untaxed_price"] = untaxed_price

        # in case all of the required "original" financial information (prices)
        # is available then the price, taxes and price compare are calculated
        if "retail_price" in measurement.meta and "untaxed_price" in measurement.meta:
            untaxed_price = (
                _currency.Currency.round(
                    measurement.meta["untaxed_price"] * ((100.0 - discount) / 100.0),
                    currency,
                )
                if discount
                else measurement.meta["untaxed_price"]
            )
            measurement.price = (
                _currency.Currency.round(
                    measurement.meta["retail_price"] * ((100.0 - discount) / 100.0),
                    currency,
                )
                if discount
                else measurement.meta["retail_price"]
            )
            measurement.taxes = measurement.price - untaxed_price
            if not measurement.price_compare and discount:
                measurement.price_compare = measurement.meta["retail_price"]

        # returns the "final" measurement instance to the caller so that it's possible
        # to properly save the newly generated measurement instance according to omni
        return measurement

    @classmethod
    def _hash(cls, value, max_size=8):
        counter = 0
        for index in range(len(value)):
            value_i = appier.legacy.ord(value[index])
            counter += value_i * pow(256, index)
        if not max_size:
            return counter
        modulus = pow(256, max_size)
        counter = counter % modulus
        return counter

    def pre_delete(self):
        base.BudyBase.pre_delete(self)
        if not self.product:
            return
        if not hasattr(self.product, "measurements"):
            return
        if not self in self.product.measurements:
            return
        self.product.measurements.remove(self)
        self.product.save()

    def get_price(self, currency=None, country=None, attributes=None):
        return self.price

    def get_taxes(self, currency=None, country=None, attributes=None):
        return self.taxes

    def get_currency(self, currency=None):
        return currency

    def get_size(self, currency=None, country=None, attributes=None):
        return None, None

    @property
    def product_id(self):
        if self._product_id_meta:
            return self._product_id_meta
        return None

    @property
    def short_description(self):
        return self.product.short_description

    @property
    def quantity(self):
        return self.quantity_hand

    @property
    def discount(self):
        if not self.price:
            return commons.Decimal(0.0)
        if not self.price_compare:
            return commons.Decimal(0.0)
        return self.price_compare - self.price

    @property
    def discount_percent(self):
        if not self.discount:
            return commons.Decimal(0.0)
        return self.discount / self.price_compare * commons.Decimal(100.0)

    @property
    def is_discounted(self):
        return self.discount > 0.0

    @property
    def is_discountable(self):
        return self.product.is_discountable

    @property
    def is_price_provided(self):
        return False

    @appier.operation(name="Fix")
    def fix_s(self):
        if not self.exists():
            return
        self._fix_value_s()

    @appier.operation(name="Duplicate", factory=True)
    def duplicate_s(self):
        cls = self.__class__
        measurement = cls(
            product=self.product.id,
            name=self.name,
            value=self.value,
            value_s=self.value_s,
            quantity_hand=self.quantity_hand,
            price=self.price,
            currency=self.currency,
            meta=self.meta,
        )
        measurement.save()
        self.product.measurements.append(measurement)
        self.product.save()
        return measurement

    @property
    def _product_id_meta(self):
        if not self.meta:
            return None
        return self.meta.get("company_product_code", None)

    def _fix_value_s(self):
        cls = self.__class__
        try:
            self.value = int(self.value)
        except ValueError:
            self.value = self._hash(self.value)
        self.save()

    def _fix_invalid_s(self):
        is_valid = hasattr(self, "parent") and not self.parent == None
        if is_valid:
            return
        self.delete()
