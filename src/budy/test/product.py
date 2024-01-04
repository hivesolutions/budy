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

import logging
import unittest

import appier

import budy


class ProductTest(unittest.TestCase):
    def setUp(self):
        self.app = budy.BudyApp(level=logging.ERROR)

    def tearDown(self):
        self.app.unload()
        adapter = appier.get_adapter()
        adapter.drop_db()

    def test_add_remove_images(self):
        file = appier.typesf.ImageFile(dict(name="name", data="data", mime="mime"))

        media_1 = budy.Media(
            description="description", label="label", order=1, file=file
        )
        media_1.save()

        media_2 = budy.Media(
            description="description", label="label", order=1, file=file
        )
        media_2.save()

        product = budy.Product(short_description="product", gender="Male", price=10.0)
        product.save()

        self.assertEqual(len(product.images), 0)

        product.add_image_s(media_1)

        self.assertEqual(len(product.images), 1)
        self.assertEqual(product.images[0].id, media_1.id)

        product.add_image_s(media_1)

        self.assertEqual(len(product.images), 1)
        self.assertEqual(product.images[0].id, media_1.id)

        product.add_image_s(media_2)

        self.assertEqual(len(product.images), 2)
        self.assertEqual(product.images[0].id, media_1.id)
        self.assertEqual(product.images[1].id, media_2.id)

        product = product.reload()

        self.assertEqual(len(product.images), 2)
        self.assertEqual(product.images[0].id, media_1.id)
        self.assertEqual(product.images[1].id, media_2.id)

        product.remove_image_s(media_1)

        self.assertEqual(len(product.images), 1)
        self.assertEqual(product.images[0].id, media_2.id)

        product.remove_image_s(media_1)

        self.assertEqual(len(product.images), 1)
        self.assertEqual(product.images[0].id, media_2.id)

        product.remove_image_s(media_2)

        self.assertEqual(len(product.images), 0)

        product = product.reload()

        self.assertEqual(len(product.images), 0)

    def test_measurements(self):
        product = budy.Product(
            short_description="product", gender="Male", price=10.0, quantity_hand=None
        )
        product.save()

        measurement = budy.Measurement(
            name="size",
            value=12,
            value_s="12",
            price=None,
            quantity_hand=2.0,
            product=product,
        )
        measurement.save()

        self.assertEqual(product.quantity_hand, None)
        self.assertEqual(measurement.product.id, 1)
        self.assertEqual(measurement.product.id, product.id)

        product.measurements.append(measurement)
        product.save()

        self.assertEqual(product.quantity_hand, 2.0)
        self.assertEqual(len(product.measurements), 1)

        measurement = measurement.reload()

        self.assertEqual(measurement.product.id, 1)
        self.assertEqual(measurement.product.id, product.id)
        self.assertEqual(len(measurement.product.measurements), 1)

        result = product.get_measurement(12, name="size")

        self.assertEqual(result.id, 1)
        self.assertEqual(result.name, "size")
        self.assertEqual(result.value, 12)
        self.assertEqual(result.value_s, "12")
        self.assertEqual(result.price, None)
        self.assertEqual(result.quantity_hand, 2.0)
        self.assertEqual(result.product.id, 1)
        self.assertEqual(result.product.short_description, "product")
        self.assertEqual(result.product.quantity_hand, 2.0)
        self.assertEqual(len(result.product.measurements), 1)

        measurement.delete()

        product = product.reload()

        self.assertEqual(len(product.measurements), 0)

    def test_labels(self):
        product = budy.Product(
            short_description="product", gender="Male", price=10.0, quantity_hand=None
        )
        product.save()

        collection = budy.Collection(name="collection", new_in=True)
        collection.save()

        self.assertEqual(product.labels, [])
        self.assertEqual(len(product.collections), 0)
        self.assertEqual(collection.new_in, True)
        self.assertEqual(collection.labels, ["new_in"])

        product.add_collection_s(collection)

        self.assertEqual(product.labels, ["new_in"])
        self.assertEqual(len(product.collections), 1)
        self.assertEqual(product.collections[0].id, collection.id)

        product.save()

        self.assertEqual(product.labels, ["new_in"])
        self.assertEqual(len(product.collections), 1)
        self.assertEqual(product.collections[0].id, collection.id)

        collection.labels.append("extra")
        collection.save()

        self.assertEqual(product.labels, ["new_in"])
        self.assertEqual(len(product.collections), 1)
        self.assertEqual(product.collections[0].id, collection.id)
        self.assertEqual(collection.new_in, True)
        self.assertEqual(collection.labels, ["new_in", "extra"])

        product = product.reload()
        product.save()

        self.assertEqual(product.labels, ["new_in", "extra"])
        self.assertEqual(len(product.collections), 1)
        self.assertEqual(product.collections[0].id, collection.id)

        collection.labels.remove("extra")
        collection.save()

        product = product.reload()
        product.save()

        self.assertEqual(product.labels, ["new_in"])
        self.assertEqual(len(product.collections), 1)
        self.assertEqual(product.collections[0].id, collection.id)

        collection.exclusive = True
        collection.save()

        self.assertEqual(product.labels, ["new_in"])
        self.assertEqual(len(product.collections), 1)
        self.assertEqual(product.collections[0].id, collection.id)
        self.assertEqual(collection.new_in, True)
        self.assertEqual(collection.exclusive, True)
        self.assertEqual(collection.labels, ["new_in", "exclusive"])

        product = product.reload()
        product.save()

        self.assertEqual(product.labels, ["new_in", "exclusive"])
        self.assertEqual(len(product.collections), 1)
        self.assertEqual(product.collections[0].id, collection.id)

    def test_discount(self):
        product = budy.Product(
            short_description="product", gender="Male", price=10.0, quantity_hand=None
        )
        product.save()

        self.assertEqual(product.price, 10.0)
        self.assertEqual(product.price_compare, 0.0)
        self.assertEqual(product.discount, 0.0)
        self.assertEqual(product.discount_percent, 0.0)
        self.assertEqual(product.is_discounted, False)

        product.price_compare = 16.0
        product.save()

        product = product.reload()

        self.assertEqual(product.price, 10.0)
        self.assertEqual(product.price_compare, 16.0)
        self.assertEqual(product.discount, 6.0)
        self.assertEqual(product.discount_percent, 37.5)
        self.assertEqual(product.is_discounted, True)

        product.price_compare = 20.0
        product.save()

        product = product.reload()

        self.assertEqual(product.price, 10.0)
        self.assertEqual(product.price_compare, 20.0)
        self.assertEqual(product.discount, 10.0)
        self.assertEqual(product.discount_percent, 50.0)
        self.assertEqual(product.is_discounted, True)
