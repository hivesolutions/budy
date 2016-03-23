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

import appier

import budy

from . import root

class OrderApiController(root.RootApiController):

    @appier.route("/api/orders", "GET", json = True)
    @appier.ensure(token = "admin")
    def list(self):
        object = appier.get_object(alias = True, find = True)
        orders = budy.Order.find(
            eager = (
                "lines",
                "lines.product",
                "shipping_address",
                "billing_address"
            ),
            map = True,
            **object
        )
        return orders

    @appier.route("/api/orders/<str:key>", "GET", json = True)
    @appier.ensure(token = "user")
    def show(self, key):
        order = budy.Order.get(key = key)
        order.refresh_s(
            currency = order.shipping_currency or self.currency,
            country = order.shipping_country or self.country
        )
        order = order.reload(
            eager = (
                "lines",
                "lines.product",
                "shipping_address",
                "billing_address"
            ),
            map = True
        )
        return order

    @appier.route("/api/orders/<str:key>/shipping_address", "PUT", json = True)
    @appier.ensure(token = "user")
    def set_shipping_address(self, key):
        address = budy.Address.new()
        address.save()
        order = budy.Order.get(key = key, rules = False)
        order.shipping_address = address
        order.save()
        order = order.reload(
            eager = (
                "lines",
                "lines.product",
                "shipping_address",
                "billing_address"
            ),
            map = True
        )
        return order

    @appier.route("/api/orders/<str:key>/billing_address", "PUT", json = True)
    @appier.ensure(token = "user")
    def set_billing_address(self, key):
        address = budy.Address.new()
        address.save()
        order = budy.Order.get(key = key, rules = False)
        order.billing_address = address
        order.save()
        order = order.reload(
            eager = (
                "lines",
                "lines.product",
                "shipping_address",
                "billing_address"
            ),
            map = True
        )
        return order

    @appier.route("/api/orders/<str:key>/email", "PUT", json = True)
    @appier.ensure(token = "user")
    def set_email(self, key):
        data = appier.request_json()
        email = data["email"]
        order = budy.Order.get(key = key, rules = False)
        order.email = email
        order.save()
        order = order.reload(
            eager = (
                "lines",
                "lines.product",
                "shipping_address",
                "billing_address"
            ),
            map = True
        )
        return order

    @appier.route("/api/orders/<str:key>/pay", "PUT", json = True)
    @appier.ensure(token = "user")
    def pay(self, key):
        data = appier.request_json()
        empty_bag = self.field("empty_bag", True, cast = bool)
        order = budy.Order.get(key = key, rules = False)
        order.pay_s(data)
        bag = budy.Bag.from_session()
        if empty_bag and bag: bag.empty_bag_s()
        order = order.reload(
            eager = (
                "lines",
                "lines.product",
                "shipping_address",
                "billing_address"
            ),
            map = True
        )
        return order
