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

from . import group


class Section(group.Group):
    """
    The section entity that represents an aggregation of groups
    that together define a proper unit of e-commerce (eg: watches
    vs jewelry on an e-commerce that sells both).

    Can be used for the creation of filtered "views" of the products
    so that partially disjoint groups are created.
    """

    context_fields = appier.field(
        type=list,
        observations="""The name of the fields that are
        considered to define the context of the section and
        that as such are going to be used in the filtering
        process of the associated products""",
    )
    """ Field that can be used to control the context filtering
    for the section by listing the names of the fields that are
    going to be used in the query, in case no value is defined
    all of the non empty groups are going to be used in the "view" """

    invisible_fields = appier.field(
        type=list,
        observations="""The name of the fields (groups) that
        although being used as part of the context selection for
        the section should not be displayed in the "normal" listing
        UI for the section""",
    )
    """ Field that controls the groups that are going to be hidden
    from the UI although being used for the context filtering"""

    genders = appier.field(type=list)

    collections = appier.field(type=appier.references("Collection", name="id"))

    categories = appier.field(type=appier.references("Category", name="id"))

    colors = appier.field(type=appier.references("Color", name="id"))

    brands = appier.field(type=appier.references("Brand", name="id"))

    seasons = appier.field(type=appier.references("Season", name="id"))

    @classmethod
    def validate(cls):
        return super(Section, cls).validate() + [
            appier.not_null("name"),
            appier.not_empty("name"),
        ]

    @classmethod
    def list_names(cls):
        return ["id", "name"]

    @appier.operation(
        name="Add Collection",
        parameters=(
            ("Collection", "collection", appier.reference("Collection", name="id")),
        ),
    )
    def add_collection_s(self, collection):
        if not collection:
            return
        self.collections.append(collection)
        self.save()

    @appier.operation(
        name="Remove Collection",
        parameters=(
            ("Collection", "collection", appier.reference("Collection", name="id")),
        ),
    )
    def remove_collection_s(self, collection):
        if not collection:
            return
        self.collections.remove(collection)
        self.save()

    @appier.operation(name="Clear Groups", level=2)
    def clear_groups_s(self):
        self.collections = []
        self.categories = []
        self.colors = []
        self.brands = []
        self.seasons = []
        self.save()
