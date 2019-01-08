#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Budy
# Copyright (c) 2008-2018 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2018 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import time

import appier

import budy

from . import base

class TrackingBot(base.Bot):

    def __init__(self, *args, **kwargs):
        base.Bot.__init__(self, *args, **kwargs)
        self.enabled = appier.conf("TRACKING_BOT_ENABLED", False, cast = bool)
        self.window = appier.conf("TRACKING_BOT_WINDOW", 14 * 86400, cast = int)
        self.enabled = kwargs.get("enabled", self.enabled)
        self.window = kwargs.get("window", self.window)
        self.api = None

    def tick(self):
        if not self.enabled: return
        self.sync_sent()

    def sync_sent(self):
        orders = budy.Order.find_e(
            status = "sent",
            created = {"$gt" : time.time() - self.window},
            limit = -1
        )
        for order in orders:
            if not order.tracking_number: continue
            try:
                result = appier.get(
                    "https://cttpie.stage.hive.pt",
                    params = dict(tracking = order.tracking_number)
                )
                if not result["status"] == "Entregue": continue
                order.mark_received_s()
            except BaseException as exception:
                self.logger.warn(
                    "Problem syncing order %s - %s ..." % (order.reference, exception)
                )
            self.logger.info("Marked order %s as received ..." % order.reference)
