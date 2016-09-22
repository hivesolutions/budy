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
from . import bundle_line

class Bundle(base.BudyBase):

    key = appier.field(
        index = True,
        safe = True,
        immutable = True
    )

    currency = appier.field(
        index = True
    )

    country = appier.field(
        index = True
    )

    quantity = appier.field(
        type = commons.Decimal,
        index = True,
        initial = commons.Decimal(0.0),
        safe = True
    )

    sub_total = appier.field(
        type = commons.Decimal,
        index = True,
        initial = commons.Decimal(0.0),
        safe = True
    )

    discount = appier.field(
        type = commons.Decimal,
        index = True,
        initial = commons.Decimal(0.0),
        safe = True
    )

    discount_fixed = appier.field(
        type = commons.Decimal,
        index = True,
        initial = commons.Decimal(0.0),
        safe = True
    )

    discount_dynamic = appier.field(
        type = commons.Decimal,
        index = True,
        initial = commons.Decimal(0.0),
        safe = True
    )

    shipping_cost = appier.field(
        type = commons.Decimal,
        index = True,
        initial = commons.Decimal(0.0),
        safe = True
    )

    taxes = appier.field(
        type = commons.Decimal,
        index = True,
        initial = commons.Decimal(0.0),
        safe = True
    )

    total = appier.field(
        type = commons.Decimal,
        index = True,
        initial = commons.Decimal(0.0),
        safe = True
    )

    ip_address = appier.field(
        index = True,
        safe = True
    )

    ip_country = appier.field(
        index = True,
        safe = True,
        meta = "country"
    )

    referrals = appier.field(
        type = appier.references(
            "Referral",
            name = "name"
        ),
        eager = True
    )

    @classmethod
    def validate(cls):
        return super(Bundle, cls).validate() + [
            appier.not_duplicate("key", cls._name()),

            appier.not_null("quantity"),
            appier.gte("quantity", 0.0),

            appier.not_null("sub_total"),
            appier.gte("sub_total", 0.0),

            appier.not_null("discount"),
            appier.gte("discount", 0.0),

            appier.not_null("shipping_cost"),
            appier.gte("shipping_cost", 0.0),

            appier.not_null("taxes"),
            appier.gte("taxes", 0.0),

            appier.not_null("total"),
            appier.gte("total", 0.0),

            appier.string_eq("ip_country", 2)
        ]

    @classmethod
    def list_names(cls):
        return ["id", "key", "total", "currency"]

    @classmethod
    def order_name(self):
        return ["id", -1]

    @classmethod
    def line_cls(cls):
        return bundle_line.BundleLine

    @classmethod
    def eval_discount(cls, *args, **kwargs):
        discount = appier.conf("BUDY_DISCOUNT", None)
        if not discount: return 0.0
        discount = eval(discount)
        return discount(*args, **kwargs)

    @classmethod
    def eval_shipping(cls, *args, **kwargs):
        shipping = appier.conf("BUDY_SHIPPING", None)
        if not shipping: return 0.0
        shipping = eval(shipping)
        return shipping(*args, **kwargs)

    @classmethod
    def eval_taxes(cls, *args, **kwargs):
        taxes = appier.conf("BUDY_TAXES", None)
        if not taxes: return 0.0
        taxes = eval(taxes)
        return taxes(*args, **kwargs)

    def pre_validate(self):
        base.BudyBase.pre_validate(self)
        self.calculate()

    def pre_save(self):
        base.BudyBase.pre_save(self)
        self.ensure_valid()

    def pre_create(self):
        base.BudyBase.pre_create(self)
        if not hasattr(self, "key") or not self.key:
            self.key = self.secret()
        self.description = self.key[:8]

    def set_ip_address_s(self, ip_address):
        result = appier.GeoResolver.resolve(ip_address) or {}
        country = result.get("country", {})
        ip_country = country.get("iso_code", None)
        self.ip_address = ip_address
        self.ip_country = ip_country
        self.save()

    def add_line_s(self, line):
        line.save()
        self.lines.append(line)
        self.save()
        return line

    def remove_line_s(self, line_id):
        match = None
        for line in self.lines:
            if not line.id == line_id: continue
            match = line
            break
        if not match: return
        self.lines.remove(match)
        self.save()
        match.delete()

    def add_product_s(
        self,
        product,
        quantity = 1.0,
        size = None,
        scale = None,
        attributes = None,
        increment = True
    ):
        cls = self.__class__

        _line = None

        if not product: raise appier.OperationalError(
            message = "No product defined"
        )

        for line in self.lines:
            is_same = line.product.id == product.id
            is_same &= line.size == size
            is_same &= line.scale == scale
            is_same &= line.attributes == attributes
            if not is_same: continue
            _line = line

        if _line:
            if not increment: return _line
            _line.quantity += quantity
            _line.save()
            self.save()
            return _line

        _line = cls.line_cls()(
            product = product,
            quantity = quantity,
            size = size,
            scale = scale,
            attributes = attributes
        )
        self.add_line_s(_line)

        return _line

    def add_update_line_s(self, line, increment = True):
        return self.add_product_s(
            line.product,
            quantity = line.quantity,
            size = line.size,
            scale = line.scale,
            attributes = line.attributes,
            increment = increment
        )

    def merge_s(self, bag_id, increment = False):
        cls = self.__class__
        if bag_id == self.id: return
        bag = cls.get(id = bag_id)
        for line in bag.lines:
            line = line.clone()
            self.add_update_line_s(line, increment = increment)
        self.refresh_s()

    def refresh_s(self, currency = None, country = None, force = False):
        currency = currency or self.currency
        country = country or self.country
        is_dirty = self.is_dirty(currency = currency, country = country)
        if not is_dirty and not force: return False
        lines = self.lines if hasattr(self, "lines") else []
        for line in lines:
            is_dirty = line.is_dirty(
                currency = currency,
                country = country
            )
            if not is_dirty: continue
            line.calculate(currency = currency, country = country)
            line.save()
        self.currency = currency
        self.country = country
        self.save()
        return True

    def add_referral_s(self, referral):
        self.referrals.append(referral)
        self.save()

    def set_referral_s(self, referral):
        self.empty_referrals_s()
        self.add_referral_s(referral)

    def empty_referrals_s(self):
        self.referrals = []
        self.save()

    def calculate(self):
        lines = self.lines if hasattr(self, "lines") else []
        self.quantity = sum(line.quantity for line in lines)
        self.sub_total = sum(line.total for line in lines)
        self.discount = self.calculate_discount()
        self.taxes = self.calculate_taxes()
        self.shipping_cost = self.calculate_shipping()
        self.total = self.sub_total - self.discount + self.shipping_cost

    def calculate_discount(self):
        discount = self.build_discount()
        discount = min(discount, self.discountable)
        return max(discount, 0.0)

    def calculate_taxes(self):
        return self.build_taxes()

    def calculate_shipping(self):
        return self.build_shipping()

    def build_discount(self):
        discount = 0.0
        join_discount = appier.conf("BUDY_JOIN_DICOUNT", True, cast = bool)
        self.discount_dynamic = self.__class__.eval_discount(
            self.sub_total,
            self.taxes,
            self.quantity,
            self
        )
        if join_discount:
            discount += self.discount_dynamic
            discount += self.discount_fixed
        else:
            discount += max(self.discount_dynamic, self.discount_fixed)
        return discount

    def build_taxes(self):
        taxes = 0.0
        join_taxes = appier.conf("BUDY_JOIN_TAXES", True, cast = bool)
        taxes_dynamic = self.__class__.eval_taxes(
            self.sub_total,
            self.taxes,
            self.quantity,
            self
        )
        taxes_lines = sum(line.total_taxes for line in self.lines)
        if join_taxes:
            taxes += taxes_dynamic
            taxes += taxes_lines
        else:
            taxes += max(taxes_dynamic, taxes_lines)
        return taxes

    def build_shipping(self):
        return self.__class__.eval_shipping(
            self.sub_total,
            self.taxes,
            self.quantity,
            self
        )

    def collect_empty(self):
        empty = []
        for line in self.lines:
            is_empty = line.is_empty()
            if is_empty: empty.append(line)
        for line in empty: self.lines.remove(line)

    def try_valid(self):
        for line in self.lines: line.try_valid()
        self.collect_empty()

    def ensure_valid(self):
        appier.verify(self.is_valid())

    def is_dirty(self, currency = None, country = None):
        dirty = False
        lines = self.lines if hasattr(self, "lines") else []
        for line in lines: dirty |= line.is_dirty(
            currency = currency,
            country = country
        )
        return dirty

    def is_valid(self):
        is_valid = True
        for line in self.lines: is_valid &= line.is_valid()
        return is_valid

    @appier.operation(name = "Empty")
    def empty_s(self):
        for line in self.lines: line.delete()
        self.lines = []
        self.save()

    @appier.operation(name = "Fix Sub Total")
    def fix_sub_total_s(self):
        if self.sub_total: return
        self.sub_total = self.total
        self.save()

    @appier.operation(name = "Calculate")
    def calculate_s(self):
        self.calculate()
        self.save()

    @property
    def discountable(self):
        return self.sub_total

    @property
    def discount_base(self):
        return self.discount_fixed + self.discount_dynamic
