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

import appier

from . import order_line
from . import bundle_line


class BagLine(bundle_line.BundleLine):
    bag = appier.field(type=appier.reference("Bag", name="id"))

    @classmethod
    def list_names(cls):
        return ["id", "quantity", "total", "currency", "product", "bag"]

    @classmethod
    def is_visible(cls):
        return False

    def pre_validate(self):
        bundle_line.BundleLine.pre_validate(self)
        self.try_valid()

    def to_order_line_s(self, order=None):
        _order_line = order_line.OrderLine(
            price=self.price,
            currency=self.currency,
            country=self.country,
            quantity=self.quantity,
            total=self.total,
            size=self.size,
            size_s=self.size_s,
            scale=self.scale,
            discounted=self.discounted,
            attributes=self.attributes,
            product=self.product,
            order=order,
        )
        _order_line.save()
        return _order_line

    @appier.operation(name="Garbage Collect")
    def collect_s(self):
        if appier.is_unset(self.bag):
            return
        self.delete()

    @property
    def bundle(self):
        return self.bag
