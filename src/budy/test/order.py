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

import logging
import unittest

import appier

import budy

class OrderTest(unittest.TestCase):

    def setUp(self):
        budy.BudyApp(level = logging.ERROR)

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

        order = budy.Order.new(form = False)
        order.save()

        self.assertEqual(type(order.key), appier.legacy.UNICODE)
        self.assertEqual(type(order.total), float)
        self.assertEqual(len(order.lines), 0)
        self.assertEqual(order.currency, None)
        self.assertEqual(order.total >= 0.0, True)
        self.assertEqual(order.paid, False)
        self.assertEqual(order.date, None)
        self.assertEqual(order.notification_sent, False)

        self.assertRaises(appier.AssertionError, order.mark_paid_s)

        order = order.reload()

        self.assertEqual(type(order.key), appier.legacy.UNICODE)
        self.assertEqual(type(order.total), float)
        self.assertEqual(len(order.lines), 0)
        self.assertEqual(len(order.reference), 9)
        self.assertEqual(order.currency, None)
        self.assertEqual(order.total >= 0.0, True)
        self.assertEqual(order.status, "created")
        self.assertEqual(order.paid, False)
        self.assertEqual(order.date, None)
        self.assertEqual(order.notification_sent, False)
        self.assertEqual(order.reference.startswith("BD-"), True)

        self.assertRaises(appier.AssertionError, order.mark_paid_s)

        order_line = budy.OrderLine.new(
            quantity = 2.0,
            form = False
        )
        order_line.product = product
        order_line.save()
        order.add_line_s(order_line)

        self.assertEqual(order_line.quantity, 2.0)
        self.assertEqual(order_line.total, 20.0)
        self.assertEqual(order.total, 20.0)
        self.assertEqual(len(order.lines), 1)

        self.assertRaises(appier.AssertionError, order.mark_paid_s)

        address = budy.Address.new(
            first_name = "first name",
            last_name = "last name",
            address = "address",
            city = "city",
            form = False
        )
        address.save()

        order.billing_address = address
        order.save()

        order.mark_paid_s()

        self.assertEqual(order.status, "paid")
        self.assertEqual(order.paid, True)

        self.assertRaises(appier.AssertionError, order.mark_paid_s)
