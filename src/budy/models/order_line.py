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

from . import bundle_line


class OrderLine(bundle_line.BundleLine):
    order = appier.field(type=appier.reference("Order", name="id"))

    @classmethod
    def list_names(cls):
        return ["id", "quantity", "total", "currency", "product", "order"]

    @classmethod
    def is_visible(cls):
        return False

    def is_valid_quantity(self, reload=True):
        order = self.order and self.order.reload() if reload else self.order
        if order and order.is_closed():
            return True
        return bundle_line.BundleLine.is_valid_quantity(self, reload=reload)

    def is_valid_price(self, reload=True):
        order = self.order and self.order.reload() if reload else self.order
        if order and order.is_closed():
            return True
        return bundle_line.BundleLine.is_valid_price(self, reload=reload)

    @appier.operation(name="Garbage Collect")
    def collect_s(self):
        if appier.is_unset(self.bag):
            return
        self.delete()

    @property
    def bundle(self):
        return self.order
