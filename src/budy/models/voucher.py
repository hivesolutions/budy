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

from . import base

class Voucher(base.BudyBase):

    key = appier.field(
        index = True,
        safe = True,
        immutable = True
    )

    amount = appier.field(
        type = commons.Decimal,
        index = True,
        safe = True,
        immutable = True
    )

    used_amount = appier.field(
        type = commons.Decimal,
        index = True,
        safe = True
    )

    percentage = appier.field(
        type = commons.Decimal,
        index = True,
        safe = True,
        immutable = True
    )

    currency = appier.field(
        index = True,
        safe = True
    )

    expiration = appier.field(
        type = int,
        index = True,
        safe = True,
        meta = "datetime"
    )

    usage_count = appier.field(
        type = int,
        index = True,
        safe = True
    )

    usage_limit = appier.field(
        type = int,
        index = True,
        safe = True
    )

    used = appier.field(
        type = bool,
        index = True,
        safe = True
    )

    def __init__(self, *args, **kwargs):
        base.BudyBase.__init__(self, *args, **kwargs)
        self.amount = kwargs.get("amount", 100.0)
        self.used_amount = kwargs.get("used_amount", 0.0)
        self.percentage = kwargs.get("percentage", 0.0)
        self.currency = kwargs.get("currency", None)
        self.expiration = kwargs.get("expiration", None)
        self.usage_count = kwargs.get("usage_count", 0)
        self.usage_limit = kwargs.get("usage_limit", 0)
        self.used = kwargs.get("used", False)

    @classmethod
    def validate(cls):
        return super(Voucher, cls).validate() + [
            appier.not_duplicate("key", cls._name()),

            appier.not_null("amount"),
            appier.gte("amount", 0.0),

            appier.not_null("used_amount"),
            appier.gte("used_amount", 0.0),

            appier.not_null("percentage"),
            appier.gte("percentage", 0.0),

            appier.not_null("usage_count"),
            appier.gte("usage_count", 0),

            appier.not_null("usage_limit"),
            appier.gte("usage_limit", 0)
        ]

    @classmethod
    def list_names(cls):
        return ["description", "created", "amount", "percentage", "expiration", "used"]

    @classmethod
    def is_snapshot(cls):
        return True

    def pre_create(self):
        base.BudyBase.pre_create(self)
        if not hasattr(self, "key") or not self.key:
            self.key = self.secret()
        self.description = self.key[:8]

    def pre_update(self):
        base.BudyBase.pre_update(self)
        if not self.used and not self.is_valid(): self.used = True

    def use_s(self, amount, currency = None):
        amount_l = self.to_local(amount, currency)
        appier.verify(self.is_valid(amount = amount, currency = currency))
        self.used_amount += commons.Decimal(amount_l)
        self.usage_count += 1
        self.save()

    def to_local(self, amount, currency, reversed = False):
        from . import exchange_rate
        if not amount: return amount
        if not currency: return amount
        if not self.currency: return amount
        if currency == self.currency: return amount
        return exchange_rate.ExchangeRate.convert(
            amount,
            currency,
            self.currency,
            reversed = reversed
        )

    def to_remote(self, amount, currency, reversed = True):
        from . import exchange_rate
        if not amount: return amount
        if not currency: return amount
        if not self.currency: return amount
        if currency == self.currency: return amount
        return exchange_rate.ExchangeRate.convert(
            amount,
            self.currency,
            currency,
            reversed = reversed
        )

    def is_valid(self, amount = None, currency = None):
        current = time.time()
        amount_l = self.to_local(amount, currency)
        if self.expiration and current > self.expiration: return False
        if self.usage_limit and self.usage_count >= self.usage_limit: return False
        if commons.Decimal(self.used_amount) >= commons.Decimal(self.amount): return False
        if amount_l and commons.Decimal(amount_l) > commons.Decimal(self.open_amount): return False
        if currency and not self.is_valid_currency(currency): return False
        return True

    def is_valid_currency(self, currency):
        from . import exchange_rate
        if currency == self.currency: return True
        has_to_remote = exchange_rate.ExchangeRate.has_rate(self.currency, currency)
        has_to_local = exchange_rate.ExchangeRate.has_rate(currency, self.currency)
        if has_to_remote and has_to_local: return True
        return False

    def open_amount_r(self, currency = None):
        open_amount = commons.Decimal(self.amount) - commons.Decimal(self.used_amount)
        return self.to_remote(open_amount, currency)

    @property
    def open_amount(self):
        return self.open_amount_r()
