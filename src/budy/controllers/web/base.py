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


class BaseController(appier.Controller):
    @appier.route("/", "GET")
    def index(self):
        return self.redirect(self.url_for("admin.index"))

    @appier.route("/index_store", "GET")
    def index_store(self):
        return self.redirect(self.url_for("order.me"))

    @appier.route("/signin", "GET")
    def signin(self):
        next = self.field("next")
        error = self.field("error")
        return self.template("signin.html.tpl", next=next, error=error)

    @appier.route("/signin", "POST")
    def login(self):
        username = self.field("username")
        password = self.field("password")
        next = self.field("next")
        try:
            account = budy.BudyAccount.login(username, password)
        except appier.AppierException as error:
            return self.template(
                "signin.html.tpl", next=next, username=username, error=error.message
            )

        account._set_account()

        return self.redirect(next or self.url_for(self.login_redirect), relative=True)

    @appier.route("/signout", "GET")
    def signout(self):
        next = self.field("next")
        budy.BudyAccount._unset_account()
        return self.redirect(next or self.url_for(self.logout_redirect), relative=True)
