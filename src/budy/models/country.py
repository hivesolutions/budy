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


class Country(base.BudyBase):
    name = appier.field(index=True, default=True)

    country_code = appier.field(index=True)

    currency_code = appier.field(index=True)

    locale = appier.field(index=True)

    @classmethod
    def validate(cls):
        return super(Country, cls).validate() + [
            appier.not_null("name"),
            appier.not_empty("name"),
            appier.not_null("country_code"),
            appier.not_empty("country_code"),
            appier.string_eq("country_code", 2),
            appier.not_null("currency_code"),
            appier.not_empty("currency_code"),
            appier.string_eq("currency_code", 3),
            appier.not_null("locale"),
            appier.not_empty("locale"),
            appier.string_eq("locale", 5),
        ]

    @classmethod
    def list_names(cls):
        return ["id", "name", "country_code", "currency_code", "locale"]

    @classmethod
    def get_by_code(cls, country_code, *args, **kwargs):
        return cls.get(country_code=country_code, *args, **kwargs)

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
            name, country_code, currency_code, locale = line
            name = name or None
            country_code = country_code or None
            currency_code = currency_code or None
            locale = locale or None
            country = cls(
                name=name,
                country_code=country_code,
                currency_code=currency_code,
                locale=locale,
            )
            country.save()

        if empty:
            cls.delete_c()
        cls._csv_import(file, callback)

    @classmethod
    @appier.link(name="Export Simple")
    def simple_csv_url(cls, absolute=False):
        return appier.get_app().url_for("country_api.simple_csv", absolute=absolute)

    @classmethod
    def _plural(cls):
        return "Countries"
