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

import appier

import budy

from . import root

class AccountAPIController(root.RootAPIController):

    @appier.route("/api/accounts", "GET", json = True)
    @appier.ensure(token = "admin")
    def list(self):
        object = appier.get_object(alias = True, find = True)
        accounts = budy.BudyAccount.find(map = True, **object)
        return accounts

    @appier.route("/api/accounts", "POST", json = True)
    def create(self):
        pre_enabled = self.field("pre_enabled", False, cast = bool)
        account = budy.BudyAccount.new()
        account.type = budy.BudyAccount.USER_TYPE
        account.password_confirm = account.password
        account.enabled = pre_enabled
        account.save()
        account = account.reload(rules = True, map = True)
        return account

    @appier.route("/api/accounts/confirm/<str:token>", "GET", json = True)
    def confirm(self, token):
        account = budy.BudyAccount.get(confirmation_token = token)
        account.confirm_s()
        return account

    @appier.route("/api/accounts/recover/<str:identifier>", "GET", json = True)
    def recover(self, identifier):
        budy.BudyAccount.recover(identifier)

    @appier.route("/api/accounts/reset", "POST", json = True)
    def reset(self):
        token = self.field("token", mandatory = True)
        password = self.field("password", mandatory = True)
        budy.BudyAccount.reset(token, password, password)

    @appier.route("/api/accounts/me", "GET", json = True)
    @appier.ensure(token = "user")
    def me(self):
        account = budy.BudyAccount.from_session(map = True)
        return account

    @appier.route("/api/accounts/me", "PUT", json = True)
    @appier.ensure(token = "user")
    def update_me(self):
        account = budy.BudyAccount.from_session()
        account.apply()
        account.save()
        account = account.map()
        return account

    @appier.route("/api/accounts/me/avatar", "GET", json = True)
    @appier.ensure(token = "user")
    def avatar_me(self):
        account = budy.BudyAccount.from_session(rules = False)
        return account._send_avatar()

    @appier.route("/api/accounts/me/orders", "GET", json = True)
    @appier.ensure(token = "user")
    def orders_me(self):
        object = appier.get_object(alias = True, find = True, sort = [("id", -1)])
        account = budy.BudyAccount.from_session()
        orders = budy.Order.find(
            account = account.id,
            paid = True,
            eager = ("lines",),
            map = True,
            **object
        )
        return orders

    @appier.route("/api/accounts/me/addresses", "GET", json = True)
    @appier.ensure(token = "user")
    def addresses_me(self):
        account = budy.BudyAccount.from_session(
            eager = ("addresses",),
            map = True
        )
        return account["addresses"]

    @appier.route("/api/accounts/me/addresses", "POST", json = True)
    @appier.ensure(token = "user")
    def create_address_me(self):
        address = budy.Address.new()
        address.save()
        account = budy.BudyAccount.from_session(rules = False)
        account.addresses.append(address)
        account.save()
        address = address.map()
        return address

    @appier.route("/api/accounts/me/addresses/<str:key>", "DELETE", json = True)
    @appier.ensure(token = "user")
    def delete_address_me(self, key):
        address = budy.Address.get(key = key)
        account = budy.BudyAccount.from_session(rules = False)
        account.addresses.remove(address.id)
        account.save()
        address.delete()

    @appier.route("/api/accounts/simple.csv", "GET")
    @appier.ensure(token = "admin")
    def simple_csv(self):
        object = appier.get_object(
            alias = True,
            find = True,
            limit = 0
        )
        accounts = budy.BudyAccount.find(
            **object
        )

        accounts_s = [(
            "username",
            "email",
            "first_name",
            "last_name",
            "birth_date"
        )]
        for account in accounts:
            account_s = (
                account.username,
                account.email,
                account.first_name,
                account.last_name,
                account.birth_date
            )
            accounts_s.append(account_s)

        result = appier.serialize_csv(accounts_s, delimiter = ",")
        self.content_type("text/csv")
        return result
