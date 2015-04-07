#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Budy
# Copyright (C) 2008-2015 Hive Solutions Lda.
#
# This file is part of Hive Budy.
#
# Hive Budy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hive Budy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hive Budy. If not, see <http://www.gnu.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2015 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

import appier

from . import base

class Product(base.BudyBase):

    short_description = dict()

    gender = dict()

    tag = dict()

    tag_descritpion = dict()

    categories = dict() #@todo many relations

    variants = dict() #@todo many relations

    images = dict() #@todo many relations

    brand = dict() #@todo one relations

    season = dict() #@todo one relation

    measurements = dict() #@todo many relation

    compositions = dict() #@todo many relation

    live_movel = dict() #@todo one relation

    @classmethod
    def validate(cls):
        return super(Product, cls).validate() + [
            appier.not_null("short_description"),
            appier.not_empty("short_description"),

            appier.not_null("gender"),
            appier.not_empty("gender")
        ]

    @classmethod
    def list_names(cls):
        return ["id", "short_description", "gender", "tag"]
