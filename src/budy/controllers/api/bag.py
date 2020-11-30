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

class BagAPIController(root.RootAPIController):

    @appier.route("/api/bags", "GET", json = True)
    @appier.ensure(token = "admin")
    def list(self):
        object = appier.get_object(alias = True, find = True)
        bags = budy.Bag.find(eager_l = True, map = True, **object)
        return bags

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
        ensure = self.field("ensure", True, cast = bool)
        try_valid = self.field("try_valid", True, cast = bool)
        bag = budy.Bag.get(key = key, raise_e = not ensure)
        if not bag: bag = budy.Bag.ensure_s(key = key)
        bag.refresh_s(currency = self.currency, country = self.country)
        if try_valid: bag.try_valid_s()
        bag = bag.reload(
            eager = (
                "lines.product.images",
                "lines.product.brand"
            ),
            map = True
        )
        return bag

    @appier.route("/api/bags/<str:key>/merge/<str:target>", "PUT", json = True)
    def merge(self, key, target):
        increment = self.field("increment", False, cast = bool)
        bag = budy.Bag.get(key = key)
        target = budy.Bag.get(key = target)
        bag.merge_s(target.id, increment = increment)
        bag = bag.reload(map = True)
        return bag

    @appier.route("/api/bags/<str:key>/lines", "POST", json = True)
    def add_line(self, key):
        line = budy.BagLine.new()
        line.ensure_size_s()
        line.save()
        bag = budy.Bag.get(key = key)
        bag.lines.append(line)
        bag.save()
        line = line.reload(map = True)
        return line

    @appier.route("/api/bags/<str:key>/lines/<int:line_id>", "DELETE", json = True)
    def remove_line(self, key, line_id):
        bag = budy.Bag.get(key = key)
        bag.remove_line_s(line_id)
        bag = bag.reload(map = True)
        return bag

    @appier.route("/api/bags/<str:key>/lines/add_update", "POST", json = True)
    def add_update_line(self, key):
        increment = self.field("increment", True, cast = bool)
        line = budy.BagLine.new()
        line.ensure_size_s()
        bag = budy.Bag.get(key = key)
        line = bag.add_update_line_s(line, increment = increment)
        line = line.reload(map = True)
        return line

    @appier.route("/api/bags/<str:key>/empty", "GET", json = True)
    def empty(self, key):
        bag = budy.Bag.get(key = key)
        bag.empty_s()
        bag = bag.reload(map = True)
        return bag

    @appier.route("/api/bags/<str:key>/order", "GET", json = True)
    def order(self, key):
        bag = budy.Bag.get(key = key)
        order = bag.to_order_s()
        order = order.reload(map = True)
        return order
