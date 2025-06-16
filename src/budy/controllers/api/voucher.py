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

from . import root


class VoucherAPIController(root.RootAPIController):
    @appier.route("/api/vouchers", "GET", json=True)
    @appier.ensure(token="admin")
    def list(self):
        object = appier.get_object(alias=True, find=True, sort=[("id", -1)])
        vouchers = budy.Voucher.find(map=True, **object)
        return vouchers

    @appier.route("/api/vouchers", "POST", json=True)
    @appier.ensure(token="admin")
    def create(self):
        voucher = budy.Voucher.new(fill_safe=True)
        voucher.save()
        voucher = voucher.map()
        return voucher

    @appier.route("/api/vouchers/<int:key>", "GET", json=True)
    @appier.ensure(token="admin")
    def show(self, key):
        voucher = budy.Voucher.get_e(key=key, map=True)
        return voucher

    @appier.route("/api/vouchers/value", "POST", json=True)
    @appier.ensure(token="admin")
    def create_value(self):
        object = appier.get_object()
        key = object.get("key", None)
        amount = object.get("amount", None)
        currency = object.get("currency", None)
        unlimited = object.get("unlimited", False)
        key = self.field("key", key)
        amount = self.field("amount", amount, cast=float)
        currency = self.field("currency", currency, cast=str)
        unlimited = self.field("unlimited", unlimited, cast=bool)
        voucher = budy.Voucher.create_value_s(key, amount, currency, unlimited)
        voucher = voucher.map()
        return voucher

    @appier.route("/api/vouchers/percentage", "POST", json=True)
    @appier.ensure(token="admin")
    def create_percentage(self):
        object = appier.get_object()
        key = object.get("key", None)
        percentage = object.get("percentage", None)
        key = self.field("key", key)
        percentage = self.field("percentage", percentage, cast=float)
        voucher = budy.Voucher.create_percentage_s(key, percentage)
        voucher = voucher.map()
        return voucher

    @appier.route("/api/vouchers/<str:key>/use", "POST", json=True)
    @appier.ensure(token="admin")
    def use(self, key):
        object = appier.get_object()
        amount = object.get("amount", None)
        currency = object.get("currency", None)
        justification = object.get("justification", None)
        save_use = object.get("save_use", True)
        voucher = budy.Voucher.get_e(key=key)
        voucher_use = voucher.use_s(
            amount, currency=currency, justification=justification, save_use=save_use
        )
        voucher = voucher.map()
        if voucher_use:
            voucher["use"] = voucher_use.map()
        return voucher

    @appier.route("/api/vouchers/<str:key>/disuse", "POST", json=True)
    @appier.ensure(token="admin")
    def disuse(self, key):
        voucher = budy.Voucher.get_e(key=key)
        voucher.disuse_s()
        voucher = voucher.map()
        return voucher
