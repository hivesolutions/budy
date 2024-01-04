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

import appier

import budy


class OrderController(appier.Controller):
    @appier.route("/orders/me", "GET")
    @appier.route("/orders/me/<str:status>", "GET")
    @appier.ensure(token="user")
    def me(self, status="waiting_payment"):
        account = budy.BudyAccount.from_session()
        orders = account.get_store_orders(status=status)
        return self.template("order/me.html.tpl", orders=orders)

    @appier.route("/orders/<str:key>/mark_paid", "GET")
    @appier.ensure(token="user")
    def mark_paid(self, key):
        order = budy.Order.get(key=key)
        account = budy.BudyAccount.from_session()
        order.verify_account(account)
        order.mark_paid_s()
        order.notify_s()
        return self.redirect(self.url_for("order.me"))
