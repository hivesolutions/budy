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

import json
import commons
import logging
import unittest

import appier

import budy


class OrderTest(unittest.TestCase):
    def setUp(self):
        self.app = budy.BudyApp(level=logging.ERROR)

    def tearDown(self):
        self.app.unload()
        adapter = appier.get_adapter()
        adapter.drop_db()

    def test_basic(self):
        product = budy.Product(
            short_description="product", gender="Male", price=10.0, quantity_hand=5.0
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
        self.assertEqual(order.id, 1)
        self.assertEqual(order.reference, "BD-000001")
        self.assertEqual(order.currency, None)
        self.assertEqual(order.total >= 0.0, True)
        self.assertEqual(order.paid, False)
        self.assertEqual(order.inventory_decremented, False)
        self.assertEqual(order.date, None)
        self.assertEqual(order.notifications, [])

        self.assertRaises(appier.AssertionError, order.verify_base)
        self.assertRaises(appier.AssertionError, order.verify_shippable)
        self.assertRaises(appier.AssertionError, order.mark_paid_s)

        order = order.reload()

        self.assertEqual(type(order.key), appier.legacy.UNICODE)
        self.assertEqual(type(order.total), commons.Decimal)
        self.assertEqual(len(order.lines), 0)
        self.assertEqual(len(order.reference), 9)
        self.assertEqual(order.id, 1)
        self.assertEqual(order.reference, "BD-000001")
        self.assertEqual(order.currency, None)
        self.assertEqual(order.total >= 0.0, True)
        self.assertEqual(order.status, "created")
        self.assertEqual(order.paid, False)
        self.assertEqual(order.date, None)
        self.assertEqual(order.notifications, [])
        self.assertEqual(order.reference.startswith("BD-"), True)

        self.assertRaises(appier.AssertionError, order.verify_base)
        self.assertRaises(appier.AssertionError, order.verify_shippable)
        self.assertRaises(appier.AssertionError, order.mark_paid_s)

        order_line = budy.OrderLine(quantity=2.0)
        order_line.product = product
        order_line.save()
        order.add_line_s(order_line)
        order.verify_base()

        self.assertEqual(order_line.quantity, 2.0)
        self.assertEqual(order_line.total, 20.0)
        self.assertEqual(order.total, 20.0)
        self.assertEqual(len(order.lines), 1)

        self.assertRaises(appier.AssertionError, order.verify_shippable)
        self.assertRaises(appier.AssertionError, order.mark_paid_s)

        address = budy.Address(
            first_name="first name",
            last_name="last name",
            address="address",
            city="city",
        )
        address.save()

        order.shipping_address = address
        order.billing_address = address
        order.email = "username@email.com"
        order.save()

        order.mark_waiting_payment_s()

        self.assertEqual(order.status, "waiting_payment")
        self.assertEqual(order.paid, False)
        self.assertEqual(order.inventory_decremented, False)

        order.mark_paid_s()

        self.assertEqual(order.status, "paid")
        self.assertEqual(order.paid, True)
        self.assertEqual(order.inventory_decremented, True)

        product = product.reload()

        self.assertEqual(product.quantity_hand, 3)

        self.assertRaises(appier.AssertionError, order.mark_paid_s)

    def test_referral(self):
        order = budy.Order()
        order.save()

        referral = budy.Referral(name="name")
        referral.save()

        order.set_referral_s(referral)

        self.assertEqual(len(order.referrals), 1)
        self.assertEqual(order.referrals[0].name, "name")

    def test_store(self):
        product = budy.Product(short_description="product", gender="Male", price=10.0)
        product.save()

        order = budy.Order()
        order.save()

        order_line = budy.OrderLine(quantity=2.0)
        order_line.product = product
        order_line.save()
        order.add_line_s(order_line)

        self.assertEqual(order.currency, None)
        self.assertEqual(order.payment_currency, None)

        order.refresh_s(
            currency=order.payment_currency or order.currency,
            country=order.shipping_country or order.country,
        )

        self.assertEqual(order.currency, None)
        self.assertEqual(order.payment_currency, None)

        store = budy.Store(name="store", currency_code="GBP")
        store.save()

        account = budy.BudyAccount(
            username="account",
            email="account@account.com",
            password="password",
            password_confirm="password",
            store=store,
        )
        account.save()

        order.set_account_s(account)

        self.assertEqual(order.account.username, "account")
        self.assertEqual(order.store.name, "store")
        self.assertEqual(order.currency, None)
        self.assertEqual(order.payment_currency, "GBP")

        order.refresh_s(
            currency=order.payment_currency or order.currency,
            country=order.shipping_country or order.country,
        )

        self.assertEqual(order.currency, "GBP")
        self.assertEqual(order.payment_currency, "GBP")

        self.assertRaises(appier.AssertionError, order.verify_store)

        address = budy.Address(
            first_name="first name",
            last_name="last name",
            address="address",
            city="city",
        )
        address.save()
        store.address = address
        store.save()

        order = order.reload()

        order.verify_store()

    def test_voucher(self):
        product = budy.Product(short_description="product", gender="Male", price=10.0)
        product.save()

        order = budy.Order()
        order.save()

        order_line = budy.OrderLine(quantity=2.0)
        order_line.product = product
        order_line.save()
        order.add_line_s(order_line)

        self.assertEqual(order_line.quantity, 2.0)
        self.assertEqual(order_line.total, 20.0)
        self.assertEqual(order.total, 20.0)
        self.assertEqual(len(order.lines), 1)

        address = budy.Address(
            first_name="first name",
            last_name="last name",
            address="address",
            city="city",
        )
        address.save()

        order.shipping_address = address
        order.billing_address = address
        order.email = "username@email.com"
        order.save()

        voucher = budy.Voucher(amount=5.0)
        voucher.save()

        order.add_voucher_s(voucher)

        self.assertEqual(order.sub_total, 20.0)
        self.assertEqual(order.discount, 5.0)
        self.assertEqual(order.total, 15.0)
        self.assertEqual(order.payable, 15.0)
        self.assertEqual(order.discountable, 20.0)
        self.assertEqual(isinstance(order.sub_total, commons.Decimal), True)
        self.assertEqual(isinstance(order.discount, commons.Decimal), True)
        self.assertEqual(isinstance(order.total, commons.Decimal), True)
        self.assertEqual(isinstance(order.payable, commons.Decimal), True)
        self.assertEqual(isinstance(order.discountable, commons.Decimal), True)

        order.use_vouchers_s()
        order.verify_vouchers()
        voucher = voucher.reload()

        self.assertEqual(voucher.is_valid(), False)
        self.assertEqual(voucher.used_amount, 5.0)
        self.assertEqual(voucher.open_amount, 0.0)
        self.assertEqual(voucher.usage_count, 1)

        small_voucher = budy.Voucher(amount=1.0)
        small_voucher.save()

        order.set_voucher_s(small_voucher)

        self.assertEqual(order.sub_total, 20.0)
        self.assertEqual(order.discount, 1.0)
        self.assertEqual(order.total, 19.0)
        self.assertEqual(order.payable, 19.0)
        self.assertEqual(order.discountable, 20.0)
        self.assertEqual(isinstance(order.sub_total, commons.Decimal), True)
        self.assertEqual(isinstance(order.discount, commons.Decimal), True)
        self.assertEqual(isinstance(order.total, commons.Decimal), True)
        self.assertEqual(isinstance(order.payable, commons.Decimal), True)

        large_voucher = budy.Voucher(amount=100.0)
        large_voucher.save()

        order.set_voucher_s(large_voucher)

        self.assertEqual(order.sub_total, 20.0)
        self.assertEqual(order.discount, 20.0)
        self.assertEqual(order.total, 0.0)
        self.assertEqual(order.payable, 0.0)
        self.assertEqual(order.discountable, 20.0)

        order.use_vouchers_s()
        order.verify_vouchers()
        voucher = large_voucher.reload()

        self.assertEqual(voucher.is_valid(), True)
        self.assertEqual(voucher.used_amount, 20.0)
        self.assertEqual(voucher.open_amount, 80.0)
        self.assertEqual(voucher.usage_count, 1)

        order.unmark_paid_s()

        percent_voucher = budy.Voucher(percentage=10.0)
        percent_voucher.save()

        order.set_voucher_s(percent_voucher)

        self.assertEqual(order.sub_total, 20.0)
        self.assertEqual(order.discount, 2.0)
        self.assertEqual(order.total, 18.0)
        self.assertEqual(order.payable, 18.0)
        self.assertEqual(order.discountable, 20.0)

        order.use_vouchers_s()
        order.verify_vouchers()
        voucher = percent_voucher.reload()

        self.assertEqual(voucher.is_valid(), True)
        self.assertEqual(voucher.percentage, 10.0)
        self.assertEqual(voucher.used_amount, 0.0)
        self.assertEqual(voucher.open_amount, 0.0)
        self.assertEqual(voucher.usage_count, 1)

    def test_duplicate_pay(self):
        product = budy.Product(short_description="product", gender="Male", price=10.0)
        product.save()

        order = budy.Order()
        order.save()

        order_line = budy.OrderLine(quantity=2.0)
        order_line.product = product
        order_line.save()
        order.add_line_s(order_line)

        self.assertEqual(order_line.quantity, 2.0)
        self.assertEqual(order_line.total, 20.0)
        self.assertEqual(order.total, 20.0)
        self.assertEqual(len(order.lines), 1)

        address = budy.Address(
            first_name="first name",
            last_name="last name",
            address="address",
            city="city",
        )
        address.save()

        order.shipping_address = address
        order.billing_address = address
        order.email = "username@email.com"
        order.save()

        def _pay_dummy(payment_data):
            order.payment_data = dict(method="dummy")
            return False

        order.pay_s(payment_data=dict(type="simple"), payment_function=_pay_dummy)

        self.assertEqual(order.is_valid(), True)
        self.assertEqual(order_line.is_valid_quantity(), True)
        self.assertEqual(order.paid, False)
        self.assertEqual(order.inventory_decremented, False)
        self.assertEqual(order.status, "waiting_payment")

        self.assertRaises(
            appier.SecurityError,
            lambda: order.pay_s(
                payment_data=dict(type="simple"), payment_function=_pay_dummy
            ),
        )

    def test_voucher_use(self):
        product = budy.Product(
            short_description="product", gender="Male", price=10.0, quantity_hand=5.0
        )
        product.save()

        order = budy.Order()
        order.save()

        order_line = budy.OrderLine(quantity=2.0)
        order_line.product = product
        order_line.save()
        order.add_line_s(order_line)

        self.assertEqual(order_line.quantity, 2.0)
        self.assertEqual(order_line.total, 20.0)
        self.assertEqual(order.total, 20.0)
        self.assertEqual(len(order.lines), 1)

        address = budy.Address(
            first_name="first name",
            last_name="last name",
            address="address",
            city="city",
        )
        address.save()

        order.shipping_address = address
        order.billing_address = address
        order.email = "username@email.com"
        order.save()

        voucher = budy.Voucher(amount=1.0)
        voucher.save()

        order.set_voucher_s(voucher)

        order.pay_s(payment_data=dict(type="simple"), strict=False)

        self.assertEqual(voucher.is_valid(), False)
        self.assertEqual(voucher.amount, 1.0)
        self.assertEqual(voucher.used_amount, 1.0)
        self.assertEqual(voucher.open_amount, 0.0)
        self.assertEqual(voucher.usage_count, 1)

        self.assertEqual(order.is_valid(), True)
        self.assertEqual(order_line.is_valid_quantity(), True)
        self.assertEqual(order.paid, False)
        self.assertEqual(order.inventory_decremented, False)
        self.assertEqual(order.status, "waiting_payment")

        order.end_pay_s(payment_data=dict(type="simple"), strict=False)

        self.assertEqual(voucher.is_valid(), False)
        self.assertEqual(voucher.amount, 1.0)
        self.assertEqual(voucher.used_amount, 1.0)
        self.assertEqual(voucher.open_amount, 0.0)
        self.assertEqual(voucher.usage_count, 1)

        self.assertEqual(order.is_valid(), True)
        self.assertEqual(order_line.is_valid_quantity(), True)
        self.assertEqual(order.paid, True)
        self.assertEqual(order.status, "paid")
        self.assertEqual(order.inventory_decremented, True)

        product = product.reload()

        self.assertEqual(product.quantity_hand, 3.0)

        order.date = None
        order.status = "created"
        order.unmark_paid_s()

        voucher = budy.Voucher(amount=1.0)
        voucher.save()

        order.set_voucher_s(voucher)

        order.pay_s(payment_data=dict(type="simple"), strict=False)

        self.assertEqual(voucher.is_valid(), False)
        self.assertEqual(voucher.amount, 1.0)
        self.assertEqual(voucher.used_amount, 1.0)
        self.assertEqual(voucher.open_amount, 0.0)
        self.assertEqual(voucher.usage_count, 1)

        self.assertEqual(order.is_valid(), True)
        self.assertEqual(order_line.is_valid_quantity(), True)
        self.assertEqual(order.paid, False)
        self.assertEqual(order.inventory_decremented, False)
        self.assertEqual(order.status, "waiting_payment")

        order.cancel_s()

        voucher = voucher.reload()

        self.assertEqual(voucher.is_valid(), True)
        self.assertEqual(voucher.amount, 1.0)
        self.assertEqual(voucher.used_amount, 0.0)
        self.assertEqual(voucher.open_amount, 1.0)
        self.assertEqual(voucher.usage_count, 0)

        self.assertEqual(order.is_valid(), True)
        self.assertEqual(order_line.is_valid_quantity(), True)
        self.assertEqual(order.paid, False)
        self.assertEqual(order.inventory_decremented, False)
        self.assertEqual(order.status, "canceled")

        order.date = None
        order.status = "created"
        order.unmark_paid_s()

        voucher = budy.Voucher(amount=1.0)
        voucher.save()

        order.set_voucher_s(voucher)

        order.pay_s(payment_data=dict(type="simple"), strict=False)

        order.end_pay_s(payment_data=dict(type="simple"), strict=False)

        self.assertEqual(voucher.is_valid(), False)
        self.assertEqual(voucher.amount, 1.0)
        self.assertEqual(voucher.used_amount, 1.0)
        self.assertEqual(voucher.open_amount, 0.0)
        self.assertEqual(voucher.usage_count, 1)

        self.assertEqual(order.is_valid(), True)
        self.assertEqual(order_line.is_valid_quantity(), True)
        self.assertEqual(order.paid, True)
        self.assertEqual(order.inventory_decremented, True)
        self.assertEqual(order.status, "paid")

        product = product.reload()

        self.assertEqual(product.quantity_hand, 3.0)

        order.cancel_s()

        voucher = voucher.reload()

        self.assertEqual(voucher.is_valid(), False)
        self.assertEqual(voucher.amount, 1.0)
        self.assertEqual(voucher.used_amount, 1.0)
        self.assertEqual(voucher.open_amount, 0.0)
        self.assertEqual(voucher.usage_count, 1)

        self.assertEqual(order.is_valid(), True)
        self.assertEqual(order_line.is_valid_quantity(), True)
        self.assertEqual(order.paid, True)
        self.assertEqual(order.inventory_decremented, True)
        self.assertEqual(order.status, "canceled")

    def test_discount(self):
        product = budy.Product(short_description="product", gender="Male", price=10.0)
        product.save()

        order = budy.Order()
        order.save()

        order_line = budy.OrderLine(quantity=2.0)
        order_line.product = product
        order_line.save()
        order.add_line_s(order_line)

        self.assertEqual(order.sub_total, 20.0)
        self.assertEqual(order.discount, 0.0)
        self.assertEqual(order.total, 20.0)
        self.assertEqual(order.payable, 20.0)
        self.assertEqual(order.discountable, 20.0)

        order.discount_fixed = 20.0
        order.save()

        self.assertEqual(order.sub_total, 20.0)
        self.assertEqual(order.discount, 20.0)
        self.assertEqual(order.total, 0.0)
        self.assertEqual(order.payable, 0.0)
        self.assertEqual(order.discountable, 20.0)

        voucher = budy.Voucher(amount=5.0)
        voucher.save()

        order.discount_fixed = 18.0
        order.set_voucher_s(voucher)
        order.use_vouchers_s()
        order.verify_vouchers()

        self.assertEqual(order.sub_total, 20.0)
        self.assertEqual(order.discount, 20.0)
        self.assertEqual(order.total, 0.0)
        self.assertEqual(order.payable, 0.0)
        self.assertEqual(order.discountable, 20.0)

        voucher = voucher.reload()

        self.assertEqual(voucher.is_valid(), True)
        self.assertEqual(voucher.used_amount, 2.0)
        self.assertEqual(voucher.open_amount, 3.0)
        self.assertEqual(voucher.usage_count, 1)

    def test_discountable_full(self):
        product = budy.Product(short_description="product", gender="Male", price=10.0)
        product.save()

        order = budy.Order(discountable_full=True, shipping_fixed=10.0)
        order.save()

        order_line = budy.OrderLine(quantity=2.0)
        order_line.product = product
        order_line.save()
        order.add_line_s(order_line)

        self.assertEqual(order.sub_total, 20.0)
        self.assertEqual(order.discount, 0.0)
        self.assertEqual(order.total, 30.0)
        self.assertEqual(order.payable, 30.0)
        self.assertEqual(order.shipping_cost, 10.0)
        self.assertEqual(order.discountable, 30.0)

        order.discount_fixed = 20.0
        order.save()

        self.assertEqual(order.sub_total, 20.0)
        self.assertEqual(order.discount, 20.0)
        self.assertEqual(order.total, 10.0)
        self.assertEqual(order.payable, 10.0)
        self.assertEqual(order.shipping_cost, 10.0)
        self.assertEqual(order.discountable, 30.0)

        order.discount_fixed = 30.0
        order.save()

        self.assertEqual(order.sub_total, 20.0)
        self.assertEqual(order.discount, 30.0)
        self.assertEqual(order.total, 0.0)
        self.assertEqual(order.payable, 0.0)
        self.assertEqual(order.shipping_cost, 10.0)
        self.assertEqual(order.discountable, 30.0)

        order.discountable_full = False
        order.save()

        self.assertEqual(order.sub_total, 20.0)
        self.assertEqual(order.discount, 20.0)
        self.assertEqual(order.total, 10.0)
        self.assertEqual(order.payable, 10.0)
        self.assertEqual(order.shipping_cost, 10.0)
        self.assertEqual(order.discountable, 20.0)

        product = budy.Product(
            short_description="product", gender="Male", price=10.0, price_compare=12.0
        )
        product.save()

        order = budy.Order(discountable_full=True, shipping_fixed=10.0)
        order.save()

        order_line = budy.OrderLine(quantity=2.0)
        order_line.product = product
        order_line.save()
        order.add_line_s(order_line)

        self.assertEqual(order.sub_total, 20.0)
        self.assertEqual(order.discount, 0.0)
        self.assertEqual(order.total, 30.0)
        self.assertEqual(order.payable, 30.0)
        self.assertEqual(order.shipping_cost, 10.0)
        self.assertEqual(order.discountable, 30.0)

        order.discount_fixed = 20.0
        order.save()

        self.assertEqual(order.sub_total, 20.0)
        self.assertEqual(order.discount, 20.0)
        self.assertEqual(order.total, 10.0)
        self.assertEqual(order.payable, 10.0)
        self.assertEqual(order.shipping_cost, 10.0)
        self.assertEqual(order.discountable, 30.0)

        order.discount_fixed = 30.0
        order.save()

        self.assertEqual(order.sub_total, 20.0)
        self.assertEqual(order.discount, 30.0)
        self.assertEqual(order.total, 0.0)
        self.assertEqual(order.payable, 0.0)
        self.assertEqual(order.shipping_cost, 10.0)
        self.assertEqual(order.discountable, 30.0)

        order.discountable_full = False
        order.save()

        self.assertEqual(order.sub_total, 20.0)
        self.assertEqual(order.discount, 0.0)
        self.assertEqual(order.total, 30.0)
        self.assertEqual(order.payable, 30.0)
        self.assertEqual(order.shipping_cost, 10.0)
        self.assertEqual(order.discountable, 0.0)

    def test_non_discountable(self):
        product = budy.Product(
            short_description="product", gender="Male", price=10.0, discountable=False
        )
        product.save()

        order = budy.Order(shipping_fixed=10.0)
        order.save()

        order_line = budy.OrderLine(quantity=2.0)
        order_line.product = product
        order_line.save()
        order.add_line_s(order_line)

        self.assertEqual(order.sub_total, 20.0)
        self.assertEqual(order.discount, 0.0)
        self.assertEqual(order.total, 30.0)
        self.assertEqual(order.payable, 30.0)
        self.assertEqual(order.shipping_cost, 10.0)
        self.assertEqual(order.discountable, 0.0)

        order.discount_fixed = 20.0
        order.save()

        self.assertEqual(order.sub_total, 20.0)
        self.assertEqual(order.discount, 0.0)
        self.assertEqual(order.total, 30.0)
        self.assertEqual(order.payable, 30.0)
        self.assertEqual(order.shipping_cost, 10.0)
        self.assertEqual(order.discountable, 0.0)

    def test_taxes(self):
        product = budy.Product(
            short_description="product", gender="Male", price=10.0, taxes=3.0
        )
        product.save()

        order = budy.Order()
        order.save()

        order_line = budy.OrderLine(quantity=2.0)
        order_line.product = product
        order_line.save()
        order.add_line_s(order_line)

        self.assertEqual(order.sub_total, 20.0)
        self.assertEqual(order.discount, 0.0)
        self.assertEqual(order.total, 20.0)
        self.assertEqual(order.taxes, 6.0)
        self.assertEqual(order.payable, 20.0)
        self.assertEqual(order.discountable, 20.0)

    def test_quantity(self):
        product = budy.Product(
            short_description="product", gender="Male", price=10.0, quantity_hand=1.0
        )
        product.save()

        order = budy.Order()
        order.save()

        order_line = budy.OrderLine(quantity=2.0)
        order_line.product = product

        self.assertRaises(appier.AssertionError, order_line.save)

        product.quantity_hand = 2.0
        product.save()

        order_line.save()
        order.add_line_s(order_line)

        self.assertEqual(order.is_open(), True)
        self.assertEqual(order.is_valid(), True)
        self.assertEqual(order_line.is_valid_quantity(), True)

        product.quantity_hand = 1.0
        product.save()

        self.assertEqual(order.is_open(), True)
        self.assertEqual(order.is_valid(), False)
        self.assertEqual(order_line.is_valid_quantity(), False)
        self.assertRaises(appier.AssertionError, order.save)
        self.assertRaises(appier.AssertionError, order.mark_waiting_payment_s)

        product.quantity_hand = None
        product.save()

        self.assertEqual(order.is_open(), True)
        self.assertEqual(order.is_valid(), True)
        self.assertEqual(order_line.is_valid_quantity(), True)

        product.quantity_hand = 1.0
        product.save()

        order.paid = True

        self.assertEqual(order.is_open(), False)
        self.assertEqual(order.is_valid(), True)
        self.assertEqual(order_line.is_valid_quantity(), False)

        order.paid = False

        product.quantity_hand = 2.0
        product.save()

        address = budy.Address(
            first_name="first name",
            last_name="last name",
            address="address",
            city="city",
        )
        address.save()

        order.shipping_address = address
        order.billing_address = address
        order.email = "username@email.com"
        order.save()

        order.save()
        order.mark_waiting_payment_s()
        order.mark_paid_s()

        self.assertEqual(order.is_valid(), True)
        self.assertEqual(order_line.is_valid_quantity(), True)
        self.assertEqual(order.paid, True)
        self.assertEqual(order.status, "paid")

        product.quantity_hand = 0.0
        product.save()

        order.save()

        self.assertEqual(order.is_valid(), True)
        self.assertEqual(order_line.is_valid_quantity(), True)
        self.assertEqual(order.paid, True)
        self.assertEqual(order.status, "paid")

    def test_measurements(self):
        product = budy.Product(
            short_description="product", gender="Male", price=10.0, quantity_hand=None
        )
        product.save()

        measurement = budy.Measurement(
            name="size",
            value=12,
            value_s="12",
            price=12.0,
            quantity_hand=None,
            product=product,
        )
        measurement.save()

        product.measurements.append(measurement)
        product.save()

        order = budy.Order()
        order.save()

        order_line = budy.OrderLine(quantity=2.0)
        order_line.product = product

        self.assertRaises(appier.AssertionError, order_line.save)
        self.assertEqual(order_line.is_valid(), False)
        self.assertEqual(order_line.is_valid_quantity(), True)
        self.assertEqual(order_line.is_valid_price(), True)
        self.assertEqual(order_line.is_valid_size(), False)

        order_line = budy.OrderLine(price=12.0, quantity=2.0, size=12, scale=1)
        order_line.product = product

        self.assertEqual(order_line.is_valid(), True)
        self.assertEqual(order_line.size_s, None)

        order_line.ensure_size_s()

        self.assertEqual(order_line.size_s, "12")

        order_line.save()
        order.add_line_s(order_line)

        self.assertEqual(order.sub_total, 24.0)
        self.assertEqual(order.discount, 0.0)
        self.assertEqual(order.total, 24.0)
        self.assertEqual(order.payable, 24.0)
        self.assertEqual(order.discountable, 24.0)

    def test_free(self):
        product = budy.Product(
            short_description="product", gender="Male", price=10.0, quantity_hand=5.0
        )
        product.save()

        order = budy.Order()
        order.save()

        order_line = budy.OrderLine(quantity=2.0)
        order_line.product = product
        order_line.save()
        order.add_line_s(order_line)

        self.assertEqual(order_line.quantity, 2.0)
        self.assertEqual(order_line.total, 20.0)
        self.assertEqual(order.total, 20.0)
        self.assertEqual(len(order.lines), 1)

        address = budy.Address(
            first_name="first name",
            last_name="last name",
            address="address",
            city="city",
        )
        address.save()

        order.shipping_address = address
        order.billing_address = address
        order.email = "username@email.com"
        order.save()

        voucher = budy.Voucher(amount=20.0)
        voucher.save()

        order.add_voucher_s(voucher)

        self.assertEqual(order.sub_total, 20.0)
        self.assertEqual(order.discount, 20.0)
        self.assertEqual(order.total, 0.0)
        self.assertEqual(order.payable, 0.0)
        self.assertEqual(order.discountable, 20.0)
        self.assertEqual(order.paid, False)
        self.assertEqual(order.inventory_decremented, False)
        self.assertEqual(isinstance(order.sub_total, commons.Decimal), True)
        self.assertEqual(isinstance(order.discount, commons.Decimal), True)
        self.assertEqual(isinstance(order.total, commons.Decimal), True)
        self.assertEqual(isinstance(order.payable, commons.Decimal), True)
        self.assertEqual(isinstance(order.discountable, commons.Decimal), True)

        order.pay_s()

        self.assertEqual(order.sub_total, 20.0)
        self.assertEqual(order.discount, 20.0)
        self.assertEqual(order.total, 0.0)
        self.assertEqual(order.payable, 0.0)
        self.assertEqual(order.discountable, 20.0)
        self.assertEqual(order.paid, True)
        self.assertEqual(order.inventory_decremented, True)
        self.assertEqual(order.payment_data, {})
        self.assertEqual(isinstance(order.sub_total, commons.Decimal), True)
        self.assertEqual(isinstance(order.discount, commons.Decimal), True)
        self.assertEqual(isinstance(order.total, commons.Decimal), True)
        self.assertEqual(isinstance(order.payable, commons.Decimal), True)
        self.assertEqual(isinstance(order.discountable, commons.Decimal), True)

        product = product.reload()

        self.assertEqual(product.quantity_hand, 3.0)

    def test_closed(self):
        order = budy.Order()
        order.save()

        product = budy.Product(short_description="product", gender="Male", price=10.0)
        product.save()

        order_line = budy.OrderLine(quantity=2.0)
        order_line.product = product
        order_line.save()
        order.add_line_s(order_line)

        address = budy.Address(
            first_name="first name",
            last_name="last name",
            address="address",
            city="city",
        )
        address.save()

        order.shipping_address = address
        order.billing_address = address
        order.email = "username@email.com"
        order.save()

        self.assertEqual(order.is_open(), True)
        self.assertEqual(order.is_closed(), False)

        order.mark_waiting_payment_s()

        self.assertEqual(order.is_open(), False)
        self.assertEqual(order.is_closed(), True)

    def test_payment_method(self):
        product = budy.Product(
            short_description="product", gender="Male", price=10.0, quantity_hand=5.0
        )
        product.save()

        order = budy.Order()
        order.save()

        order_line = budy.OrderLine(quantity=2.0)
        order_line.product = product
        order_line.save()
        order.add_line_s(order_line)

        self.assertEqual(order_line.quantity, 2.0)
        self.assertEqual(order_line.total, 20.0)
        self.assertEqual(order.total, 20.0)
        self.assertEqual(len(order.lines), 1)

        address = budy.Address(
            first_name="first name",
            last_name="last name",
            address="address",
            city="city",
        )
        address.save()

        order.shipping_address = address
        order.billing_address = address
        order.email = "username@email.com"
        order.save()

        self.assertEqual(order.is_valid(), True)
        self.assertEqual(order_line.is_valid_quantity(), True)
        self.assertEqual(order.paid, False)
        self.assertEqual(order.inventory_decremented, False)
        self.assertEqual(order.status, "created")

        self.assertRaises(
            appier.SecurityError, lambda: order.pay_s(payment_data=dict(type="simple"))
        )

        order.pay_s(payment_data=dict(type="simple"), strict=False)

        self.assertEqual(order.is_valid(), True)
        self.assertEqual(order_line.is_valid_quantity(), True)
        self.assertEqual(order.paid, False)
        self.assertEqual(order.inventory_decremented, False)
        self.assertEqual(order.status, "waiting_payment")

        self.assertRaises(
            appier.SecurityError,
            lambda: order.end_pay_s(payment_data=dict(type="simple"), strict=True),
        )

        order.end_pay_s(payment_data=dict(type="simple"))

        self.assertEqual(order.is_valid(), True)
        self.assertEqual(order_line.is_valid_quantity(), True)
        self.assertEqual(order.paid, True)
        self.assertEqual(order.inventory_decremented, True)
        self.assertEqual(order.status, "paid")

        product = product.reload()

        self.assertEqual(product.quantity_hand, 3.0)

    def test__build_notes(self):
        product = budy.Product(short_description="product", gender="Male", price=10.0)
        product.save()

        order = budy.Order()
        order.save()

        order_line = budy.OrderLine(quantity=2.0)
        order_line.product = product
        order_line.save()
        order.add_line_s(order_line)

        self.assertEqual(order_line.quantity, 2.0)
        self.assertEqual(order_line.total, 20.0)
        self.assertEqual(order.total, 20.0)
        self.assertEqual(len(order.lines), 1)

        notes = order._build_notes()

        self.assertEqual(notes, "Budy order - BD-000001")

        order_line.attributes = json.dumps(dict(initials="IN"))
        order_line.save()

        order = order.reload()
        notes = order._build_notes()

        self.assertEqual(
            notes, "Budy order - BD-000001\nOrder line - product | initials = IN"
        )

        order_line.attributes = json.dumps(dict(initials="IN", engraving="gold"))
        order_line.save()

        order = order.reload()
        notes = order._build_notes()

        self.assertEqual(
            notes,
            "Budy order - BD-000001\nOrder line - product | engraving = gold\nOrder line - product | initials = IN",
        )

        order_line.attributes = "INVALID STRING"
        order_line.save()

        order = order.reload()
        notes = order._build_notes()

        self.assertEqual(notes, "Budy order - BD-000001")

        order_line.attributes = None
        order_line.save()

        order = order.reload()
        notes = order._build_notes()

        self.assertEqual(notes, "Budy order - BD-000001")

        order_line.attributes = 12345
        order_line.save()

        order = order.reload()
        notes = order._build_notes()

        self.assertEqual(notes, "Budy order - BD-000001")
