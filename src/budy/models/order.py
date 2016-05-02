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
import commons

import appier
import appier_extras

from . import bundle
from . import country
from . import order_line

class Order(bundle.Bundle):

    STATUS_S = dict(
        created = "created",
        waiting_payment = "waiting_payment",
        paid = "paid",
        sent = "sent",
        received = "received",
        returned = "returned",
        canceled = "canceled"
    )

    STATUS_C = dict(
        created = "grey",
        waiting_payment = "orange",
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

    reference = appier.field(
        index = True,
        default = True,
        safe = True
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

    tracking_number = appier.field(
        index = True
    )

    tracking_url = appier.field(
        index = True,
        meta = "url"
    )

    lines = appier.field(
        type = appier.references(
            "OrderLine",
            name = "id"
        ),
        eager = True
    )

    vouchers = appier.field(
        type = appier.references(
            "Voucher",
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

    store = appier.field(
        type = appier.reference(
            "Store",
            name = "id"
        )
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

    @classmethod
    def list_names(cls):
        return ["reference", "total", "currency", "account", "email", "status"]

    @classmethod
    def line_cls(cls):
        return order_line.OrderLine

    @classmethod
    def is_snapshot(cls):
        return True

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

    def pre_delete(self):
        bundle.Bundle.pre_delete(self)
        for line in self.lines: line.delete()

    def post_create(self):
        bundle.Bundle.post_create(self)
        self.set_reference_s()

    def add_line_s(self, line):
        line.order = self
        return bundle.Bundle.add_line_s(self, line)

    def set_account_s(self, account):
        self.account = account
        self.store = self.account.store
        self.save()

    def add_voucher_s(self, voucher):
        appier.verify(voucher.is_valid(currency = self.currency))
        discount = voucher.discount(self.sub_total, currency = self.currency)
        overflows = discount > self.payable
        amount = self.payable if overflows else discount
        self.discount += amount
        self.vouchers.append(voucher)
        self.save()

    def set_voucher_s(self, voucher):
        appier.verify(voucher.is_valid(currency = self.currency))
        self.empty_vouchers_s()
        self.add_voucher_s(voucher)

    def empty_vouchers_s(self):
        self.vouchers = []
        self.discount = commons.Decimal(0.0)
        self.save()

    def refresh_vouchers_s(self):
        vouchers = self.vouchers
        self.empty_vouchers_s()
        for voucher in vouchers: self.add_voucher_s(voucher)

    def refresh_s(self, *args, **kwargs):
        if self.paid: return
        refreshed = bundle.Bundle.refresh_s(self, *args, **kwargs)
        if refreshed: self.refresh_vouchers_s()

    def verify_waiting_payment(self):
        appier.verify(not self.shipping_address == None)
        appier.verify(not self.billing_address == None)
        appier.verify(not self.email == None)
        appier.verify(not self.email == "")
        appier.verify(self.status == "created")
        appier.verify(self.paid == False)
        appier.verify(self.date == None)
        self.verify_vouchers()

    def verify_paid(self):
        appier.verify(not self.shipping_address == None)
        appier.verify(not self.billing_address == None)
        appier.verify(not self.email == None)
        appier.verify(not self.email == "")
        appier.verify(self.status == "waiting_payment")
        appier.verify(self.paid == False)
        appier.verify(self.date == None)
        self.verify_vouchers()

    def verify_sent(self):
        appier.verify(not self.date == None)
        appier.verify(self.status == "paid")
        appier.verify(self.paid == True)

    def verify_vouchers(self):
        pending = self.discount
        for voucher in self.vouchers:
            if pending == 0.0: break
            open_amount = voucher.open_amount_r(currency = self.currency)
            overflows = open_amount > pending
            amount = pending if overflows else pending
            result = voucher.is_valid(
                amount = amount,
                currency = self.currency
            )
            if not result: continue
            pending -= commons.Decimal(amount)
        appier.verify(pending == 0.0)

    def verify_account(self, account):
        appier.verify(not account == None)
        appier.verify(self.account.username == account.username)
        appier.verify(self.account.email == account.email)

    def wait_payment_s(self):
        self.verify_waiting_payment()
        self.mark_waiting_payment_s()

    def pay_s(
        self,
        payment_data,
        vouchers = True,
        notify = False,
        ensure_waiting = True
    ):
        if ensure_waiting: self.ensure_waiting_s()
        self.verify_paid()
        self._pay(payment_data)
        self.mark_paid_s()
        if vouchers: self.use_vouchers_s()
        if notify: self.notify_s()

    def use_vouchers_s(self):
        pending = self.discount
        for voucher in self.vouchers:
            if pending == 0.0: break
            discount = voucher.discount(
                self.sub_total,
                currency = self.currency
            )
            overflows = discount > pending
            amount = pending if overflows else discount
            voucher.use_s(amount, currency = self.currency)
            pending -= commons.Decimal(amount)
        appier.verify(pending == 0.0)

    def ensure_waiting_s(self):
        if not self.state == "created": return
        self.mark_waiting_payment_s()

    @appier.operation(name = "Notify")
    def notify_s(self, name = None):
        name = name or "order.%s" % self.status
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

    @appier.operation(name = "Mark Waiting Payment")
    def mark_waiting_payment_s(self):
        self.verify_waiting_payment()
        self.status = "waiting_payment"
        self.save()

    @appier.operation(name = "Mark Paid")
    def mark_paid_s(self):
        self.verify_paid()
        self.status = "paid"
        self.paid = True
        self.date = time.time()
        self.save()

    @appier.operation(name = "Unmark Paid")
    def unmark_paid_s(self):
        self.status = "waiting_payment"
        self.paid = False
        self.save()

    @appier.operation(name = "Mark Sent")
    def mark_sent_s(self):
        self.verify_sent()
        self.status = "sent"
        self.save()

    @appier.operation(name = "Garbage Collect")
    def collect_s(self):
        if self.paid: return
        self.delete()

    @appier.operation(
        name = "Set Tracking",
        parameters = (
            ("Tracking Number", "tracking_number", str),
            ("Tracking URL", "tracking_url", str)
        )
    )
    def set_tracking_s(self, tracking_number, tracking_url):
        if not tracking_number and not tracking_url: return
        self.tracking_number = tracking_number
        self.tracking_url = tracking_url
        self.save()

    @appier.operation(name = "Set Reference")
    def set_reference_s(self):
        prefix = appier.conf("BUDY_ORDER_REF", "BD-%06d")
        self.reference = prefix % self.id
        self.save()

    @appier.operation(name = "Fix Orphans")
    def fix_orphans_s(self):
        for line in self.lines:
            line.order = self
            line.save()

    @appier.operation(name = "Fix Shipping")
    def fix_shipping_s(self):
        if self.shipping_address: return
        if not self.store: return
        if not self.store.address: return
        address = self.store.address.clone()
        address.save()
        self.shipping_address = address
        self.save()

    @appier.operation(name = "Fix Store")
    def fix_store_s(self):
        if self.store: return
        if not self.account: return
        self.store = self.account.store
        self.save()

    @property
    def payable(self):
        return self.total

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

    @property
    def payment_currency(self):
        has_store_currency = self.store and self.store.currency_code
        if has_store_currency: return self.store.currency_code
        return self.shipping_currency

    def _pay(self, payment_data):
        if self.payable == 0.0: return
        self._pay_stripe(payment_data)

    def _pay_stripe(self, payment_data):
        import stripe
        api = stripe.Api()
        number = payment_data["card_number"]
        exp_month = int(payment_data["expiration_month"])
        exp_year = int(payment_data["expiration_year"])
        name = payment_data.get("card_name", None)
        api.create_charge(
            int(self.payable * 100),
            self.currency,
            exp_month,
            exp_year,
            number,
            name = name
        )
