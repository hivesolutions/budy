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

import appier
import appier_extras

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
        ),
        index = "hashed",
        eager = True
    )

    @classmethod
    def list_names(cls):
        return ["id", "key", "total", "currency", "account"]

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

    @classmethod
    def ensure_s(cls, key = None):
        from . import BudyAccount
        account = BudyAccount.from_session(raise_e = False)
        if account: return account.ensure_bag_s(key = key)
        bag = cls(key = key)
        bag.save()
        return bag

    def pre_validate(self):
        bundle.Bundle.pre_validate(self)
        self.try_valid()

    def pre_delete(self):
        bundle.Bundle.pre_delete(self)
        for line in self.lines: line.delete()

    def add_line_s(self, line):
        line.bag = self
        return bundle.Bundle.add_line_s(self, line)

    def to_order_s(self, verify = True, try_valid = True):
        self.refresh_s()
        if try_valid: self.try_valid_s()
        if verify: self.verify_order()
        _order = order.Order(
            currency = self.currency,
            country = self.country,
            sub_total = self.sub_total,
            discounted_sub_total = self.discounted_sub_total,
            undiscounted_sub_total = self.undiscounted_sub_total,
            discount = self.discount,
            shipping_cost = self.shipping_cost,
            taxes = self.taxes,
            total = self.total,
            account = self.account,
            store = self.account and self.account.store
        )
        _order.save()
        _order.lines = []
        for line in self.lines:
            order_line = line.to_order_line_s(_order)
            _order.lines.append(order_line)
        _order.save()
        if verify: _order.verify_base()
        return _order

    def verify_order(self):
        """
        Runs a series of verifications to make sure that the bag
        is ready to be used to generate/create an order.
        """

        appier.verify(len(self.lines) > 0)
        for line in self.lines:
            appier.verify(line.is_valid())

    @appier.operation(name = "Garbage Collect")
    def collect_s(self):
        self.delete()

    @appier.operation(name = "Fix Orphans")
    def fix_orphans_s(self):
        for line in self.lines:
            line.bag = self
            line.save()

    @appier.operation(name = "Notify")
    def notify(self, name = None, *args, **kwargs):
        name = name or "bag.new"
        bag = self.reload(map = True)
        account = bag.get("account", {})
        account = kwargs.get("email", account)
        receiver = account.get("email", None)
        receiver = kwargs.get("email", receiver)
        appier_extras.admin.Event.notify_g(
            name,
            arguments = dict(
                params = dict(
                    payload = bag,
                    bag = bag,
                    receiver = receiver,
                    extra = kwargs
                )
            )
        )

    @appier.operation(name = "Remind")
    def remind(self, *args, **kwargs):
        self.notify("bag.remind", *args, **kwargs)

    @appier.view(name = "Lines")
    def lines_v(self, *args, **kwargs):
        kwargs["sort"] = kwargs.get("sort", [("created", -1)])
        return appier.lazy_dict(
            model = self.lines._target,
            kwargs = kwargs,
            entities = appier.lazy(lambda: self.lines.find(*args, **kwargs)),
            page = appier.lazy(lambda: self.lines.paginate(*args, **kwargs)),
            names = ["product", "quantity", "total", "currency"]
        )
