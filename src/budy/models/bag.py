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
from . import bag_line

class Bag(base.BudyBase):

    key = appier.field(
        index = True,
        safe = True,
        immutable = True
    )

    currency = appier.field(
        index = True,
        initial = "EUR"
    )

    total = appier.field(
        type = float,
        index = True,
        safe = True
    )

    lines = appier.field(
        type = appier.references(
            "BagLine",
            name = "id"
        )
    )

    @classmethod
    def validate(cls):
        return super(Bag, cls).validate() + [
            appier.not_null("currency"),
            appier.not_empty("currency")
        ]

    @classmethod
    def list_names(cls):
        return ["id", "key", "currency", "total"]

    def pre_create(self):
        base.BudyBase.pre_create(self)
        self.key = self.secret()
        self.description = self.key

    def pre_save(self):
        base.BudyBase.pre_save(self)
        self._calculate()

    def add_line_s(self, bag_line):
        bag_line.bag = self
        bag_line.save()
        self.lines.append(bag_line)
        self.save()
        return bag_line

    def add_product_s(self, product, quantity = 1.0):
        self.reload()

        _bag_line = None

        for line in self.lines:
            is_same = line.product.id == product.id
            if not is_same: continue
            _bag_line = line

        if _bag_line:
            _bag_line.quantity += quantity
            _bag_line.save()
            self.save()
            return

        _bag_line = bag_line.BagLine(
            product = product,
            quantity = quantity
        )
        self.add_line_s(_bag_line)

    def _calculate(self):
        lines = self.lines if hasattr(self, "lines") else []
        self.total = sum(line.total for line in lines)
