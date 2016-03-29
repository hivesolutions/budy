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

from . import order
from . import bundle
from . import bag_line

class Bag(bundle.Bundle):

    lines = appier.field(
        type = appier.references(
            "BagLine",
            name = "id"
        ),
        eager = True
    )

    account = appier.field(
        type = appier.reference(
            "BudyAccount",
            name = "id"
        )
    )

    @classmethod
    def list_names(cls):
        return ["id", "key", "currency", "total", "account"]

    @classmethod
    def order_name(self):
        return ["id", -1]

    @classmethod
    def line_cls(cls):
        return bag_line.BagLine

    @classmethod
    def from_session(cls, ensure = True, raise_e = False):
        from . import BudyAccount
        account = BudyAccount.from_session(raise_e = raise_e)
        if account: return account.ensure_bag_s()
        session = appier.get_session()
        key = session.get("bag", None)
        bag = cls.get(key = key, raise_e = raise_e) if key else None
        if bag: return bag
        if not ensure: return None
        bag = cls()
        bag.save()
        session["bag"] = bag.key
        return bag

    def add_line_s(self, line):
        line.bag = self
        return bundle.Bundle.add_line_s(self, line)

    def to_order_s(self):
        self.refresh_s()
        _order = order.Order(
            currency = self.currency,
            country = self.country,
            total = self.total,
            discount = self.discount,
            taxes = self.taxes,
            shipping_cost = self.shipping_cost,
            account = self.account
        )
        _order.lines = []
        for line in self.lines:
            order_line = line.to_order_line_s()
            _order.lines.append(order_line)
        _order.save()
        return _order

    @appier.operation(name = "Empty Bag")
    def empty_bag_s(self):
        for line in self.lines: line.delete()
        self.lines = []
        self.save()
