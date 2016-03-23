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

import time

import appier

from . import bundle
from . import country
from . import order_line

class Order(bundle.Bundle):

    STATUS_S = dict(
        created = "created",
        paid = "paid",
        sent = "sent",
        received = "received",
        returned = "returned",
        canceled = "canceled"
    )

    STATUS_C = dict(
        created = "grey",
        paid = "blue",
        sent = "blue",
        received = "green",
        returned = "red",
        canceled = "red"
    )

    status = appier.field(
        initial = "created",
        index = True,
        safe = True,
        meta = "enum",
        enum = STATUS_S,
        colors = STATUS_C
    )

    paid = appier.field(
        type = bool,
        initial = False,
        safe = True
    )

    date = appier.field(
        type = int,
        index = True,
        safe = True,
        meta = "datetime"
    )

    email = appier.field(
        index = True,
        safe = True
    )

    lines = appier.field(
        type = appier.references(
            "OrderLine",
            name = "id"
        )
    )

    account = appier.field(
        type = appier.reference(
            "BudyAccount",
            name = "id"
        )
    )

    shipping_address = appier.field(
        type = appier.reference(
            "Address",
            name = "id"
        )
    )

    billing_address = appier.field(
        type = appier.reference(
            "Address",
            name = "id"
        )
    )

    def __init__(self, *args, **kwargs):
        bundle.Bundle.__init__(self, *args, **kwargs)
        self.paid = kwargs.get("paid", False)

    @classmethod
    def list_names(cls):
        return ["id", "currency", "total", "account", "status"]

    @classmethod
    def order_name(self):
        return ["id", -1]

    @classmethod
    def line_cls(cls):
        return order_line.OrderLine

    @classmethod
    def _build(cls, model, map):
        prefix = appier.conf("BUDY_ORDER_REF", "BD-%05d")
        id = model.get("id", None)
        if id: model["refernce"] = prefix % id

    def verify(self):
        appier.verify(not self.billing_address == None)
        appier.verify(self.status == "created")
        appier.verify(self.paid == False)

    def pay_s(self, payment_data):
        self.verify()
        self._pay_stripe(payment_data)
        self.status = "paid"
        self.paid = True
        self.date = time.time()
        self.save()

    @property
    def shipping_country(self):
        has_shipping = hasattr(self, "shipping_address")
        if not has_shipping: return None
        if not self.shipping_address: return None
        return self.shipping_address.country

    @property
    def shipping_currency(self):
        if not self.shipping_country: return None
        shipping_country = country.Country.get_by_code(self.shipping_country)
        return shipping_country.currency_code

    def _pay_stripe(self, payment_data):
        import stripe
        api = stripe.Api()
        number = payment_data["card_number"]
        exp_month = int(payment_data["expiration_month"])
        exp_year = int(payment_data["expiration_year"])
        name = payment_data.get("card_name", None)
        api.create_charge(
            int(self.total * 100),
            self.currency,
            exp_month,
            exp_year,
            number,
            name = name
        )
