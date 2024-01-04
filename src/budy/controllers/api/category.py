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


class CategoryAPIController(root.RootAPIController):
    @appier.route("/api/categories", "GET", json=True)
    def list(self):
        object = appier.get_object(alias=True, find=True)
        categories = budy.Category.find_e(eager=("images",), map=True, **object)
        return categories

    @appier.route("/api/categories/<int:id>", "GET", json=True)
    def show(self, id):
        category = budy.Category.get_e(id=id, map=True)
        return category

    @appier.route("/api/categories/slug/<str:slug>", "GET", json=True)
    def slug(self, slug):
        category = budy.Category.get_e(slug=slug, map=True)
        return category
