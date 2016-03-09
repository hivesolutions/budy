#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2016 Hive Solutions Lda.
#
# This file is part of Hive Appier Framework.
#
# Hive Appier Framework is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Appier Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Appier Framework. If not, see <http://www.apache.org/licenses/>.

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

import unittest

import appier

import budy

class BagTest(unittest.TestCase):

    def setUp(self):
        budy.BudyApp()

    def tearDown(self):
        adapter = appier.get_adapter()
        adapter.drop_db()

    def test_basic(self):
        product = budy.Product.new(
            short_description = "product",
            gender = "Male",
            price = 10.0,
            form = False
        )
        product.save()

        self.assertEqual(product.short_description, "product")
        self.assertEqual(product.gender, "Male")
        self.assertEqual(product.price, 10.0)

        bag = budy.Bag.new(form = False)
        bag.save()

        self.assertEqual(type(bag.key), appier.legacy.UNICODE)
        self.assertEqual(type(bag.currency), appier.legacy.UNICODE)
        self.assertEqual(type(bag.total), float)
        self.assertEqual(len(bag.lines), 0)
        self.assertEqual(bag.currency, "EUR")
        self.assertEqual(bag.total >= 0.0, True)

        bag_line = budy.BagLine.new(
            quantity = 2.0,
            form = False
        )
        bag_line.product = product
        bag_line.save()
        bag.add_line_s(bag_line)

        self.assertEqual(bag_line.quantity, 2.0)
        self.assertEqual(bag_line.total, 20.0)
        self.assertEqual(bag.total, 20.0)
        self.assertEqual(len(bag.lines), 1)

        bag.add_product_s(product, 3.0)

        self.assertEqual(bag.total, 50.0)
        self.assertEqual(len(bag.lines), 1)

        product_expensive = budy.Product.new(
            short_description = "product_expensive",
            gender = "Female",
            price = 100.0,
            form = False
        )
        product_expensive.save()

        self.assertEqual(product_expensive.short_description, "product_expensive")
        self.assertEqual(product_expensive.gender, "Female")
        self.assertEqual(product_expensive.price, 100.0)

        bag.add_product_s(product_expensive, 1.0)

        self.assertEqual(bag.total, 150.0)
        self.assertEqual(len(bag.lines), 2)

        bag.empty_s()

        self.assertEqual(bag.total, 0.0)
        self.assertEqual(len(bag.lines), 0)
