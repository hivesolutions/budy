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

class ColorAPIController(root.RootAPIController):

    @appier.route("/api/colors", "GET", json = True)
    def list(self):
        object = appier.get_object(alias = True, find = True)
        colors = budy.Color.find_e(
            eager = ("images",),
            map = True,
            **object
        )
        return colors

    @appier.route("/api/colors/<int:id>", "GET", json = True)
    def show(self, id):
        color = budy.Color.get_e(id = id, map = True)
        return color

    @appier.route("/api/colors/slug/<str:slug>", "GET", json = True)
    def slug(self, slug):
        color = budy.Color.get_e(slug = slug, map = True)
        return color
