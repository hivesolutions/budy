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

from . import base


class VoucherUse(base.BudyBase):

    USAGE_TYPE_S = dict(
        percentage="percentage",
        value="value",
    )

    usage_type = appier.field(
        type=str,
        safe=True,
        meta="enum",
        enum=USAGE_TYPE_S,
        observations="""Type of usage, either value or percentage""",
    )

    amount = appier.field(
        type=float,
        safe=True,
        observations="""The amount used from the voucher""",
    )

    currency = appier.field(
        type=str,
        safe=True,
        observations="""Currency in which the amount was expressed""",
    )

    justification = appier.field(
        type=str,
        safe=True,
        observations="""Justification or reason for the usage of the voucher,
        may contain external ID references""",
    )

    voucher = appier.field(
        type=appier.reference("Voucher", name="id"),
        safe=True,
        observations="""Reference to the voucher instance that was used.""",
    )

    account = appier.field(
        type=appier.reference("BudyAccount", name="id"),
        safe=True,
        observations="""Reference to the account that used the voucher (nullable).""",
    )

    @classmethod
    def validate(cls):
        return super(VoucherUse, cls).validate() + [
            appier.not_null("voucher"),
        ]

    @classmethod
    def list_names(cls):
        return [
            "id",
            "voucher",
            "account",
            "amount",
            "usage_type",
            "justification",
            "created",
        ]

    @classmethod
    def order_name(cls):
        return ["id", -1]
