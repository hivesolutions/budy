#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Budy
# Copyright (c) 2008-2015 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2015 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
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

    order = appier.field(
        type = int,
        index = True
    )

    tag = appier.field()

    tag_descritpion = appier.field()

    farfetch_url = appier.field(
        index = True,
        meta = "url"
    )

    farfetch_male_url = appier.field(
        index = True,
        meta = "url"
    )

    farfetch_female_url = appier.field(
        index = True,
        meta = "url"
    )

    colors = appier.field(
        type = appier.references(
            "Color",
            name = "id"
        )
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
        return ["id", "product_id", "short_description", "enabled", "gender", "tag"]

    @classmethod
    @appier.operation(
        name = "Import CSV",
        parameters = (("CSV File", "file", "file"),)
    )
    def import_csv_s(cls, file):

        def callback(line):
            from . import color
            from . import brand
            from . import season
            from . import category
            from . import composition
            from . import measurement

            short_description,\
            product_id,\
            gender,\
            price,\
            order,\
            tag,\
            tag_descritpion,\
            farfetch_url,\
            farfetch_male_url,\
            farfetch_female_url,\
            colors,\
            categories,\
            variants,\
            _brand,\
            _season,\
            measurements,\
            compositions = line

            product_id = product_id or None
            price = float(price) if price else None
            order = int(order) if order else None
            tag = tag or None
            tag_descritpion = tag_descritpion or None
            farfetch_url = farfetch_url or None
            farfetch_male_url = farfetch_male_url or None
            farfetch_female_url = farfetch_female_url or None

            colors = colors.split(";") if colors else []
            colors = color.Color.find(name = {"$in" : colors})

            categories = categories.split(";") if categories else []
            categories = category.Category.find(name = {"$in" : categories})

            variants = variants.split(";") if variants else []
            variants = Product.find(product_id = {"$in" : variants})

            _brand = brand.Brand.find(name = _brand) if _brand else None
            _season = season.Season.find(name = _season) if _season else None

            measurements = measurements.split(";") if measurements else []
            measurements = measurement.Measurement.find(name = {"$in" : measurements})

            compositions = compositions.split(";") if compositions else []
            compositions = composition.Composition.find(name = {"$in" : compositions})

            product = Product(
                short_description = short_description,
                product_id = product_id,
                gender = gender,
                price = price,
                order = order,
                tag = tag,
                tag_descritpion = tag_descritpion,
                farfetch_url = farfetch_url,
                farfetch_male_url = farfetch_male_url,
                farfetch_female_url = farfetch_female_url,
                colors = colors,
                categories = categories,
                variants = variants,
                brand = _brand,
                season = _season,
                measurements = measurements,
                compositions = compositions
            )
            product.save()

        cls._csv_import(file, callback)
