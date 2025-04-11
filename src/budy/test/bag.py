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


class BagTest(unittest.TestCase):
    def setUp(self):
        self.app = budy.BudyApp(level=logging.ERROR)

    def tearDown(self):
        self.app.unload()
        adapter = appier.get_adapter()
        adapter.drop_db()

    def test_basic(self):
        product = budy.Product(short_description="product", gender="Male", price=10.0)
        product.save()

        self.assertEqual(product.short_description, "product")
        self.assertEqual(product.gender, "Male")
        self.assertEqual(product.price, 10.0)

        bag = budy.Bag()
        bag.save()

        self.assertEqual(type(bag.key), appier.legacy.UNICODE)
        self.assertEqual(type(bag.total), commons.Decimal)
        self.assertEqual(len(bag.lines), 0)
        self.assertEqual(bag.currency, None)
        self.assertEqual(bag.total >= 0.0, True)

        bag_line = budy.BagLine(quantity=2.0)
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

        product_expensive = budy.Product(
            short_description="product_expensive", gender="Female", price=100.0
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

    def test_remove_line(self):
        product = budy.Product(short_description="product", gender="Male", price=10.0)
        product.save()

        bag = budy.Bag()
        bag.save()

        bag_line = budy.BagLine(quantity=2.0)
        bag_line.product = product
        bag_line.save()
        bag.add_line_s(bag_line)

        self.assertEqual(bag_line.quantity, 2.0)
        self.assertEqual(bag_line.total, 20.0)
        self.assertEqual(bag.total, 20.0)
        self.assertEqual(len(bag.lines), 1)

        bag.remove_line_s(bag_line.id)

        self.assertEqual(len(bag.lines), 0)

        bag = bag.reload()

        self.assertEqual(len(bag.lines), 0)

    def test_empty_line(self):
        product = budy.Product(short_description="product", gender="Male", price=10.0)
        product.save()

        bag = budy.Bag()
        bag.save()

        bag_line = budy.BagLine(quantity=2.0)
        bag_line.product = product
        bag_line.save()
        bag.add_line_s(bag_line)

        self.assertEqual(bag_line.quantity, 2.0)
        self.assertEqual(bag_line.total, 20.0)
        self.assertEqual(bag.total, 20.0)
        self.assertEqual(len(bag.lines), 1)

        bag_line.quantity = 0.0
        bag_line.save()

        bag = bag.reload()
        bag.collect_empty()

        self.assertEqual(len(bag.lines), 0)

        bag = bag.reload()

        self.assertEqual(len(bag.lines), 1)

        bag = bag.reload()
        bag.save()

        self.assertEqual(len(bag.lines), 0)

        bag = bag.reload()

        self.assertEqual(len(bag.lines), 0)

    def test_merge(self):
        product = budy.Product(short_description="product", gender="Male", price=10.0)
        product.save()

        bag = budy.Bag()
        bag.save()

        bag_line = budy.BagLine(quantity=2.0)
        bag_line.product = product
        bag_line.save()
        bag.add_line_s(bag_line)

        self.assertEqual(bag_line.quantity, 2.0)
        self.assertEqual(bag_line.total, 20.0)
        self.assertEqual(bag.total, 20.0)
        self.assertEqual(len(bag.lines), 1)

        bag = bag.reload()

        self.assertEqual(bag.total, 20.0)
        self.assertEqual(len(bag.lines), 1)

        extra = budy.Bag()
        extra.save()

        self.assertEqual(len(extra.lines), 0)

        extra.merge_s(bag.id)

        self.assertEqual(extra.total, 20.0)
        self.assertEqual(len(extra.lines), 1)

        extra.merge_s(bag.id)

        self.assertEqual(extra.total, 20.0)
        self.assertEqual(len(extra.lines), 1)

        extra.merge_s(bag.id, increment=True)

        self.assertEqual(extra.total, 40.0)
        self.assertEqual(len(extra.lines), 1)

    def test_order(self):
        product = budy.Product(short_description="product", gender="Male", price=10.0)
        product.save()

        bag = budy.Bag()
        bag.save()

        bag_line = budy.BagLine(quantity=2.0)
        bag_line.product = product
        bag_line.save()
        bag.add_line_s(bag_line)

        self.assertEqual(bag_line.quantity, 2.0)
        self.assertEqual(bag_line.total, 20.0)
        self.assertEqual(bag_line.discounted, False)
        self.assertEqual(bag.sub_total, 20.0)
        self.assertEqual(bag.discounted_sub_total, 0.0)
        self.assertEqual(bag.undiscounted_sub_total, 20.0)
        self.assertEqual(bag.total, 20.0)
        self.assertEqual(bag.discountable, 20.0)
        self.assertEqual(len(bag.lines), 1)

        order = bag.to_order_s()

        self.assertEqual(order.currency, bag.currency)
        self.assertEqual(order.sub_total, 20.0)
        self.assertEqual(order.discounted_sub_total, 0.0)
        self.assertEqual(order.undiscounted_sub_total, 20.0)
        self.assertEqual(order.total, 20.0)
        self.assertEqual(order.discountable, 20.0)
        self.assertEqual(len(order.lines), 1)

        bag.empty_s()

        self.assertRaises(appier.AssertionError, bag.to_order_s)

        result = budy.Order.count()

        self.assertEqual(result, 1)

    def test_duplicate(self):
        bag = budy.Bag()
        bag.save()

        self.assertNotEqual(bag.key, None)
        self.assertEqual(type(bag.key), appier.legacy.UNICODE)

        duplicated = budy.Bag()
        duplicated.key = bag.key

        self.assertRaises(appier.ValidationError, duplicated.save)

    def test_price_change(self):
        product = budy.Product(short_description="product", gender="Male", price=10.0)
        product.save()

        bag = budy.Bag()
        bag.save()

        bag_line = budy.BagLine(quantity=2.0)
        bag_line.product = product
        bag_line.save()
        bag.add_line_s(bag_line)

        self.assertEqual(bag_line.quantity, 2.0)
        self.assertEqual(bag_line.total, 20.0)
        self.assertEqual(bag.total, 20.0)
        self.assertEqual(len(bag.lines), 1)

        product.price = 20.0
        product.save()

        bag = bag.reload()
        bag.save()

        bag_line = bag_line.reload()

        self.assertEqual(bag_line.quantity, 2.0)
        self.assertEqual(bag_line.total, 40.0)
        self.assertEqual(bag.total, 40.0)
        self.assertEqual(len(bag.lines), 1)

    def test_quantity_change(self):
        product = budy.Product(
            short_description="product", gender="Male", price=10.0, quantity_hand=2.0
        )
        product.save()

        bag = budy.Bag()
        bag.save()

        bag_line = budy.BagLine(quantity=2.0)
        bag_line.product = product
        bag_line.save()
        bag.add_line_s(bag_line)

        self.assertEqual(bag_line.quantity, 2.0)
        self.assertEqual(bag_line.total, 20.0)
        self.assertEqual(bag.total, 20.0)
        self.assertEqual(len(bag.lines), 1)

        product.quantity_hand = 1.0
        product.save()

        bag = bag.reload()
        bag.save()

        bag_line = bag_line.reload()

        self.assertEqual(bag_line.quantity, 1.0)
        self.assertEqual(bag_line.total, 10.0)
        self.assertEqual(bag.total, 10.0)
        self.assertEqual(len(bag.lines), 1)

        product.quantity_hand = 0.0
        product.save()

        bag = bag.reload()
        bag.save()

        self.assertEqual(len(bag.lines), 0)

    def test_quantity_multiple_lines(self):
        product = budy.Product(
            short_description="product", gender="Male", price=10.0, quantity_hand=3.0
        )
        product.save()

        bag = budy.Bag()
        bag.save()

        bag_line_red = budy.BagLine(quantity=2.0)
        bag_line_red.product = product
        bag_line_red.attributes = '{"color": "red"}'
        bag_line_red.save()
        bag.add_line_s(bag_line_red)

        bag_line_yellow = budy.BagLine(quantity=1.0)
        bag_line_yellow.product = product
        bag_line_yellow.attributes = '{"color": "yellow"}'
        bag_line_yellow.save()
        bag.add_line_s(bag_line_yellow)

        bag = bag.reload()
        bag_line_red = bag_line_red.reload()
        bag_line_yellow = bag_line_yellow.reload()

        self.assertEqual(bag_line_red.quantity, 2.0)
        self.assertEqual(bag_line_red.total, 20.0)
        self.assertEqual(bag_line_red.attributes, '{"color": "red"}')
        self.assertEqual(bag_line_yellow.quantity, 1.0)
        self.assertEqual(bag_line_yellow.total, 10.0)
        self.assertEqual(bag_line_yellow.attributes, '{"color": "yellow"}')
        self.assertEqual(bag.total, 30.0)
        self.assertEqual(len(bag.lines), 2)
        self.assertEqual(bag.lines[0].attributes, '{"color": "red"}')
        self.assertEqual(bag.lines[0].quantity, 2.0)
        self.assertEqual(bag.lines[1].attributes, '{"color": "yellow"}')
        self.assertEqual(bag.lines[1].quantity, 1.0)

        bag = bag.reload()
        bag.save()

        bag.add_product_s(product, quantity=1.0, attributes='{"color": "yellow"}')

        bag = bag.reload()
        bag_line_red = bag_line_red.reload()
        bag_line_yellow = bag_line_yellow.reload()

        self.assertEqual(bag_line_red.quantity, 2.0)
        self.assertEqual(bag_line_red.total, 20.0)
        self.assertEqual(bag_line_red.attributes, '{"color": "red"}')
        self.assertEqual(bag_line_yellow.quantity, 1.0)
        self.assertEqual(bag_line_yellow.total, 10.0)
        self.assertEqual(bag_line_yellow.attributes, '{"color": "yellow"}')
        self.assertEqual(bag.total, 30.0)
        self.assertEqual(len(bag.lines), 2)
        self.assertEqual(bag.lines[0].attributes, '{"color": "red"}')
        self.assertEqual(bag.lines[0].quantity, 2.0)
        self.assertEqual(bag.lines[1].attributes, '{"color": "yellow"}')
        self.assertEqual(bag.lines[1].quantity, 1.0)

        product.quantity_hand = 4.0
        product.save()

        bag = bag.reload()
        bag.save()

        bag = bag.reload()
        bag_line_red = bag_line_red.reload()
        bag_line_yellow = bag_line_yellow.reload()

        self.assertEqual(bag_line_red.quantity, 2.0)
        self.assertEqual(bag_line_red.total, 20.0)
        self.assertEqual(bag_line_red.attributes, '{"color": "red"}')
        self.assertEqual(bag_line_yellow.quantity, 1.0)
        self.assertEqual(bag_line_yellow.total, 10.0)
        self.assertEqual(bag_line_yellow.attributes, '{"color": "yellow"}')
        self.assertEqual(bag.total, 30.0)
        self.assertEqual(len(bag.lines), 2)
        self.assertEqual(bag.lines[0].attributes, '{"color": "red"}')
        self.assertEqual(bag.lines[0].quantity, 2.0)
        self.assertEqual(bag.lines[1].attributes, '{"color": "yellow"}')
        self.assertEqual(bag.lines[1].quantity, 1.0)

        bag.add_product_s(product, quantity=1.0, attributes='{"color": "yellow"}')

        bag = bag.reload()
        bag_line_red = bag_line_red.reload()
        bag_line_yellow = bag_line_yellow.reload()

        self.assertEqual(bag_line_red.quantity, 2.0)
        self.assertEqual(bag_line_red.total, 20.0)
        self.assertEqual(bag_line_yellow.quantity, 2.0)
        self.assertEqual(bag_line_yellow.total, 20.0)
        self.assertEqual(bag.total, 40.0)
        self.assertEqual(len(bag.lines), 2)
        self.assertEqual(bag.lines[0].attributes, '{"color": "red"}')
        self.assertEqual(bag.lines[0].quantity, 2.0)
        self.assertEqual(bag.lines[1].attributes, '{"color": "yellow"}')
        self.assertEqual(bag.lines[1].quantity, 2.0)

        product.quantity_hand = 0.0
        product.save()

        bag = bag.reload()
        bag.save()

        self.assertEqual(len(bag.lines), 0)

    def test_product_discounted(self):
        product = budy.Product(
            short_description="product",
            gender="Male",
            price=10.0,
            price_compare=12.0,
            quantity_hand=2.0,
        )
        product.save()

        bag = budy.Bag()
        bag.save()

        bag_line = budy.BagLine(quantity=2.0)
        bag_line.product = product
        bag_line.save()
        bag.add_line_s(bag_line)

        self.assertEqual(bag_line.quantity, 2.0)
        self.assertEqual(bag_line.total, 20.0)
        self.assertEqual(bag_line.discounted, True)
        self.assertEqual(bag.sub_total, 20.0)
        self.assertEqual(bag.discounted_sub_total, 20.0)
        self.assertEqual(bag.undiscounted_sub_total, 0.0)
        self.assertEqual(bag.total, 20.0)
        self.assertEqual(bag.discountable, 0.0)
        self.assertEqual(len(bag.lines), 1)

    def test_product_non_discountable(self):
        product = budy.Product(
            short_description="product",
            gender="Male",
            price=10.0,
            quantity_hand=2.0,
            discountable=False,
        )
        product.save()

        bag = budy.Bag()
        bag.save()

        bag_line = budy.BagLine(quantity=2.0)
        bag_line.product = product
        bag_line.save()
        bag.add_line_s(bag_line)

        self.assertEqual(bag_line.quantity, 2.0)
        self.assertEqual(bag_line.total, 20.0)
        self.assertEqual(bag_line.discounted, False)
        self.assertEqual(bag.sub_total, 20.0)
        self.assertEqual(bag.discounted_sub_total, 0.0)
        self.assertEqual(bag.undiscounted_sub_total, 20.0)
        self.assertEqual(bag.discountable_sub_total, 0.0)
        self.assertEqual(bag.total, 20.0)
        self.assertEqual(bag.discountable, 0.0)
        self.assertEqual(len(bag.lines), 1)
