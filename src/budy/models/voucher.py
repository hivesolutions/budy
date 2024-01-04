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

import time
import commons

import appier
import appier_extras

from . import base


class Voucher(base.BudyBase):
    key = appier.field(index=True, safe=True, immutable=True)

    amount = appier.field(
        type=commons.Decimal,
        index=True,
        initial=commons.Decimal(0.0),
        safe=True,
        immutable=True,
    )

    used_amount = appier.field(
        type=commons.Decimal, initial=commons.Decimal(0.0), index=True, safe=True
    )

    percentage = appier.field(
        type=commons.Decimal,
        initial=commons.Decimal(0.0),
        index=True,
        safe=True,
        immutable=True,
    )

    currency = appier.field(
        index=True,
        safe=True,
        observations="""The base currency to be used for
        the voucher, usage of the voucher under other currency
        will be performed using proper exchange rate conversion""",
    )

    start = appier.field(type=int, index=True, safe=True, meta="datetime")

    expiration = appier.field(type=int, index=True, safe=True, meta="datetime")

    usage_count = appier.field(
        type=int,
        initial=0,
        index=True,
        safe=True,
        observations="""The number of time the voucher has
        already been used, if this value reached the usage limit
        the voucher is marked as used and no further usages are
        possible""",
    )

    usage_limit = appier.field(
        type=int,
        initial=0,
        index=True,
        safe=True,
        observations="""The maximum number of usages of the
        voucher before it's considered invalid, if the number
        is set to zero the voucher is considered to have no
        limit in the number of usages""",
    )

    unlimited = appier.field(
        type=bool,
        initial=False,
        index=True,
        safe=True,
        observations="""Flag that indicated if the value based
        voucher should not have its used amount deducted and instead
        be considered an unlimited voucher""",
    )

    used = appier.field(
        type=bool,
        initial=False,
        index=True,
        safe=True,
        observations="""Calculated value used to determine if
        the voucher is already used and should not be used anymore
        under any circumstance""",
    )

    @classmethod
    def validate(cls):
        return super(Voucher, cls).validate() + [
            appier.not_empty("key"),
            appier.not_duplicate("key", cls._name()),
            appier.not_null("amount"),
            appier.gte("amount", 0.0),
            appier.not_null("used_amount"),
            appier.gte("used_amount", 0.0),
            appier.not_null("percentage"),
            appier.gte("percentage", 0.0),
            appier.lte("percentage", 100.0),
            appier.not_null("usage_count"),
            appier.gte("usage_count", 0),
            appier.not_null("usage_limit"),
            appier.gte("usage_limit", 0),
            appier.not_null("unlimited"),
            appier.not_null("used"),
        ]

    @classmethod
    def list_names(cls):
        return [
            "description",
            "created",
            "amount",
            "percentage",
            "start",
            "expiration",
            "used",
        ]

    @classmethod
    def order_name(cls):
        return ["id", -1]

    @classmethod
    def is_snapshot(cls):
        return True

    @classmethod
    @appier.operation(
        name="Create Value",
        parameters=(
            ("Key", "key", str),
            ("Amount", "amount", commons.Decimal),
            ("Currency", "currency", str),
            ("Unlimited", "unlimited", bool, False),
        ),
        factory=True,
    )
    def create_value_s(cls, key, amount, currency, unlimited):
        voucher = cls(key=key, amount=amount, currency=currency, unlimited=unlimited)
        voucher.save()
        return voucher

    @classmethod
    @appier.operation(
        name="Create Value Multiple",
        parameters=(
            ("Key", "key", str),
            ("Amount", "amount", commons.Decimal),
            ("Currency", "currency", str),
            ("Unlimited", "unlimited", bool, False),
            ("Count", "count", int, 1),
        ),
    )
    def create_value_multiple_s(cls, key, amount, currency, unlimited, count):
        key = key or cls.secret_g()
        for index in appier.legacy.xrange(count):
            voucher = cls(
                key=key + "-" + str(index),
                amount=amount,
                currency=currency,
                unlimited=unlimited,
            )
            voucher.save()

    @classmethod
    @appier.operation(
        name="Create Percentage",
        parameters=(("Key", "key", str), ("Percentage", "percentage", commons.Decimal)),
        factory=True,
    )
    def create_percentage_s(cls, key, percentage):
        voucher = cls(key=key, percentage=percentage)
        voucher.save()
        return voucher

    @classmethod
    @appier.operation(
        name="Create Percentage Multiple",
        parameters=(
            ("Key", "key", str),
            ("Percentage", "percentage", commons.Decimal),
            ("Count", "count", int, 1),
        ),
    )
    def create_percentage_multiple_s(cls, key, percentage, count):
        key = key or cls.secret_g()
        for index in appier.legacy.xrange(count):
            voucher = cls(key=key + "-" + str(index), percentage=percentage)
            voucher.save()

    def pre_create(self):
        base.BudyBase.pre_create(self)
        if not hasattr(self, "key") or not self.key:
            self.key = self.secret()
        self.description = self.key[:8]

    def pre_update(self):
        base.BudyBase.pre_update(self)
        if not self.used and self.is_used():
            self.used = True
        if self.used and not self.is_used():
            self.used = False

    def use_s(self, amount, currency=None):
        amount_l = self.to_local(amount, currency)
        appier.verify(self.is_valid(amount=amount, currency=currency))
        if self.is_value and not self.unlimited:
            self.used_amount += commons.Decimal(amount_l)
        self.usage_count += 1
        self.save()

    def disuse_s(self, amount, currency=None):
        appier.verify(self.usage_count > 0)
        amount_l = self.to_local(amount, currency)
        if self.is_value and not self.unlimited:
            self.used_amount -= commons.Decimal(amount_l)
            self.used_amount = max(self.used_amount, commons.Decimal(0.0))
        self.usage_count -= 1
        self.save()

    def discount(self, amount, currency=None):
        if self.is_percent:
            return self.open_amount_p(amount, currency=currency)
        else:
            return self.open_amount_r(currency=currency)

    def to_local(self, amount, currency, reversed=False):
        from . import exchange_rate

        if not amount:
            return amount
        if not currency:
            return amount
        if not self.currency:
            return amount
        if currency == self.currency:
            return amount
        return exchange_rate.ExchangeRate.convert(
            amount, currency, self.currency, reversed=reversed, rounder=commons.floor
        )

    def to_remote(self, amount, currency, reversed=True):
        from . import exchange_rate

        if not amount:
            return amount
        if not currency:
            return amount
        if not self.currency:
            return amount
        if currency == self.currency:
            return amount
        return exchange_rate.ExchangeRate.convert(
            amount, self.currency, currency, reversed=reversed, rounder=commons.floor
        )

    def is_used(self):
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return True
        if self.amount and commons.Decimal(self.used_amount) >= commons.Decimal(
            self.amount
        ):
            return True
        return False

    def is_valid(self, amount=None, currency=None):
        current = time.time()
        amount_l = self.to_local(amount, currency)
        if self.is_used():
            return False
        if self.used:
            return False
        if not self.enabled:
            return False
        if self.start and current < self.start:
            return False
        if self.expiration and current > self.expiration:
            return False
        if (
            self.amount
            and amount_l
            and commons.Decimal(amount_l) > commons.Decimal(self.open_amount)
        ):
            return False
        if currency and not self.is_valid_currency(currency):
            return False
        if not self.amount and not self.percentage:
            return False
        return True

    def is_valid_currency(self, currency):
        from . import exchange_rate

        if not currency:
            return True
        if not self.currency:
            return True
        if currency == self.currency:
            return True
        has_to_remote = exchange_rate.ExchangeRate.has_rate(self.currency, currency)
        has_to_local = exchange_rate.ExchangeRate.has_rate(currency, self.currency)
        if has_to_remote and has_to_local:
            return True
        return False

    def open_amount_r(self, currency=None):
        open_amount = commons.Decimal(self.amount) - commons.Decimal(self.used_amount)
        return self.to_remote(open_amount, currency)

    def open_amount_p(self, amount, currency=None):
        from . import currency as _currency

        decimal = self.percentage / 100.0
        open_amount = commons.Decimal(amount) * decimal
        if not currency:
            return open_amount
        return _currency.Currency.round(open_amount, currency)

    @appier.operation(name="Notify", parameters=(("Email", "email", str),))
    def notify(self, name=None, *args, **kwargs):
        name = name or "voucher.new"
        voucher = self.reload(map=True)
        receiver = kwargs.get("email", None)
        appier_extras.admin.Event.notify_g(
            name,
            arguments=dict(
                params=dict(
                    payload=voucher, voucher=voucher, receiver=receiver, extra=kwargs
                )
            ),
        )

    @appier.operation(name="Remind", parameters=(("Email", "email", str),))
    def remind(self, *args, **kwargs):
        self.notify(name="voucher.remind", *args, **kwargs)

    @appier.view(name="All Orders")
    def all_orders_v(self, *args, **kwargs):
        from . import order

        kwargs["sort"] = kwargs.get("sort", [("created", -1)])
        kwargs.update(vouchers={"$in": (self.id,)})
        return appier.lazy_dict(
            model=order.Order,
            kwargs=kwargs,
            entities=appier.lazy(lambda: order.Order.find(*args, **kwargs)),
            page=appier.lazy(lambda: order.Order.paginate(*args, **kwargs)),
            names=["reference", "created", "total", "currency", "status"],
        )

    @appier.view(name="Paid Orders")
    def paid_orders_v(self, *args, **kwargs):
        from . import order

        kwargs["sort"] = kwargs.get("sort", [("created", -1)])
        kwargs.update(
            vouchers={"$in": (self.id,)},
            paid=True,
        )
        return appier.lazy_dict(
            model=order.Order,
            kwargs=kwargs,
            entities=appier.lazy(lambda: order.Order.find(*args, **kwargs)),
            page=appier.lazy(lambda: order.Order.paginate(*args, **kwargs)),
            names=["reference", "created", "total", "currency", "status"],
        )

    @property
    def open_amount(self):
        return self.open_amount_r()

    @property
    def is_percent(self):
        if self.amount:
            return False
        if self.percentage:
            return True
        raise appier.OperationalError(message="No amount or percentage defined")

    @property
    def is_value(self):
        return not self.is_percent

    @property
    def is_unlimited(self):
        return self.unlimited
