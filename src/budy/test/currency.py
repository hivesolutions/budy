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

import commons
import logging
import unittest

import appier

import budy


class CurrencyTest(unittest.TestCase):
    def setUp(self):
        self.app = budy.BudyApp(level=logging.ERROR)

    def tearDown(self):
        self.app.unload()
        adapter = appier.get_adapter()
        adapter.drop_db()

    def test_basic(self):
        budy.Currency.create_s("EUR", 2)
        budy.Currency.create_s("USD", 2)

        result = budy.Currency.round(12.45678, "EUR")

        self.assertEqual(result, 12.46)
        self.assertEqual(result, commons.Decimal(12.46))

        result = budy.Currency.round(12.45678, "EUR", rounder=commons.floor)

        self.assertEqual(result, 12.45)
        self.assertEqual(result, commons.Decimal(12.45))

        result = budy.Currency.round(12.45678, "EUR", rounder=commons.ceil)

        self.assertEqual(result, 12.46)
        self.assertEqual(result, commons.Decimal(12.46))

        result = budy.Currency.round(12.45578, "EUR")

        self.assertEqual(result, 12.46)
        self.assertEqual(result, commons.Decimal(12.46))

        result = budy.Currency.round(12.45478, "EUR")

        self.assertEqual(result, 12.45)
        self.assertEqual(result, commons.Decimal(12.45))

        result = budy.Currency.round(12.45478, "EUR", rounder=commons.floor)

        self.assertEqual(result, 12.45)
        self.assertEqual(result, commons.Decimal(12.45))

        result = budy.Currency.round(12.45478, "EUR", rounder=commons.ceil)

        self.assertEqual(result, 12.46)
        self.assertEqual(result, commons.Decimal(12.46))

    def test_format(self):
        budy.Currency.create_s("EUR", 2)
        budy.Currency.create_s("USD", 2)
        budy.Currency.create_s("JPY", 0)

        result = budy.Currency.format(1200.2, "EUR")
        self.assertEqual(result, "1200.20")

        result = budy.Currency.format(1200.238, "EUR")
        self.assertEqual(result, "1200.24")

        result = budy.Currency.format(1200.2, "USD")
        self.assertEqual(result, "1200.20")

        result = budy.Currency.format(1200.238, "USD")
        self.assertEqual(result, "1200.24")

        result = budy.Currency.format(1200.2, "JPY")
        self.assertEqual(result, "1200")

        result = budy.Currency.format(1200.238, "JPY")
        self.assertEqual(result, "1200")
