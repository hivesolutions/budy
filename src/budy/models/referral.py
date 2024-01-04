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


class Referral(base.BudyBase):
    name = appier.field(index=True, default=True)

    @classmethod
    def validate(cls):
        return super(Referral, cls).validate() + [
            appier.not_null("name"),
            appier.not_empty("name"),
            appier.string_gt("name", 3),
            appier.string_lt("name", 64),
            appier.not_duplicate("name", cls._name()),
        ]

    @classmethod
    def list_names(cls):
        return ["id", "name"]

    @classmethod
    def order_name(cls):
        return ["id", -1]

    @classmethod
    @appier.operation(
        name="Import CSV",
        parameters=(
            ("CSV File", "file", "file"),
            ("Empty source", "empty", bool, False),
        ),
    )
    def import_csv_s(cls, file, empty):
        def callback(line):
            store, name = line
            composed_name = "%s|%s" % (name, store)
            referral = cls(name=composed_name)
            referral.save()

        if empty:
            cls.delete_c()
        cls._csv_import(file, callback)
