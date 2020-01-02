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

import budy

from . import root

class ProductAPIController(root.RootAPIController):

    @appier.route("/api/products", "GET", json = True)
    def list(self):
        object = appier.get_object(alias = True, find = True)
        products = budy.Product.find_e(
            find_t = "right",
            eager = ("images", "brand"),
            map = True,
            **object
        )
        return products

    @appier.route("/api/products/<int:id>", "GET", json = True)
    def show(self, id):
        product = budy.Product.get_e(
            id = id,
            eager = ("images", "brand", "measurements"),
            map = True
        )
        return product

    @appier.route("/api/products/search", "GET", json = True)
    def search(self):
        object = appier.get_object(alias = True, find = True)
        products = budy.Product.find_se(
            find_t = "both",
            find_n = "tokens",
            eager = ("images", "brand"),
            map = True,
            **object
        )
        return products

    @appier.route("/api/products/<int:id>/related", "GET", json = True)
    def related(self, id):
        limit = self.field("limit", 10, cast = int)
        available = self.field("available", True, cast = bool)
        product = budy.Product.get_e(id = id)
        products = product.related(
            limit = limit,
            available = available,
            enabled = True
        )
        return products

    @appier.route("/api/products/<int:id>/share", "GET", json = True)
    def share(self, id):
        email = self.field("email", mandatory = True, not_empty = True)
        sender = self.field("sender", mandatory = True, not_empty = True)
        product = budy.Product.get_e(id = id)
        share = product.share(email = email, sender = sender)
        return share

    @appier.route("/api/products/simple.csv", "GET")
    @appier.ensure(token = "admin")
    def simple_csv(self):
        object = appier.get_object(
            alias = True,
            find = True,
            limit = 0
        )
        products = budy.Product.find_e(
            eager = (
                "colors",
                "categories",
                "collections",
                "variants",
                "brand",
                "season",
                "measurements",
                "compositions"
            ),
            **object
        )

        products_s = [(
            "description",
            "short_description",
            "product_id",
            "gender",
            "price",
            "order",
            "tag",
            "tag_description",
            "farfetch_url",
            "farfetch_male_url",
            "farfetch_female_url",
            "colors",
            "categories",
            "collections",
            "variants",
            "brand",
            "season",
            "measurements",
            "compositions",
            "price_provider",
            "price_url"
        )]
        for product in products:
            product_s = (
                product.description,
                product.short_description,
                product.product_id,
                product.gender,
                product.price,
                product.order,
                product.tag,
                product.tag_description,
                product.farfetch_url,
                product.farfetch_male_url,
                product.farfetch_female_url,
                ";".join([color.name for color in product.colors]),
                ";".join([category.name for category in product.categories]),
                ";".join([collection.name for collection in product.collections]),
                ";".join([variant.product_id for variant in product.variants]),
                product.brand.name if product.brand else None,
                product.season.name if product.season else None,
                ";".join([measurement.name for measurement in product.measurements]),
                ";".join([composition.name for composition in product.compositions]),
                product.price_provider,
                product.price_url
            )
            products_s.append(product_s)

        result = appier.serialize_csv(products_s, delimiter = ",")
        self.content_type("text/csv")
        return result
