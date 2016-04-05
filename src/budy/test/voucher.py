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

import time
import commons
import logging
import unittest

import appier

import budy

class VoucherTest(unittest.TestCase):

    def setUp(self):
        self.app = budy.BudyApp(level = logging.ERROR)

    def tearDown(self):
        self.app.unload()
        adapter = appier.get_adapter()
        adapter.drop_db()

    def test_basic(self):
        voucher = budy.Voucher(amount = 200.0)
        voucher.save()

        self.assertEqual(voucher.used, False)
        self.assertEqual(voucher.amount, 200.0)
        self.assertEqual(voucher.used_amount, 0.0)
        self.assertEqual(voucher.usage_count, 0)
        self.assertEqual(voucher.is_valid(), True)
        self.assertEqual(type(voucher.key), appier.legacy.UNICODE)
        self.assertNotEqual(voucher.key, None)

        voucher.use_s(100.0)

        self.assertEqual(voucher.is_valid(), True)
        self.assertEqual(voucher.is_valid(amount = 100.0), True)
        self.assertEqual(voucher.is_valid(amount = 200.0), False)
        self.assertEqual(voucher.used, False)
        self.assertEqual(voucher.amount, 200.0)
        self.assertEqual(voucher.open_amount, 100.0)
        self.assertEqual(voucher.used_amount, 100.0)
        self.assertEqual(voucher.usage_count, 1)
        self.assertEqual(isinstance(voucher.amount, commons.Decimal), True)
        self.assertEqual(isinstance(voucher.open_amount, commons.Decimal), True)

        voucher.use_s(100.0)

        self.assertEqual(voucher.is_valid(), False)
        self.assertEqual(voucher.used, True)
        self.assertEqual(voucher.amount, 200.0)
        self.assertEqual(voucher.open_amount, 0.0)
        self.assertEqual(voucher.used_amount, 200.0)
        self.assertEqual(voucher.usage_count, 2)

        self.assertRaises(
            appier.AssertionError,
            lambda: voucher.use_s(100.0, currency = "EUR")
        )

        budy.Currency.create_s("EUR", 2)
        budy.Currency.create_s("USD", 2)
        budy.ExchangeRate.create_both_s("EUR", "USD", 1.135)

        voucher = budy.Voucher(amount = 200.0, currency = "EUR")
        voucher.use_s(100.0, currency = "EUR")

        self.assertEqual(voucher.is_valid(), True)
        self.assertEqual(voucher.used, False)
        self.assertEqual(voucher.amount, 200.0)
        self.assertEqual(voucher.currency, "EUR")
        self.assertEqual(voucher.open_amount, 100.0)
        self.assertEqual(voucher.used_amount, 100.0)
        self.assertEqual(voucher.usage_count, 1)

        voucher.use_s(100.0, currency = "USD")

        self.assertEqual(voucher.is_valid(), True)
        self.assertEqual(voucher.used, False)
        self.assertEqual(voucher.amount, 200.0)
        self.assertEqual(voucher.currency, "EUR")
        self.assertEqual(voucher.open_amount, 11.90)
        self.assertEqual(voucher.used_amount, 188.10)
        self.assertEqual(voucher.usage_count, 2)

    def test_single(self):
        voucher = budy.Voucher(amount = 200.0, usage_limit = 1)
        voucher.save()

        voucher.use_s(100.0)

        self.assertEqual(voucher.is_valid(), False)
        self.assertEqual(voucher.is_valid(amount = 100.0), False)
        self.assertEqual(voucher.is_valid(amount = 200.0), False)
        self.assertEqual(voucher.used, True)
        self.assertEqual(voucher.amount, 200.0)
        self.assertEqual(voucher.open_amount, 100.0)
        self.assertEqual(voucher.used_amount, 100.0)
        self.assertEqual(voucher.usage_count, 1)
        self.assertEqual(isinstance(voucher.amount, commons.Decimal), True)
        self.assertEqual(isinstance(voucher.open_amount, commons.Decimal), True)

        self.assertRaises(
            appier.AssertionError,
            lambda: voucher.use_s(100.0)
        )

    def test_expired(self):
        voucher = budy.Voucher(amount = 200.0, expiration = time.time() + 3600)
        voucher.save()

        voucher.use_s(100.0)

        self.assertEqual(voucher.is_valid(), True)
        self.assertEqual(voucher.is_valid(amount = 100.0), True)
        self.assertEqual(voucher.is_valid(amount = 200.0), False)
        self.assertEqual(voucher.used, False)
        self.assertEqual(voucher.amount, 200.0)
        self.assertEqual(voucher.open_amount, 100.0)
        self.assertEqual(voucher.used_amount, 100.0)
        self.assertEqual(voucher.usage_count, 1)
        self.assertEqual(isinstance(voucher.amount, commons.Decimal), True)
        self.assertEqual(isinstance(voucher.open_amount, commons.Decimal), True)

        voucher = budy.Voucher(amount = 200.0, expiration = time.time() - 60)
        voucher.save()

        self.assertRaises(
            appier.AssertionError,
            lambda: voucher.use_s(100.0)
        )
