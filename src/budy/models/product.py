#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Budy
# Copyright (C) 2008-2015 Hive Solutions Lda.
#
# This file is part of Hive Budy.
#
# Hive Budy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hive Budy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hive Budy. If not, see <http://www.gnu.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2015 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

import appier

from . import base

class Product(base.BudyBase):

    GENDER_S = {
        "Male" : "Male",
        "Female" : "Female",
        "Both" : "Both"
    }

    short_description = appier.field(
        index = True,
        default = True
    )

    product_id = appier.field(
        index = True
    )

    gender = appier.field(
        index = True,
        meta = "enum",
        enum = GENDER_S
    )

    price = appier.field(
        type = float,
        index = True
    )

    tag = appier.field()

    tag_descritpion = appier.field()

    farfetch_url = appier.field(
        index = True,
        meta = "url"
    )

    categories = appier.field(
        type = appier.references(
            "Category",
            name = "id"
        )
    )

    variants = appier.field(
        type = appier.references(
            "Product",
            name = "id"
        )
    )

    images = appier.field(
        type = appier.references(
            "Media",
            name = "id"
        )
    )

    brand = appier.field(
        type = appier.reference(
            "Brand",
            name = "id"
        )
    )

    season = appier.field(
        type = appier.reference(
            "Season",
            name = "id"
        )
    )

    measurements = appier.field(
        type = appier.references(
            "Measurement",
            name = "id"
        )
    )

    compositions = appier.field(
        type = appier.references(
            "Composition",
            name = "id"
        )
    )

    live_movel = appier.field(
        type = appier.references(
            "LiveModel",
            name = "id"
        )
    )

    @classmethod
    def validate(cls):
        return super(Product, cls).validate() + [
            appier.not_null("short_description"),
            appier.not_empty("short_description"),

            appier.not_null("gender"),
            appier.not_empty("gender"),

            appier.not_null("price"),
            appier.gt("price", 0.0)
        ]

    @classmethod
    def list_names(cls):
        return ["id", "short_description", "gender", "tag"]
