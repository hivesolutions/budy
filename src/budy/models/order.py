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
from . import currency
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

    reference_f = appier.field(
        index = True,
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

    tracking_number = appier.field(
        index = True
    )

    tracking_url = appier.field(
        index = True,
        meta = "url"
    )

    payment_data = appier.field(
        type = dict
    )

    cancel_data = appier.field(
        type = dict
    )

    notifications = appier.field(
        type = list,
        index = True,
        initial = [],
        safe = True
    )

    discount_voucher = appier.field(
        type = commons.Decimal,
        index = True,
        initial = commons.Decimal(0.0),
        safe = True
    )

    discount_used = appier.field(
        type = commons.Decimal,
        index = True,
        initial = commons.Decimal(0.0),
        safe = True
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
    def setup(cls):
        super(Order, cls).setup()
        cls._get_api_easypay()

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

    @classmethod
    @appier.link(
        name = "Export CTT",
        parameters = (
            ("Start Id", "start", int),
            ("End Id", "end", int),
        )
    )
    def ctt_csv_url(cls, start = None, end = None, absolute = False):
        return appier.get_app().url_for(
            "order_api.ctt_csv",
            start = start,
            end = end,
            absolute = absolute
        )

    @classmethod
    def _pmethods(cls):
        methods = dict()
        for engine in ("stripe", "easypay", "paypal"):
            function = getattr(cls, "_pmethods_" + engine)
            engine_m = [(value, engine) for value in function()]
            methods.update(engine_m)
        return methods

    @classmethod
    def _pmethods_stripe(cls):
        return (
            "visa",
            "mastercard",
            "american_express"
        )

    @classmethod
    def _pmethods_easypay(cls):
        return ("multibanco",)

    @classmethod
    def _pmethods_paypal(cls):
        return ("paypal",)

    @classmethod
    def _get_api_stripe(cls):
        try: import stripe
        except: return None
        return stripe.Api.singleton()

    @classmethod
    def _get_api_easypay(cls):
        try: import easypay
        except: return None
        return easypay.ShelveApi.singleton(scallback = cls._on_api_easypay)

    @classmethod
    def _get_api_paypal(cls):
        try: import paypal
        except: return None
        return paypal.Api.singleton()

    @classmethod
    def _on_api_easypay(cls, api):
        api.bind("paid", cls._on_paid_easypay)
        api.bind("canceled", cls._on_canceled_easypay)
        api.start_scheduler()

    @classmethod
    def _on_paid_easypay(cls, reference, details):
        identifier = reference["identifier"]
        order = cls.get(key = identifier, raise_e = False)
        if order.is_payable(): order.end_pay_s(notify = True)

    @classmethod
    def _on_canceled_easypay(cls, reference):
        identifier = reference["identifier"]
        order = cls.get(key = identifier, raise_e = False)
        order.cancel_s(notify = True)

    def pre_delete(self):
        bundle.Bundle.pre_delete(self)
        for line in self.lines: line.delete()

    def post_create(self):
        bundle.Bundle.post_create(self)
        self.set_reference_s()

    def add_line_s(self, line):
        line.order = self
        return bundle.Bundle.add_line_s(self, line)

    def build_discount(self):
        join = appier.conf("BUDY_DISCOUNT_JOIN", True, cast = bool)
        base_discount = bundle.Bundle.build_discount(self)
        if join: return base_discount + self.discount_voucher
        if self.discount_voucher > base_discount: return self.discount_voucher
        return base_discount

    def set_account_s(self, account):
        self.verify_base()
        self.verify_open()
        self.account = account
        self.store = self.account.store
        self.save()

    def add_voucher_s(self, voucher):
        join = appier.conf("BUDY_DISCOUNT_JOIN", True, cast = bool)
        appier.verify(voucher.is_valid(currency = self.currency))
        discount = voucher.discount(self.discountable, currency = self.currency)
        base_discount = bundle.Bundle.build_discount(self)
        if not join and discount <= base_discount: return
        self.discount_voucher += discount
        self.vouchers.append(voucher)
        self.save()

    def set_voucher_s(self, voucher):
        appier.verify(voucher.is_valid(currency = self.currency))
        self.empty_vouchers_s()
        self.add_voucher_s(voucher)

    def empty_vouchers_s(self):
        self.vouchers = []
        self.discount_voucher = commons.Decimal(0.0)
        self.save()

    def refresh_vouchers_s(self):
        vouchers = self.vouchers
        self.empty_vouchers_s()
        for voucher in vouchers: self.add_voucher_s(voucher)

    def set_meta_s(self, name, value):
        self.meta[name] = value
        self.save()

    def refresh_s(self, *args, **kwargs):
        if self.paid: return
        refreshed = bundle.Bundle.refresh_s(self, *args, **kwargs)
        if refreshed: self.refresh_vouchers_s()

    def wait_payment_s(self, notify = False):
        self.verify_waiting_payment()
        self.mark_waiting_payment_s()
        if notify: self.notify_s()

    def pay_s(
        self,
        payment_data = {},
        vouchers = True,
        notify = False,
        ensure_waiting = True
    ):
        if ensure_waiting: self.ensure_waiting_s()
        self.verify_paid()
        result = self._pay(payment_data)
        confirmed = result == True
        self.save()
        if vouchers: self.use_vouchers_s()
        if confirmed: self.end_pay_s()
        if notify: self.notify_s()
        return result

    def end_pay_s(
        self,
        payment_data = {},
        strict = False,
        notify = False
    ):
        payment_data.update(self.payment_data)
        result = self._end_pay(payment_data, strict = strict)
        self.mark_paid_s()
        if notify: self.notify_s()
        return result

    def cancel_s(
        self,
        cancel_data = {},
        strict = False,
        notify = False
    ):
        cancel_data.update(self.cancel_data)
        result = self._cancel(cancel_data, strict = strict)
        self.mark_canceled_s()
        if notify: self.notify_s()
        return result

    def use_vouchers_s(self, reset = True):
        """
        Runs the use/redeem operation on the vouchers currently associated
        with the order, note that in case the reset flag is set the values
        already applied as discount to the order are reset meaning that even
        if (previous) vouchers have been discounted in the order they will
        be discarded as not relevant.

        @type reset: bool
        @param reset: If previous voucher discount values should be discarded
        before the use/redeem operation is performed.
        """

        discount = self.calculate_discount()
        if reset: self.discount_used = commons.Decimal(0.0)
        pending = discount - self.discount_base - self.discount_used
        if pending <= 0.0: return
        for voucher in self.vouchers:
            if pending == 0.0: break
            discount = voucher.discount(
                self.discountable,
                currency = self.currency
            )
            overflows = discount > pending
            amount = pending if overflows else discount
            voucher.use_s(amount, currency = self.currency)
            pending -= commons.Decimal(amount)
            self.discount_used += commons.Decimal(amount)
        appier.verify(pending == 0.0)
        self.save()

    def ensure_waiting_s(self):
        if not self.status == "created": return
        self.mark_waiting_payment_s()

    def get_paypal(self, return_url = None, cancel_url = None):
        items = []
        for line in self.lines:
            items.append(
                dict(
                    name = line.product.short_description,
                    price = currency.Currency.format(line.price, line.currency),
                    currency = line.currency,
                    quantity = line.quantity
                )
            )
        if self.discount: items.append(
            dict(
                name = "Discount",
                price = currency.Currency.format(self.discount * -1, self.currency),
                currency = self.currency,
                quantity = 1
            )
        )
        transaction = dict(
            item_list = dict(
                items = items,
                shipping_address = dict(
                    recipient_name = self.shipping_address.full_name,
                    line1 = self.shipping_address.address,
                    line2 = self.shipping_address.address_extra,
                    city = self.shipping_address.city,
                    country_code = self.shipping_address.country,
                    postal_code = self.shipping_address.postal_code,
                    state = self.shipping_address.state
                )
            ),
            amount = dict(
                total = currency.Currency.format(self.total, self.currency),
                currency = self.currency,
                details = dict(
                    subtotal = currency.Currency.format(self.sub_total - self.discount, self.currency),
                    shipping = currency.Currency.format(self.shipping_cost, self.currency)
                )
            ),
            soft_descriptor = self.reference
        )
        return dict(
            payer = dict(payment_method = "paypal"),
            transactions = [transaction],
            redirect_urls = dict(
                return_url = return_url,
                cancel_url = cancel_url
            )
        )

    def is_payable(self):
        if not self.status == "waiting_payment": return False
        if self.paid: return False
        if self.date: return False
        return True

    def verify_base(self):
        """
        Series of base verifications that define the basic integrity
        check for the order, if any of these rules fail the order
        is considered to be invalid under any scenario.
        """

        appier.verify(len(self.lines) > 0)

    def verify_open(self):
        """
        Verifies that the current order is considered open,
        meaning that the it is still under the checkout stage.
        """

        appier.verify(self.status == "created")
        appier.verify(self.paid == False)

    def verify_shippable(self):
        appier.verify(not self.shipping_address == None)
        appier.verify(not self.billing_address == None)
        appier.verify(not self.email == None)
        appier.verify(not self.email == "")

    def verify_waiting_payment(self):
        self.verify_base()
        self.verify_shippable()
        appier.verify(self.status == "created")
        appier.verify(self.paid == False)
        appier.verify(self.date == None)
        self.verify_vouchers()

    def verify_paid(self):
        self.verify_base()
        self.verify_shippable()
        appier.verify(self.status == "waiting_payment")
        appier.verify(self.paid == False)
        appier.verify(self.date == None)
        self.verify_vouchers()

    def verify_sent(self):
        self.verify_base()
        self.verify_shippable()
        appier.verify(self.status == "paid")
        appier.verify(self.paid == True)
        appier.verify(not self.date == None)

    def verify_canceled(self):
        self.verify_base()
        appier.verify(not self.status in ("created", "canceled", "received"))

    def verify_vouchers(self):
        discount = self.calculate_discount()
        pending = discount - self.discount_base - self.discount_used
        if pending <= 0.0: return
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

    @appier.operation(name = "Notify")
    def notify_s(self, name = None, *args, **kwargs):
        name = name or "order.%s" % self.status
        order = self.reload(map = True)
        receiver = order.get("email", None)
        receiver = kwargs.get("email", receiver)
        appier_extras.admin.Event.notify_g(
            name,
            arguments = dict(
                params = dict(
                    payload = order,
                    order = order,
                    receiver = receiver,
                    extra = kwargs
                )
            )
        )
        exists = name in self.notifications
        if not exists: self.notifications.append(name)
        self.save()

    @appier.operation(name = "Mark Waiting Payment")
    def mark_waiting_payment_s(self):
        self.verify_waiting_payment()
        self.status = "waiting_payment"
        self.set_reference_f_s()
        self.save()

    @appier.operation(name = "Mark Paid")
    def mark_paid_s(self):
        self.verify_paid()
        self.status = "paid"
        self.paid = True
        self.date = time.time()
        self.set_reference_f_s()
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

    @appier.operation(name = "Mark Canceled")
    def mark_canceled_s(self):
        self.verify_canceled()
        self.status = "canceled"
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
    def set_reference_s(self, force = False):
        if self.reference and not force: return
        prefix = appier.conf("BUDY_ORDER_REF", "BD-%06d")
        self.reference = prefix % self.id
        self.save()

    @appier.operation(name = "Set Reference Final")
    def set_reference_f_s(self, force = False):
        if self.reference_f and not force: return
        cls = self.__class__
        prefix = appier.conf("BUDY_ORDER_REF_F", "BDF-%06d")
        self.reference_f = prefix % cls._increment("reference_f")
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

    @appier.link(name = "Export Lines CSV")
    def lines_csv_url(self, absolute = False):
        return appier.get_app().url_for(
            "order_api.lines_csv",
            key = self.key,
            absolute = absolute
        )

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
        currency = appier.conf("BUDY_CURRENCY", None)
        if currency: return currency
        if not self.shipping_country: return None
        shipping_country = country.Country.get_by_code(self.shipping_country)
        return shipping_country.currency_code

    @property
    def payment_currency(self):
        currency = appier.conf("BUDY_CURRENCY", None)
        if currency: return currency
        has_store_currency = self.store and self.store.currency_code
        if has_store_currency: return self.store.currency_code
        return self.shipping_currency

    def _pay(self, payment_data):
        cls = self.__class__
        if self.payable == 0.0: return True
        methods = cls._pmethods()
        type = payment_data.get("type", None)
        method = methods.get(type, None)
        if not method: return
        function = getattr(self, "_pay_" + method)
        return function(payment_data)

    def _pay_stripe(self, payment_data):
        cls = self.__class__
        api = cls._get_api_stripe()
        type = payment_data["type"]
        number = payment_data["card_number"]
        exp_month = int(payment_data["expiration_month"])
        exp_year = int(payment_data["expiration_year"])
        cvc = payment_data.get("security_code", None)
        name = payment_data.get("card_name", None)
        if number: number = number.replace(" ", "")
        if cvc: cvc = cvc.replace(" ", "")
        if name: name = name.strip()
        api.create_charge(
            int(self.payable * 100),
            self.currency,
            exp_month,
            exp_year,
            number,
            cvc = cvc,
            name = name,
            description = self.reference,
            address_country = self.shipping_address.country,
            address_city = self.shipping_address.city,
            address_zip = self.shipping_address.postal_code,
            address_line1 = self.shipping_address.address,
            address_line2 = self.shipping_address.address_extra,
            metadata = dict(
                order = self.reference,
                email = self.email,
                ip_address = self.ip_address,
                ip_country = self.ip_country,
                first_name = self.shipping_address.first_name,
                last_name = self.shipping_address.last_name
            )
        )
        self.payment_data = dict(
            engine = "stripe",
            type = type,
            number = "*" * 12 + number[-4:],
            exp_month = exp_month,
            exp_year = exp_year
        )
        return True

    def _pay_easypay(self, payment_data, warning_d = 172800, cancel_d = 259200):
        cls = self.__class__
        api = cls._get_api_easypay()
        type = payment_data["type"]
        mb = api.generate_mb(
            self.payable,
            key = self.key,
            warning = int(time.time() + warning_d) if warning_d else None,
            cancel = int(time.time() + cancel_d) if cancel_d else None
        )
        entity = mb["entity"]
        reference = mb["reference"]
        cin = mb["cin"]
        identifier = mb["identifier"]
        warning = mb["warning"]
        cancel = mb["cancel"]
        self.payment_data = dict(
            engine = "easypay",
            type = type,
            entity = entity,
            reference = reference,
            cin = cin,
            identifier = identifier,
            warning = warning,
            cancel = cancel
        )
        return False

    def _pay_paypal(self, payment_data):
        cls = self.__class__
        api = cls._get_api_paypal()
        return_url = payment_data.get("return_url", None)
        cancel_url = payment_data.get("cancel_url", None)
        paypal_order = self.get_paypal(
            return_url = return_url,
            cancel_url = cancel_url
        )
        payment = api.create_payment(**paypal_order)
        payment_id = payment["id"]
        approval_url = api.get_url(payment["links"], "approval_url")
        self.payment_data = dict(
            engine = "paypal",
            type = "paypal",
            payment_id = payment_id,
            approval_url = approval_url
        )
        return approval_url

    def _end_pay(self, payment_data, strict = False):
        cls = self.__class__
        if self.payable == 0.0: return
        methods = cls._pmethods()
        type = payment_data.get("engine", None)
        type = payment_data.get("type", type)
        method = methods.get(type, type)
        has_function = hasattr(self, "_end_pay_" + method)
        if not has_function and not strict: return
        function = getattr(self, "_end_pay_" + method)
        return function(payment_data)

    def _end_pay_paypal(self, payment_data):
        cls = self.__class__
        api = cls._get_api_paypal()
        payment_id = payment_data["payment_id"]
        payer_id = payment_data["payer_id"]
        api.execute_payment(payment_id, payer_id)
        return True

    def _cancel(self, cancel_data, strict = False):
        cls = self.__class__
        if self.payable == 0.0: return
        methods = cls._pmethods()
        type = cancel_data.get("engine", None)
        type = cancel_data.get("type", type)
        method = methods.get(type, type)
        if not method: return
        has_function = hasattr(self, "_cancel_" + method)
        if not has_function and not strict: return
        function = getattr(self, "_cancel_" + method)
        return function(cancel_data)
