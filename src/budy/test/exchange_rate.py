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

class ExchangeRateTest(unittest.TestCase):

    def setUp(self):
        self.app = budy.BudyApp(level = logging.ERROR)

    def tearDown(self):
        self.app.unload()
        adapter = appier.get_adapter()
        adapter.drop_db()

    def test_basic(self):
        exchange_rate = budy.ExchangeRate(
            base = "EUR",
            target = "USD",
            rate = 1.138
        )
        exchange_rate.save()

        result = budy.ExchangeRate.convert(10.0, "EUR", "USD")

        self.assertEqual(result, commons.Decimal(11.38))

    def test_both(self):
        budy.ExchangeRate.create_both_s("EUR", "USD", 1.138)

        result = budy.ExchangeRate.convert(10.0, "EUR", "USD")

        self.assertEqual(result, commons.Decimal(11.38))

        result = budy.ExchangeRate.convert(10.0, "USD", "EUR")

        self.assertEqual(result, commons.Decimal(8.78735))
