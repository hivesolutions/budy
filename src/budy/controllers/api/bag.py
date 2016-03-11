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

class BagApiController(appier.Controller):

    @appier.route("/api/bags", "GET", json = True)
    @appier.ensure(token = "admin")
    def list(self):
        object = appier.get_object(alias = True, find = True)
        products = budy.Bag.find(
            eager = ("lines",),
            map = True,
            **object
        )
        return products

    @appier.route("/api/bags", "POST", json = True)
    def create(self):
        bag = budy.Bag.new()
        bag.save()
        bag = bag.map()
        return bag

    @appier.route("/api/bags/key", "GET", json = True)
    def key(self):
        bag = budy.Bag.from_session()
        return dict(key = bag.key)

    @appier.route("/api/bags/<str:key>", "GET", json = True)
    def show(self, key):
        bag = budy.Bag.get(
            key = key,
            eager = ("lines",),
            map = True
        )
        return bag

    @appier.route("/api/bags/<str:key>/lines", "POST", json = True)
    def add_line(self, key):
        bag_line = budy.BagLine.new()
        bag_line.save()
        bag = budy.Bag.get(key = key)
        bag.lines.append(bag_line)
        bag.save()
        return bag_line
