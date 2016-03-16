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
from . import order
from . import bag_line

class Bag(base.BudyBase):

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

    total = appier.field(
        type = float,
        index = True,
        initial = 0.0,
        safe = True
    )

    discount = appier.field(
        type = float,
        index = True,
        initial = 0.0,
        safe = True
    )

    taxes = appier.field(
        type = float,
        index = True,
        initial = 0.0,
        safe = True
    )

    shipping_cost = appier.field(
        type = float,
        index = True,
        initial = 0.0,
        safe = True
    )

    lines = appier.field(
        type = appier.references(
            "BagLine",
            name = "id"
        )
    )

    account = appier.field(
        type = appier.references(
            "BudyAccount",
            name = "id"
        )
    )

    def __init__(self, *args, **kwargs):
        base.BudyBase.__init__(self, *args, **kwargs)
        self.currency = kwargs.get("currency", None)
        self.country = kwargs.get("country", None)
        self.total = kwargs.get("total", 0.0)
        self.discount = kwargs.get("discount", 0.0)
        self.taxes = kwargs.get("taxes", 0.0)
        self.shipping_cost = kwargs.get("shipping_cost", 0.0)

    @classmethod
    def list_names(cls):
        return ["id", "key", "currency", "total"]

    @classmethod
    def from_session(cls, ensure = True, raise_e = False):
        from . import BudyAccount
        account = BudyAccount.from_session(raise_e = raise_e)
        if account: return account.get_bag()
        session = appier.get_session()
        key = session.get("bag", None)
        bag = cls.get(key = key, raise_e = raise_e)
        if bag: return bag
        if not ensure: return None
        bag = cls()
        bag.save()
        session["bag"] = bag.key
        return bag

    def pre_create(self):
        base.BudyBase.pre_create(self)
        self.key = self.secret()
        self.description = self.key[:8]

    def pre_save(self):
        base.BudyBase.pre_save(self)
        self.calculate()

    def empty_s(self):
        for line in self.lines: line.delete()
        self.lines = []
        self.save()

    def add_line_s(self, line):
        line.bag = self
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
        attributes = None
    ):
        _line = None

        for line in self.lines:
            is_same = line.product.id == product.id
            is_same &= line.size == size
            is_same &= line.scale == scale
            is_same &= line.attributes == attributes
            if not is_same: continue
            _line = line

        if _line:
            _line.quantity += quantity
            _line.save()
            self.save()
            return _line

        _line = bag_line.BagLine(
            product = product,
            quantity = quantity,
            size = size,
            scale = scale,
            attributes = attributes
        )
        self.add_line_s(_line)

        return _line

    def add_update_line_s(self, line):
        return self.add_product_s(
            line.product,
            quantity = line.quantity,
            size = line.size,
            scale = line.scale,
            attributes = line.attributes
        )

    def merge_s(self, bag_id):
        bag = Bag.get(id = bag_id)
        for line in bag.lines:
            line = line.clone()
            self.add_update_line_s(line)

    def refresh_s(self, currency = None, country = None, force = False):
        is_dirty = self.is_dirty(currency = currency, country = country)
        if not is_dirty and not force: return
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

    def to_order_s(self):
        #@todo must complete this with proper creation of order
        order = order.Order(
            currency = self.currency,
            country = self.country
        )
        order.save()
        return order

    def calculate(self):
        lines = self.lines if hasattr(self, "lines") else []
        self.total = sum(line.total for line in lines)

    def is_dirty(self, currency = None, country = None):
        dirty = False
        lines = self.lines if hasattr(self, "lines") else []
        for line in lines: dirty |= line.is_dirty(
            currency = currency,
            country = country
        )
        return dirty
