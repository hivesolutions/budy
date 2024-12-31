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


class EasypayV2APIController(root.RootAPIController):
    @appier.route("/api/easypay_v2/generic_notification", "POST", json=True)
    def generic_notification(self):
        data = appier.request_json()
        api = budy.Order._get_api_easypay_v2()
        api.notify_payment(data)

    @appier.route("/api/easypay_v2/payment_notification", "POST", json=True)
    def payment_notification(self):
        pass

    @appier.route("/api/easypay_v2/cancel", ("GET", "POST"), json=True)
    @appier.ensure(token="admin")
    def cancel(self):
        identifier = self.field("identifier", mandatory=True)
        api = budy.Order._get_api_easypay_v2()
        return api.cancel_payment(identifier)

    @appier.route("/api/easypay_v2/delete", ("GET", "POST"), json=True)
    @appier.ensure(token="admin")
    def delete(self):
        identifier = self.field("identifier", mandatory=True)
        api = budy.Order._get_api_easypay_v2()
        return api.del_payment(identifier)

    @appier.route("/api/easypay_v2/diagnostics", "GET", json=True)
    @appier.ensure(token="admin")
    def diagnostics(self):
        api = budy.Order._get_api_easypay_v2()
        return api.diagnostics()
