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

import logging
import unittest

import appier

import budy

class MeasurementTest(unittest.TestCase):

    def setUp(self):
        self.app = budy.BudyApp(level = logging.ERROR)

    def tearDown(self):
        self.app.unload()
        adapter = appier.get_adapter()
        adapter.drop_db()

    def test_basic(self):
        product = budy.Product(
            short_description = "product",
            gender = "Male",
            price = 10.0,
            quantity_hand = None
        )
        product.save()

        measurement = budy.Measurement(
            product = product,
            name = "measurement",
            value = 1,
            value_s = "1"
        )
        measurement.save()

        measurement = measurement.reload()

        self.assertEqual(measurement.product.id, product.id)
        self.assertEqual(measurement.name, "measurement")
        self.assertEqual(measurement.value, 1)
        self.assertEqual(measurement.value_s, "1")

    def test_discount(self):
        product = budy.Product(
            short_description = "product",
            gender = "Male",
            price = 10.0,
            quantity_hand = None
        )
        product.save()

        measurement = budy.Measurement(
            product = product,
            name = "measurement",
            value = 1,
            value_s = "1",
            price = 10.0
        )
        measurement.save()

        self.assertEqual(measurement.price, 10.0)
        self.assertEqual(measurement.price_compare, 0.0)
        self.assertEqual(measurement.discount, 0.0)
        self.assertEqual(measurement.discount_percent, 0.0)
        self.assertEqual(measurement.is_discounted, False)

        measurement.price_compare = 16.0
        measurement.save()

        measurement = measurement.reload()

        self.assertEqual(measurement.price, 10.0)
        self.assertEqual(measurement.price_compare, 16.0)
        self.assertEqual(measurement.discount, 6.0)
        self.assertEqual(measurement.discount_percent, 37.5)
        self.assertEqual(measurement.is_discounted, True)

        measurement.price_compare = 20.0
        measurement.save()

        measurement = measurement.reload()

        self.assertEqual(measurement.price, 10.0)
        self.assertEqual(measurement.price_compare, 20.0)
        self.assertEqual(measurement.discount, 10.0)
        self.assertEqual(measurement.discount_percent, 50.0)
        self.assertEqual(measurement.is_discounted, True)

    def test__fix_value_s(self):
        product = budy.Product(
            short_description = "product",
            gender = "Male",
            price = 10.0,
            quantity_hand = None
        )
        product.save()

        measurement = budy.Measurement(
            product = product,
            name = "measurement",
            value = 2,
            value_s = "2"
        )
        measurement.save()

        self.assertEqual(measurement.product.id, product.id)
        self.assertEqual(measurement.name, "measurement")
        self.assertEqual(measurement.value, 2)
        self.assertEqual(measurement.value_s, "2")

        measurement.value = "a"
        measurement._fix_value_s()

        self.assertEqual(measurement.product.id, product.id)
        self.assertEqual(measurement.name, "measurement")
        self.assertEqual(measurement.value, 97)
        self.assertEqual(measurement.value_s, "2")

        measurement.value = "b"
        measurement._fix_value_s()

        self.assertEqual(measurement.product.id, product.id)
        self.assertEqual(measurement.name, "measurement")
        self.assertEqual(measurement.value, 98)
        self.assertEqual(measurement.value_s, "2")

        measurement.value = "abc"
        measurement._fix_value_s()

        self.assertEqual(measurement.product.id, product.id)
        self.assertEqual(measurement.name, "measurement")
        self.assertEqual(measurement.value, 6513249)
        self.assertEqual(measurement.value_s, "2")

        measurement.value = "abcabcabcabcabc"
        measurement._fix_value_s()

        self.assertEqual(measurement.product.id, product.id)
        self.assertEqual(measurement.name, "measurement")
        self.assertEqual(measurement.value, 7089056562649719393)
        self.assertEqual(measurement.value_s, "2")
