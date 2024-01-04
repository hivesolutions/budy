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

from . import base


class Address(base.BudyBase):
    key = appier.field(index=True, safe=True, immutable=True)

    first_name = appier.field(index=True)

    last_name = appier.field(index=True)

    tax_number = appier.field(index=True)

    address = appier.field()

    address_extra = appier.field()

    postal_code = appier.field()

    city = appier.field()

    state = appier.field()

    country = appier.field(meta="country")

    phone_number = appier.field()

    vat_number = appier.field(description="VAT Number")

    neighborhood = appier.field()

    @classmethod
    def validate(cls):
        return super(Address, cls).validate() + [
            appier.not_null("first_name"),
            appier.not_empty("first_name"),
            appier.not_null("last_name"),
            appier.not_empty("last_name"),
            appier.not_null("address"),
            appier.not_empty("address"),
            appier.not_null("city"),
            appier.not_empty("city"),
            appier.string_eq("country", 2),
        ]

    @classmethod
    def list_names(cls):
        return ["id", "first_name", "last_name", "address", "country"]

    @classmethod
    def unique_names(cls):
        return super(Address, cls).unique_names() + ["key"]

    @classmethod
    def order_name(cls):
        return ["id", -1]

    @classmethod
    def _plural(cls):
        return "Addresses"

    def pre_create(self):
        base.BudyBase.pre_create(self)
        if not hasattr(self, "key") or not self.key:
            self.key = self.secret()
        self.description = self.key[:8]

    @property
    def full_name(self):
        if not self.last_name:
            return self.first_name
        return self.first_name + " " + self.last_name
