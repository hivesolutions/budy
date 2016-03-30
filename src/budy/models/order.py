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
import appier_extras

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

    notification_sent = appier.field(
        type = bool,
        index = True,
        initial = False,
        safe = True
    )

    lines = appier.field(
        type = appier.references(
            "OrderLine",
            name = "id"
        ),
        eager = True
    )

    account = appier.field(
        type = appier.reference(
            "BudyAccount",
            name = "id"
        ),
        eager = True
    )

    shipping_address = appier.field(
        type = appier.reference(
            "Address",
            name = "id"
        ),
        eager = True
    )

    billing_address = appier.field(
        type = appier.reference(
            "Address",
            name = "id"
        ),
        eager = True
    )

    def __init__(self, *args, **kwargs):
        bundle.Bundle.__init__(self, *args, **kwargs)
        self.created = kwargs.get("status", "created")
        self.paid = kwargs.get("paid", False)
        self.date = kwargs.get("date", None)
        self.notification_sent = kwargs.get("notification_sent", False)

    @classmethod
    def list_names(cls):
        return ["id", "total", "currency", "account", "status"]

    @classmethod
    def order_name(self):
        return ["id", -1]

    @classmethod
    def line_cls(cls):
        return order_line.OrderLine

    @classmethod
    @appier.link(
        name = "Export Complex",
        parameters = (
            ("Start Id", "start", int),
            ("End Id", "end", int),
        )
    )
    def complex_csv_url(cls, start = None, end = None, absolute = False):
        return appier.get_app().url_for(
            "order_api.complex_csv",
            start = start,
            end = end,
            absolute = absolute
        )

    @classmethod
    def _build(cls, model, map):
        prefix = appier.conf("BUDY_ORDER_REF", "BD-%06d")
        id = model.get("id", None)
        if id: model["reference"] = prefix % id

    def pre_delete(self):
        bundle.Bundle.pre_delete(self)
        for line in self.lines: line.delete()

    def add_line_s(self, line):
        line.order = self
        return bundle.Bundle.add_line_s(self, line)

    def refresh_s(self, *args, **kwargs):
        if self.paid: return
        bundle.Bundle.refresh_s(self, *args, **kwargs)

    def verify(self):
        appier.verify(not self.billing_address == None)
        appier.verify(self.status == "created")
        appier.verify(self.paid == False)
        appier.verify(self.date == None)

    def pay_s(self, payment_data, notify = False):
        self.verify()
        self._pay_stripe(payment_data)
        self.mark_paid_s()
        if notify: self.notify_s()

    @appier.operation(name = "Notify")
    def notify_s(self, name = "order.new"):
        order = self.reload(map = True)
        appier_extras.admin.Event.notify_g(
            name,
            arguments = dict(
                params = dict(
                    order = order
                )
            )
        )
        self.notification_sent = True
        self.save()

    @appier.operation(name = "Mark Paid")
    def mark_paid_s(self):
        self.verify()
        self.status = "paid"
        self.paid = True
        self.date = time.time()
        self.save()

    @appier.operation(name = "Garbage Collect")
    def collect_s(self):
        if self.paid: return
        self.delete()

    @appier.operation(name = "Fix Orphans")
    def fix_orphans_s(self):
        for line in self.lines:
            line.order = self
            line.save()

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
