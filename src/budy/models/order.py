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

import time
import uuid
import commons

import appier
import appier_extras

from . import bundle
from . import product
from . import country
from . import voucher
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
        canceled = "canceled",
        completed = "completed"
    )

    STATUS_C = dict(
        created = "grey",
        waiting_payment = "orange",
        paid = "purple",
        sent = "blue",
        received = "green",
        returned = "red",
        canceled = "red",
        completed = "green"
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
        index = "hashed",
        default = True,
        safe = True
    )

    reference_f = appier.field(
        index = "hashed",
        safe = True
    )

    paid = appier.field(
        type = bool,
        index = "hashed",
        initial = False,
        safe = True
    )

    date = appier.field(
        type = int,
        index = True,
        safe = True,
        meta = "datetime"
    )

    delivery_date = appier.field(
        type = int,
        index = True,
        safe = True,
        meta = "datetime"
    )

    email = appier.field(
        index = "hashed",
        safe = True
    )

    gift_wrap = appier.field(
        type = bool,
        index = "hashed",
        initial = False,
        safe = True
    )

    tracking_number = appier.field(
        index = "hashed",
    )

    tracking_url = appier.field(
        index = "hashed",
        meta = "url",
        description = "Tracking URL"
    )

    payment_data = appier.field(
        type = dict
    )

    cancel_data = appier.field(
        type = dict
    )

    discount_data = appier.field(
        type = dict
    )

    notifications = appier.field(
        type = list,
        initial = [],
        safe = True
    )

    discount_voucher = appier.field(
        type = commons.Decimal,
        index = "hashed",
        initial = commons.Decimal(0.0),
        safe = True,
        observations = """The discount value that is related with
        the vouchers to be redeemed (or already redeemed) for the
        current order"""
    )

    discount_used = appier.field(
        type = commons.Decimal,
        index = "hashed",
        initial = commons.Decimal(0.0),
        safe = True,
        observations = """The total value already used via the
        redeeming of the vouchers associated with the current order"""
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

    @classmethod
    def setup(cls):
        super(Order, cls).setup()
        cls._get_api_easypay()

    @classmethod
    def list_names(cls):
        return ["reference", "total", "currency", "email", "created", "status"]

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
            ("Start ID", "start", int),
            ("End ID", "end", int)
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
            ("Start ID", "start", int),
            ("End ID", "end", int)
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
    @appier.link(name = "Export CTT Context", context = True)
    def ctt_csv_context_url(cls, view = None, context = None, absolute = False):
        return appier.get_app().url_for(
            "order_api.ctt_csv",
            view = view,
            context = context,
            absolute = absolute
        )

    @classmethod
    @appier.operation(
        name = "Import CTT",
        parameters = (
            ("CSV File", "file", "file"),
            ("Base URL", "base_url", str, "http://www.ctt.pt/feapl_2/app/open/cttexpresso/objectSearch/objectSearch.jspx?objects=%s"),
            ("Force", "force", bool, False)
        )
    )
    def import_ctt_csv_s(cls, file, base_url, force):

        def callback(line):
            _date,\
            _ctt_ref,\
            _ctt_id,\
            reference,\
            tracking_number,\
            _quantity,\
            _customer,\
            _weight,\
            _price = line

            order = cls.get(reference = reference, raise_e = False)
            if not order: return
            if not force and order.tracking_number: return
            if not force and order.tracking_url: return

            order.set_tracking_s(
                tracking_number,
                base_url % tracking_number
            )

        cls._csv_import(
            file,
            callback,
            header = False,
            delimiter = "+",
            encoding = "Cp1252"
        )

    @classmethod
    @appier.operation(
        name = "Generate Dummy",
        parameters = (
            ("Product Description", "short_description", str, "product"),
            ("Product Gender", "gender", str, "Male"),
            ("Product Price", "price", float, 10.0),
            ("Quantity", "quantity", float, 1.0),
            ("Set Account", "set_account", bool, True)
        ),
        devel = True
    )
    def generate_dummy_s(
        cls,
        short_description = "product",
        gender = "Male",
        price = 10.0,
        quantity = 1.0,
        set_account = True
    ):
        _product = product.Product(
            short_description = short_description,
            gender = gender,
            price = price
        )
        _product.save()

        order = cls()
        order.save()

        _order_line = order_line.OrderLine(quantity = quantity)
        _order_line.product = _product
        _order_line.save()
        order.add_line_s(_order_line)

        if not set_account: return

        from . import account

        username = str(uuid.uuid4())
        email = "%s@account.com" % username

        _account = account.BudyAccount(
            username = username,
            email = email,
            password = "password",
            password_confirm = "password"
        )
        _account.save()

        order.set_account_s(_account)

    @classmethod
    @appier.operation(
        name = "Multiple Dummy",
        parameters = (
            ("Quantity", "quantity", int, 10),
        ),
        devel = True
    )
    def multiple_dummy_s(cls, quantity):
        for _index in range(quantity): cls.generate_dummy_s()

    @classmethod
    @appier.view(name = "Paid")
    def paid_v(cls, *args, **kwargs):
        kwargs["sort"] = kwargs.get("sort", [("id", -1)])
        kwargs.update(paid = True)
        return appier.lazy_dict(
            model = cls,
            kwargs = kwargs,
            entities = appier.lazy(lambda: cls.find(*args, **kwargs)),
            page = appier.lazy(lambda: cls.paginate(*args, **kwargs))
        )

    @classmethod
    @appier.view(
        name = "Status",
        parameters = (
            ("Status", "status", str, "paid"),
        )
    )
    def status_v(cls, status, *args, **kwargs):
        kwargs["sort"] = kwargs.get("sort", [("id", -1)])
        kwargs.update(status = status)
        return appier.lazy_dict(
            model = cls,
            kwargs = kwargs,
            entities = appier.lazy(lambda: cls.find(*args, **kwargs)),
            page = appier.lazy(lambda: cls.paginate(*args, **kwargs))
        )

    @classmethod
    def _pmethods(cls):
        methods = dict()
        for engine in ("stripe", "easypay", "paypal", "stripe_sca"):
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
    def _pmethods_stripe_sca(cls):
        return ("stripe_sca",)

    @classmethod
    def _get_api_stripe(cls):
        try: import stripe
        except ImportError: return None
        return stripe.API.singleton()

    @classmethod
    def _get_api_easypay(cls):
        try: import easypay
        except ImportError: return None
        return easypay.ShelveAPI.singleton(scallback = cls._on_api_easypay)

    @classmethod
    def _get_api_paypal(cls):
        try: import paypal
        except ImportError: return None
        return paypal.API.singleton()

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

    def pre_validate(self):
        bundle.Bundle.pre_validate(self)
        if self.is_open(): self.try_valid()

    def pre_delete(self):
        bundle.Bundle.pre_delete(self)
        for line in self.lines: line.delete()

    def post_create(self):
        bundle.Bundle.post_create(self)
        self.set_reference_s()

    def add_line_s(self, line):
        line.order = self
        return bundle.Bundle.add_line_s(self, line)

    def is_valid(self):
        # in case the current status of the current order is the
        # first one (created) the order is considered to be open
        # and so the validation process must occur
        if self.is_open(): return bundle.Bundle.is_valid(self)

        # returns the true value on all other cases as the order lines
        # are considered to be valid at all times and don't require
        # constant validation (inventory snapshot frozen)
        return True

    def build_discount(self):
        join = appier.conf("BUDY_JOIN_DISCOUNT", True, cast = bool)
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
        join = appier.conf("BUDY_JOIN_DISCOUNT", True, cast = bool)
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
        payment_data = None,
        vouchers = True,
        strict = True,
        notify = False,
        ensure_waiting = True
    ):
        payment_data = payment_data or dict()
        if ensure_waiting: self.ensure_waiting_s()
        self.verify_paid()
        result = self._pay(payment_data, strict = strict)
        confirmed = result == True
        self.save()
        if vouchers: self.use_vouchers_s()
        if confirmed: self.end_pay_s()
        if notify: self.notify_s()
        return result

    def end_pay_s(
        self,
        payment_data = None,
        strict = False,
        notify = False
    ):
        # joins the payment data passed as parameter and then
        # one currently stored as part of the order, these
        # values are going to be sent for the end pay operation
        payment_data = payment_data or dict()
        payment_data.update(self.payment_data)

        # runs the concrete implementation of the end payment
        # (finish payment) operation return a valid value in case
        # a concrete operation has been executed or an invalid
        # value in case nothing has been done
        result = self._end_pay(payment_data, strict = strict)

        # marks the current order as completely paid and in case
        # the notify flag is set notifies the event handlers
        self.mark_paid_s()
        if notify: self.notify_s()

        # returns the result value from the end pay operation to
        # the caller method (for post-processing)
        return result

    def cancel_s(
        self,
        cancel_data = None,
        vouchers = True,
        strict = False,
        notify = False
    ):
        cancel_data = cancel_data or dict()
        cancel_data.update(self.cancel_data)
        result = self._cancel(cancel_data, strict = strict)
        self.mark_canceled_s()
        if vouchers: self.disuse_vouchers_s()
        if notify: self.notify_s()
        return result

    def use_vouchers_s(self, reset = True):
        """
        Runs the use/redeem operation on the vouchers currently associated
        with the order, note that in case the reset flag is set the values
        already applied as discount to the order are reset meaning that even
        if (previous) vouchers have been discounted in the order they will
        be discarded as not relevant.

        :type reset: bool
        :param reset: If previous voucher discount values should be discarded
        before the use/redeem operation is performed.
        """

        # in case the reset flag is set then resets both the discount
        # used count and the discount data (meta-information)
        if reset:
            self.discount_used = commons.Decimal(0.0)
            self.discount_data = dict()

        # calculates the total amount of order value pending to be passive
        # of being discount and in case the value is already lower or equal
        # to zero there's no need to redeem any voucher, as the order total
        # value is already zero
        discount = self.calculate_discount()
        pending = discount - self.discount_base - self.discount_used
        if pending <= 0.0: return

        # iterates over the complete set of vouchers currently associated
        # with the order (both value and percentage) to try to retrieve
        # the possible discount value for each of them
        for voucher in self.vouchers:
            # in case there's no more discount pending/allowed to be
            # applied breaks the current loop (no more usage allowed)
            if pending == 0.0: break

            # retrieves the "possible" discount value from the voucher
            # according to the order's currency (this value may be calculated
            # as a percentage of the discountable value or a fixed value
            # depending on the nature of the voucher, value vs percentage)
            discount = voucher.discount(
                self.discountable,
                currency = self.currency
            )

            # determines the concrete amount of discount to be used by
            # comparing it with the pending value (lowest wins)
            amount = min(discount, pending)

            # runs the concrete voucher usage operation taking into account
            # the "target" discount amount and the currency and decrements
            # the pending value by the amount one
            voucher.use_s(amount, currency = self.currency)
            pending -= commons.Decimal(amount)

            # updates the discount used and the discount data value according
            # to the new voucher usage operation that has just been executed
            self.discount_used += commons.Decimal(amount)
            self.discount_data[str(voucher.id)] = amount

        # verifies that there's no more pending value to be discounted and
        # then save the current order values
        appier.verify(pending == 0.0)
        self.save()

    def disuse_vouchers_s(self, force = False):
        """
        Disuses the complete set of voucher associated with the current
        order, note that only vouchers set in the discount data will be
        used. This map is typically populated once the order is marked
        as waiting payment.

        :type force: bool
        :param force: If the disuse operation should be forced meaning
        that even if the order is paid the disuse will proceed.
        """

        # in case the order is already paid and the force flag is not
        # set the disuse of the voucher is skipped, otherwise it would
        # "return vouchers" for an already paid order
        if self.paid and not force: return

        # in case the discount data is not valid there's no voucher
        # value to be reverted/disused, should return immediately
        if not self.discount_data: return

        # iterates over the complete set of vouchers and associated amount
        # to disuse the associated amount in the related vouchers
        for voucher_id, amount in appier.legacy.items(self.discount_data):
            voucher_id = int(voucher_id)
            _voucher = voucher.Voucher.get(id = voucher_id)
            _voucher.disuse_s(amount, currency = self.currency)

    def ensure_waiting_s(self):
        if not self.status == "created": return
        self.mark_waiting_payment_s()

    def close_lines_s(self):
        for line in self.lines: line.close_s()

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
        if not self.status in ("waiting_payment",): return False
        if self.paid: return False
        if self.date: return False
        return True

    def is_open(self):
        if not self.status in ("created",): return False
        if self.paid: return False
        return True

    def is_closed(self):
        return not self.is_open()

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

    def verify_received(self):
        self.verify_base()
        self.verify_shippable()
        appier.verify(self.status == "sent")
        appier.verify(self.paid == True)
        appier.verify(not self.date == None)

    def verify_canceled(self):
        self.verify_base()
        appier.verify(not self.status in ("created", "canceled", "received", "completed"))

    def verify_completed(self):
        self.verify_base()
        appier.verify(self.status in ("paid", "sent", "received"))

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

    def verify_store(self):
        """
        Verifies that the store associated with the order contains
        all the required fields for proper handling.

        The raised exception should contain proper english messages.
        """

        appier.verify(
            not self.store == None,
            message = "No store is set for order"
        )
        appier.verify(
            not self.store.address == None,
            message = "Address is not set for order's store"
        )

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

    @appier.operation(name = "Mark Received")
    def mark_received_s(self):
        self.verify_received()
        self.status = "received"
        self.save()

    @appier.operation(name = "Mark Canceled")
    def mark_canceled_s(self):
        self.verify_canceled()
        self.status = "canceled"
        self.save()

    @appier.operation(name = "Mark Completed")
    def mark_completed_s(self):
        self.verify_completed()
        self.status = "completed"
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

    @appier.operation(name = "Fix Closed Lines")
    def fix_closed_s(self):
        if not self.is_closed(): return
        self.close_lines_s()

    @appier.link(name = "Export Lines CSV")
    def lines_csv_url(self, absolute = False):
        return appier.get_app().url_for(
            "order_api.lines_csv",
            key = self.key,
            absolute = absolute
        )

    @appier.view(name = "Lines")
    def lines_v(self, *args, **kwargs):
        return appier.lazy_dict(
            model = self.lines._target,
            kwargs = kwargs,
            entities = appier.lazy(lambda: self.lines.find(*args, **kwargs)),
            page = appier.lazy(lambda: self.lines.paginate(*args, **kwargs)),
            names = [
                "id",
                "product.product_id",
                "product",
                "size_s",
                "quantity",
                "total",
                "currency"
            ]
        )

    @appier.view(
        name = "Lines Currency",
        parameters = (
            ("Currency", "currency", str, "EUR"),
        )
    )
    def lines_currency_v(self, currency, *args, **kwargs):
        kwargs.update(currency = currency)
        return appier.lazy_dict(
            model = self.lines._target,
            kwargs = kwargs,
            entities = appier.lazy(lambda: self.lines.find(*args, **kwargs)),
            page = appier.lazy(lambda: self.lines.paginate(*args, **kwargs)),
            names = ["id", "product", "quantity", "total", "currency"]
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

    def _pay(self, payment_data, strict = True):
        cls = self.__class__
        if self.payable == 0.0: return True
        methods = cls._pmethods()
        type = payment_data.get("type", None)
        method = methods.get(type, type)
        if not method: raise appier.SecurityError(
            message = "No payment method defined"
        )
        has_function = hasattr(self, "_pay_" + method)
        if not has_function and not strict: return
        if not has_function: raise appier.SecurityError(
            message = "Invalid payment method"
        )
        function = getattr(self, "_pay_" + method)
        return function(payment_data)

    def _pay_stripe(self, payment_data):
        cls = self.__class__
        api = cls._get_api_stripe()

        stripe_legacy = appier.conf("BUDY_STRIPE_LEGACY", False, cast = bool)
        three_d_enable = appier.conf("BUDY_3D_SECURE", False, cast = bool)
        three_d_ensure = appier.conf("BUDY_3D_ENSURE", False, cast = bool)

        type = payment_data["type"]
        number = payment_data["card_number"]
        exp_month = int(payment_data["expiration_month"])
        exp_year = int(payment_data["expiration_year"])
        cvc = payment_data.get("security_code", None)
        name = payment_data.get("card_name", None)
        return_url = payment_data.get("return_url", None)
        return_url = payment_data.get("stripe_return_url", return_url)
        if number: number = number.replace(" ", "")
        if cvc: cvc = cvc.replace(" ", "")
        if name: name = name.strip()

        token = api.create_token(
            exp_month,
            exp_year,
            number,
            cvc = cvc,
            name = name,
            address_country = self.shipping_address.country,
            address_city = self.shipping_address.city,
            address_zip = self.shipping_address.postal_code,
            address_line1 = self.shipping_address.address,
            address_line2 = self.shipping_address.address_extra
        )

        token_id = token["id"]
        card = token.get("card", {})
        three_d_secure = card.get("three_d_secure", {})
        secure_supported = three_d_secure.get("supported", None)

        use_secure = three_d_enable
        use_secure &= secure_supported in ("required", "optional")

        if use_secure:
            if stripe_legacy:
                secure = api.create_3d_secure(
                    int(self.payable * 100),
                    self.currency,
                    return_url,
                    token_id
                )
                redirect = secure.get("redirect_url", None)
            else:
                source = api.create_card_source(
                    exp_month,
                    exp_year,
                    number,
                    cvc = cvc,
                    name = name,
                    address_country = self.shipping_address.country,
                    address_city = self.shipping_address.city,
                    address_zip = self.shipping_address.postal_code,
                    address_line1 = self.shipping_address.address,
                    address_line2 = self.shipping_address.address_extra
                )
                source = api.create_3d_secure_source(
                    int(self.payable * 100),
                    self.currency,
                    return_url,
                    card = source["id"]
                )
                redirect = source.get("redirect", {})
                redirect_u = redirect.get("url", None)
                redirect_s = redirect.get("status", "pending")
                redirect = None if redirect_s == "failed" else redirect_u

            redirect_valid = True if redirect else False
            use_secure &= redirect_valid

        if use_secure:
            if stripe_legacy:
                redirect_url = appier.get_app().url_for(
                    "stripe.redirect",
                    redirect_url = redirect,
                    absolute = True
                )
            else:
                redirect_url = redirect

            self.payment_data = dict(
                engine = "stripe",
                type = type,
                number = "*" * 12 + number[-4:],
                exp_month = exp_month,
                exp_year = exp_year,
                token = token_id,
                redirect = redirect,
                redirect_url = redirect_url,
                secure = True
            )

            return redirect_url
        else:
            if three_d_ensure: raise appier.SecurityError(
                message = "No 3-D Secure enabled for provided card"
            )

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
                exp_year = exp_year,
                token = token_id,
                secure = False
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
        return_url = payment_data.get("paypal_return_url", return_url)
        cancel_url = payment_data.get("cancel_url", None)
        cancel_url = payment_data.get("paypal_cancel_url", cancel_url)
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

    def _pay_stripe_sca(self, payment_data):
        cls = self.__class__
        api = cls._get_api_stripe()
        pay_url = payment_data.get("pay_url", None)
        pay_url = payment_data.get("stripe_sca_pay_url", pay_url)
        return_url = payment_data.get("return_url", None)
        return_url = payment_data.get("stripe_sca_return_url", return_url)
        intent = api.create_intent(
            int(self.payable * 100),
            self.currency,
            description = self.reference,
            metadata = dict(
                order = self.reference,
                email = self.email,
                ip_address = self.ip_address,
                ip_country = self.ip_country,
                first_name = self.shipping_address.first_name,
                last_name = self.shipping_address.last_name
            )
        )
        identifier = intent["id"]
        secret = intent["client_secret"]
        query = "secret=%s&return_url=%s" % (
            appier.quote(secret),
            appier.quote(return_url)
        )
        pay_secret_url = pay_url + ("&" if "?" in pay_url else "?") + query
        self.payment_data = dict(
            engine = "stripe_sca",
            type = "stripe_sca",
            identifier = identifier,
            secret = secret,
            pay_url = pay_url,
            return_url = return_url,
            pay_secret_url = pay_secret_url
        )
        return pay_secret_url

    def _end_pay(self, payment_data, strict = False):
        cls = self.__class__
        if self.payable == 0.0: return
        methods = cls._pmethods()
        type = payment_data.get("engine", None)
        type = payment_data.get("type", type)
        method = methods.get(type, type)
        if not method: raise appier.SecurityError(
            message = "No payment method defined"
        )
        has_function = hasattr(self, "_end_pay_" + method)
        if not has_function and not strict: return
        if not has_function: raise appier.SecurityError(
            message = "Invalid payment method"
        )
        function = getattr(self, "_end_pay_" + method)
        return function(payment_data)

    def _end_pay_stripe(self, payment_data):
        cls = self.__class__

        # retrieves the reference to the Stripe API client
        # to be used for remote operations
        api = cls._get_api_stripe()

        # retrieves the payment data values that are going to be
        # used to complete the Stripe payment work-flow
        secure = payment_data.get("secure", False)
        token_return = payment_data.get("token_return", None)

        # in case the current payment stream is not the (3D) secure
        # one then returns immediately
        if not secure: return

        # tries to obtain the source associated with the return
        # so that the proper course of action may be taken
        source = api.get_source(token_return)
        status = source.get("status", "success")

        # in case the current status of the source is failed then
        # the cancel operation is run instead to cancel the current
        # order and a security exception is raised for the failure
        if status == "failed":
            self.cancel_s(notify = True)
            raise appier.SecurityError(
                message = "Security verification failed"
            )

        # (otherwise) runs the charging operation using the token
        # for the source as the source is considered to be valid
        api.create_charge_token(
            int(self.payable * 100),
            self.currency,
            token_return,
            description = self.reference,
            metadata = dict(
                order = self.reference,
                email = self.email,
                ip_address = self.ip_address,
                ip_country = self.ip_country,
                first_name = self.shipping_address.first_name,
                last_name = self.shipping_address.last_name
            )
        )

        # returns a valid value to the caller method indicating that
        # the end pay operation has been completed with success
        return True

    def _end_pay_paypal(self, payment_data):
        cls = self.__class__
        api = cls._get_api_paypal()
        payment_id = payment_data["payment_id"]
        payer_id = payment_data["payer_id"]
        api.execute_payment(payment_id, payer_id)
        return True

    def _end_pay_stripe_sca(self, payment_data):
        cls = self.__class__
        api = cls._get_api_stripe()
        identifier = payment_data["identifier"]
        token = payment_data.get("token", None)
        if token:
            api.create_charge_token(
                int(self.payable * 100),
                self.currency,
                token,
                description = self.reference,
                metadata = dict(
                    order = self.reference,
                    email = self.email,
                    ip_address = self.ip_address,
                    ip_country = self.ip_country,
                    first_name = self.shipping_address.first_name,
                    last_name = self.shipping_address.last_name
                )
            )
        else:
            charges = api.list_charges(
                payment_intent = identifier,
                limit = 1
            )
            items = charges.get("data", [])
            appier.verify(
                items,
                message = "No valid charge found"
            )
            charge = items[0]
            appier.verify(
                charge.get("status", "succeeded"),
                message = "Charge was not successful"
            )
            appier.verify(
                charge.get("captured", False),
                message = "Charge was not captured"
            )
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
