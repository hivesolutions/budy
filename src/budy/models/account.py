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
import appier_extras

from . import bag

class BudyAccount(appier_extras.admin.Account):

    PREFIXES = appier_extras.admin.Account.PREFIXES + [
        "budy."
    ]

    GENDER_S = dict(
        Male = "Male",
        Female = "Female"
    )

    first_name = appier.field(
        index = True
    )

    last_name = appier.field(
        index = True
    )

    gender = appier.field(
        meta = "enum",
        enum = GENDER_S
    )

    birth_date = appier.field(
        type = int,
        index = True,
        meta = "date"
    )

    country = appier.field(
        meta = "country"
    )

    phone_number = appier.field()

    receive_newsletters = appier.field(
        type = bool,
        initial = False
    )

    addresses = appier.field(
        type = appier.references(
            "Address",
            name = "id"
        )
    )

    @classmethod
    def _build(cls, model, map):
        id = model.get("id", None)
        if id: model["bag_key"] = cls._get_bag_key(id)

    @classmethod
    def _get_bag_key(cls, id):
        _bag = bag.Bag.get(account = id, raise_e = False)
        if not _bag: return None
        return _bag.key

    def pre_create(self):
        appier_extras.admin.Account.pre_create(self)
        if not hasattr(self, "first_name"): self.first_name = self.username

    def post_create(self):
        appier_extras.admin.Account.post_create(self)
        self.ensure_bag_s()

    def ensure_bag_s(self, key = None):
        _bag = self.get_bag()
        if _bag: return _bag
        _bag = bag.Bag(key = key)
        _bag.account = self
        _bag.save()
        return _bag

    def get_bag(self):
        return bag.Bag.get(account = self.id, raise_e = False)
