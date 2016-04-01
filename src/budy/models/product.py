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

import json

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

    tag_description = appier.field()

    price_provider = appier.field(
        index = True
    )

    price_url = appier.field(
        index = True,
        meta = "url"
    )

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

    collections = appier.field(
        type = appier.references(
            "Collection",
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
        parameters = (
            ("CSV File", "file", "file"),
            ("Empty source", "empty", bool, True)
        )
    )
    def import_csv_s(cls, file, empty):

        def callback(line):
            from . import color
            from . import brand
            from . import season
            from . import category
            from . import collection
            from . import composition
            from . import measurement

            description,\
            short_description,\
            product_id,\
            gender,\
            price,\
            order,\
            tag,\
            tag_description,\
            farfetch_url,\
            farfetch_male_url,\
            farfetch_female_url,\
            colors,\
            categories,\
            collections, \
            variants,\
            _brand,\
            _season,\
            measurements,\
            compositions, \
            price_provider, \
            price_url = line

            product_id = product_id or None
            price = float(price) if price else None
            order = int(order) if order else None
            tag = tag or None
            tag_description = tag_description or None
            farfetch_url = farfetch_url or None
            farfetch_male_url = farfetch_male_url or None
            farfetch_female_url = farfetch_female_url or None
            price_provider = price_provider or None
            price_url = price_url or None

            colors = colors.split(";") if colors else []
            colors = color.Color.find(name = {"$in" : colors})

            categories = categories.split(";") if categories else []
            categories = category.Category.find(name = {"$in" : categories})

            collections = collections.split(";") if collections else []
            collections = collection.Collection.find(name = {"$in" : collections})

            variants = variants.split(";") if variants else []
            variants = Product.find(product_id = {"$in" : variants})

            _brand = brand.Brand.find(name = _brand) if _brand else None
            _season = season.Season.find(name = _season) if _season else None

            measurements = measurements.split(";") if measurements else []
            measurements = measurement.Measurement.find(name = {"$in" : measurements})

            compositions = compositions.split(";") if compositions else []
            compositions = composition.Composition.find(name = {"$in" : compositions})

            product = Product(
                description = description,
                short_description = short_description,
                product_id = product_id,
                gender = gender,
                price = price,
                order = order,
                tag = tag,
                tag_description = tag_description,
                farfetch_url = farfetch_url,
                farfetch_male_url = farfetch_male_url,
                farfetch_female_url = farfetch_female_url,
                colors = colors,
                categories = categories,
                collections = collections,
                variants = variants,
                brand = _brand,
                season = _season,
                measurements = measurements,
                compositions = compositions,
                price_provider = price_provider,
                price_url = price_url
            )
            product.save()

        if empty: Product.delete_c()
        cls._csv_import(file, callback)

    @classmethod
    @appier.link(name = "Export Simple")
    def simple_csv_url(cls, absolute = False):
        return appier.get_app().url_for(
            "product_api.simple_csv",
            absolute = absolute
        )

    @appier.operation(
        name = "Apply Collection",
        parameters = (
            ("Collection", "collection", str),
        )
    )
    def apply_collection_s(self, collection):
        from . import collection as _collection
        collection = _collection.Collection.get(name = collection)
        self.collections.append(collection)
        self.save()

    def get_price(
        self,
        currency = None,
        country = None,
        attributes = None
    ):
        if not self.price_provider: return self.price
        method = getattr(self, "get_price_%s" % self.price_provider)
        return method(
            currency = currency,
            country = country,
            attributes = attributes
        )

    def get_price_ripe(
        self,
        currency = None,
        country = None,
        attributes = None
    ):
        if not self.price_url: return self.price
        attributes_m = json.loads(attributes)
        p = []
        parts = attributes_m.get("parts", {})
        embossing = attributes_m.get("embossing", None)
        letters = attributes_m.get("letters", None)

        for key, value in appier.legacy.iteritems(parts):
            material = value["material"]
            color = value["color"]
            triplet = "%s:%s:%s" % (key, material, color)
            p.append(triplet)

        params = dict(
            product_id = self.product_id,
            p = p
        )
        if currency: params["currency"] = currency
        if country: params["country"] = country
        if embossing: params["embossing"] = embossing
        if letters: params["letters"] = letters

        result = appier.get(
            self.price_url,
            params = params
        )
        total = result["total"]
        return total["price_final"]

    def get_size(self, currency = None, country = None, attributes = None):
        if not self.price_provider: return None, None
        method = getattr(self, "get_size_%s" % self.price_provider)
        return method(
            country = country,
            attributes = attributes
        )

    def get_size_ripe(
        self,
        currency = None,
        country = None,
        attributes = None
    ):
        attributes_m = json.loads(attributes)
        size = attributes_m["size"]
        scale = attributes_m["scale"]
        gender = attributes_m["gender"]

        if gender == "male": converter = lambda native: ((native - 17) / 2) + 36
        else: converter = lambda native: ((native - 17) / 2) + 34

        return converter(size), scale
