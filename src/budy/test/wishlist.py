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

import commons
import logging
import unittest

import appier

import budy

class WishlistTest(unittest.TestCase):

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
            price = 10.0
        )
        product.save()

        self.assertEqual(product.short_description, "product")
        self.assertEqual(product.gender, "Male")
        self.assertEqual(product.price, 10.0)

        wishlist = budy.Wishlist()
        wishlist.save()

        self.assertEqual(type(wishlist.key), appier.legacy.UNICODE)
        self.assertEqual(type(wishlist.total), commons.Decimal)
        self.assertEqual(len(wishlist.lines), 0)
        self.assertEqual(wishlist.currency, None)
        self.assertEqual(wishlist.total >= 0.0, True)

        wishlist_line = budy.WishlistLine(
            quantity = 2.0
        )
        wishlist_line.product = product
        wishlist_line.save()
        wishlist.add_line_s(wishlist_line)

        self.assertEqual(wishlist_line.quantity, 2.0)
        self.assertEqual(wishlist_line.total, 20.0)
        self.assertEqual(wishlist.total, 20.0)
        self.assertEqual(len(wishlist.lines), 1)

        wishlist.add_product_s(product, 3.0)

        self.assertEqual(wishlist.total, 50.0)
        self.assertEqual(len(wishlist.lines), 1)

        product_expensive = budy.Product(
            short_description = "product_expensive",
            gender = "Female",
            price = 100.0
        )
        product_expensive.save()

        self.assertEqual(product_expensive.short_description, "product_expensive")
        self.assertEqual(product_expensive.gender, "Female")
        self.assertEqual(product_expensive.price, 100.0)

        wishlist.add_product_s(product_expensive, 1.0)

        self.assertEqual(wishlist.total, 150.0)
        self.assertEqual(len(wishlist.lines), 2)

        wishlist.empty_s()

        self.assertEqual(wishlist.total, 0.0)
        self.assertEqual(len(wishlist.lines), 0)
