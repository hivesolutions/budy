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

import commons
import logging
import unittest

import appier

import budy

class OrderTest(unittest.TestCase):

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

        order = budy.Order()
        order.save()

        self.assertEqual(type(order.key), appier.legacy.UNICODE)
        self.assertEqual(type(order.total), commons.Decimal)
        self.assertEqual(len(order.lines), 0)
        self.assertEqual(order.currency, None)
        self.assertEqual(order.total >= 0.0, True)
        self.assertEqual(order.paid, False)
        self.assertEqual(order.date, None)
        self.assertEqual(order.notification_sent, False)

        self.assertRaises(appier.AssertionError, order.mark_paid_s)

        order = order.reload()

        self.assertEqual(type(order.key), appier.legacy.UNICODE)
        self.assertEqual(type(order.total), commons.Decimal)
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

        order_line = budy.OrderLine(quantity = 2.0)
        order_line.product = product
        order_line.save()
        order.add_line_s(order_line)

        self.assertEqual(order_line.quantity, 2.0)
        self.assertEqual(order_line.total, 20.0)
        self.assertEqual(order.total, 20.0)
        self.assertEqual(len(order.lines), 1)

        self.assertRaises(appier.AssertionError, order.mark_paid_s)

        address = budy.Address(
            first_name = "first name",
            last_name = "last name",
            address = "address",
            city = "city"
        )
        address.save()

        order.billing_address = address
        order.email = "username@email.com"
        order.save()

        order.mark_paid_s()

        self.assertEqual(order.status, "paid")
        self.assertEqual(order.paid, True)

        self.assertRaises(appier.AssertionError, order.mark_paid_s)

    def test_referral(self):
        order = budy.Order()
        order.save()

        referral = budy.Referral(name = "name")
        referral.save()

        order.set_referral_s(referral)

        self.assertEqual(len(order.referrals), 1)
        self.assertEqual(order.referrals[0].name, "name")

    def test_voucher(self):
        product = budy.Product(
            short_description = "product",
            gender = "Male",
            price = 10.0
        )
        product.save()

        order = budy.Order()
        order.save()

        order_line = budy.OrderLine(quantity = 2.0)
        order_line.product = product
        order_line.save()
        order.add_line_s(order_line)

        self.assertEqual(order_line.quantity, 2.0)
        self.assertEqual(order_line.total, 20.0)
        self.assertEqual(order.total, 20.0)
        self.assertEqual(len(order.lines), 1)

        address = budy.Address(
            first_name = "first name",
            last_name = "last name",
            address = "address",
            city = "city"
        )
        address.save()

        order.billing_address = address
        order.email = "username@email.com"
        order.save()

        voucher = budy.Voucher(amount = 5.0)
        voucher.save()

        order.add_voucher_s(voucher)

        self.assertEqual(order.sub_total, 20.0)
        self.assertEqual(order.discount, 5.0)
        self.assertEqual(order.total, 15.0)
        self.assertEqual(order.payable, 15.0)
        self.assertEqual(isinstance(order.sub_total, commons.Decimal), True)
        self.assertEqual(isinstance(order.discount, commons.Decimal), True)
        self.assertEqual(isinstance(order.total, commons.Decimal), True)
        self.assertEqual(isinstance(order.payable, commons.Decimal), True)

        order.use_vouchers_s()
        voucher = voucher.reload()

        self.assertEqual(voucher.is_valid(), False)
        self.assertEqual(voucher.used_amount, 5.0)
        self.assertEqual(voucher.open_amount, 0.0)
        self.assertEqual(voucher.usage_count, 1)

        order.unmark_paid_s()

        small_voucher = budy.Voucher(amount = 1.0)
        small_voucher.save()

        order.set_voucher_s(small_voucher)

        self.assertEqual(order.sub_total, 20.0)
        self.assertEqual(order.discount, 1.0)
        self.assertEqual(order.total, 19.0)
        self.assertEqual(order.payable, 19.0)
        self.assertEqual(isinstance(order.sub_total, commons.Decimal), True)
        self.assertEqual(isinstance(order.discount, commons.Decimal), True)
        self.assertEqual(isinstance(order.total, commons.Decimal), True)
        self.assertEqual(isinstance(order.payable, commons.Decimal), True)

        large_voucher = budy.Voucher(amount = 100.0)
        large_voucher.save()

        order.set_voucher_s(large_voucher)

        self.assertEqual(order.sub_total, 20.0)
        self.assertEqual(order.discount, 20.0)
        self.assertEqual(order.total, 0.0)
        self.assertEqual(order.payable, 0.0)

        order.use_vouchers_s()
        voucher = large_voucher.reload()

        self.assertEqual(voucher.is_valid(), True)
        self.assertEqual(voucher.used_amount, 20.0)
        self.assertEqual(voucher.open_amount, 80.0)
        self.assertEqual(voucher.usage_count, 1)

        order.unmark_paid_s()

        percent_voucher = budy.Voucher(percentage = 10.0)
        percent_voucher.save()

        order.set_voucher_s(percent_voucher)

        self.assertEqual(order.sub_total, 20.0)
        self.assertEqual(order.discount, 2.0)
        self.assertEqual(order.total, 18.0)
        self.assertEqual(order.payable, 18.0)

        order.use_vouchers_s()
        voucher = percent_voucher.reload()

        self.assertEqual(voucher.is_valid(), True)
        self.assertEqual(voucher.percentage, 10.0)
        self.assertEqual(voucher.used_amount, 0.0)
        self.assertEqual(voucher.open_amount, 0.0)
        self.assertEqual(voucher.usage_count, 1)
