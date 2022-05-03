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
import appier_extras

from budy import bots

class BudyApp(appier.WebApp):

    def __init__(self, *args, **kwargs):
        appier.WebApp.__init__(
            self,
            name = "budy",
            parts = (
                appier_extras.AdminPart,
            ),
            *args, **kwargs
        )
        self.login_route = "base.signin"
        self.login_redirect = "base.index_store"
        self.logout_redirect = "base.signin"
        self.scheduler = bots.Scheduler(self)
        self.omni_api = None

    def start(self):
        appier.WebApp.start(self)
        self.scheduler.start()
        self.admin_part.add_operation(
            "force_scheduler", "admin.force_scheduler",
            description = "Force scheduler",
            message = "Are you really sure you want to force scheduler?",
            note = "Forcing scheduler may consume computer resources",
            level = 3
        )

    def stop(self):
        try: import easypay
        except ImportError: easypay = None
        if easypay: easypay.ShelveAPI.cleanup()
        appier.WebApp.stop(self)

    def get_omni_api(self):
        import omni
        if self.omni_api: return self.omni_api
        self.omni_api = omni.API()
        return self.omni_api

    def _version(self):
        return "0.6.3"

    def _description(self):
        return "Budy"

    def _observations(self):
        return "Simple and easy to use E-commerce engine"

if __name__ == "__main__":
    app = BudyApp()
    app.serve()
else:
    __path__ = []
