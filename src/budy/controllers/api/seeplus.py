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

import time

import appier

import budy

from . import root


class SeeplusAPIController(root.RootAPIController):
    @appier.route("/api/seeplus/update", "POST", json=True)
    def update(self):
        key = self.field("token", None)
        key = self.field("key", key)
        key = self.request.get_header("X-Seeplus-Key", key)
        _key = appier.conf("SEEPLUS_KEY", None)
        if _key and not _key == key:
            raise appier.SecurityError(message="Mismatch in Seeplus key", code=401)
        object = appier.get_object()
        event = object.get("event", "OrderManagement.StatusChanged")
        data = object.get("data", {})
        result = "Ignored"
        if event == "OrderManagement.StatusChanged":
            self._status_change_s(data)
            result = "Handled"
        return dict(result=result)

    def _status_change_s(self, data):
        for key in ("code", "status"):
            appier.verify(
                key in data,
                message="Missing '%s' in Seeplus data payload" % key,
                code=400,
            )
        reference, status = data["code"], data["status"]
        order = budy.Order.get(reference=reference)
        seeplus_status = order.meta.get("seeplus_status", None)
        seeplus_timestamp = order.meta.get("seeplus_timestamp", None)
        seeplus_updates = order.meta.get("seeplus_updates", [])
        if not seeplus_timestamp:
            raise appier.OperationalError(message="Order not imported in Seeplus")
        if status == seeplus_status:
            raise appier.OperationalError(
                message="Order already in status '%s'" % status
            )
        status_timestamp = time.time()
        seeplus_updates.append(dict(status=status, timestamp=status_timestamp))
        order.meta.update(
            seeplus_status=status,
            seeplus_update=status_timestamp,
            seeplus_updates=seeplus_updates,
        )
        order.save()
