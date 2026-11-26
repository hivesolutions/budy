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

import appier

from . import base

CHANNELS = (
    "direct",
    "organic_search",
    "paid_search",
    "organic_social",
    "paid_social",
    "email",
    "referral",
    "other",
)
""" The marketing channels (Google Analytics 4 default channel
groups) into which the storefront classifies every visit """

FIELDS = (
    "date",
    "channel",
    "source",
    "medium",
    "campaign",
    "referer",
    "landing",
    "landing_product",
    "gclid",
)
""" The fields of a visit that may be set by the storefront,
any other value in the visit payload is ignored """


class Visit(base.BudyBase):
    date = appier.field(
        type=int,
        index=True,
        meta="datetime",
        observations="""The date of the visit, either the start of the
        session or the one of a new tracked touch inside it""",
    )

    day = appier.field(
        index="hashed",
        observations="""The UTC day of the visit (eg: 2026-11-25), used
        to group and count the visits per day""",
    )

    channel = appier.field(
        index="hashed",
        observations="""The marketing channel into which the storefront
        classified the visit (eg: organic_search, paid_social)""",
    )

    source = appier.field()

    medium = appier.field()

    campaign = appier.field(
        index="hashed",
        observations="""The campaign of the visit (utm_campaign), the
        identifier of the campaign in the platform for paid ads""",
    )

    referer = appier.field(observations="""The host of the referer of the visit, the
        remaining parts of the URL are never stored""")

    landing = appier.field(
        observations="""The path of the page where the visit started"""
    )

    landing_product = appier.field(
        type=int,
        index="hashed",
        observations="""The identifier of the product of the landing
        page, in case the visit started in a product page""",
    )

    gclid = appier.field(
        type=bool,
        initial=False,
        description="GCLID",
        observations="""If a Google Ads click identifier was present
        in the landing page of the visit""",
    )

    country = appier.field(
        index="hashed",
        meta="country",
        observations="""Country obtained through GEO IP from the address
        of the visitor, the address itself is never stored""",
    )

    @classmethod
    def validate(cls):
        return super(Visit, cls).validate() + [
            appier.not_null("date"),
            appier.not_null("channel"),
            appier.is_in("channel", CHANNELS),
            appier.string_eq("country", 2),
        ]

    @classmethod
    def list_names(cls):
        return ["id", "date", "channel", "source", "campaign", "landing", "country"]

    @classmethod
    def order_name(cls):
        return ["id", -1]

    @classmethod
    def create_many_s(cls, visits):
        """
        Creates the visits of a batch sent by the storefront, resolving
        the country of each visit from the IP address of the visitor,
        which is then discarded.

        The complete batch is verified before any visit is stored, so
        that an invalid batch never leaves a partial result.

        :type visits: list
        :param visits: The sequence of visit dictionaries, each with the
        channel, the date and the remaining source fields, plus the IP
        address of the visitor (optional, never stored).
        :rtype: list
        :return: The sequence of visits that have been created.
        """

        appier.verify(
            isinstance(visits, list), message="Visits must be a list", code=400
        )
        for visit in visits:
            appier.verify(
                isinstance(visit, dict), message="Visit must be a map", code=400
            )
            channel = visit.get("channel", None)
            appier.verify(
                channel in CHANNELS,
                message="Invalid channel '%s' for visit" % channel,
                code=400,
            )

        # builds the complete set of visit entities, using only the
        # fields known to the visit and resolving the country of the
        # visitor, whose IP address is never stored
        entities = []
        for visit in visits:
            ip_address = visit.get("ip_address", None)
            result = appier.GeoResolver.resolve(ip_address) if ip_address else None
            country = (result or {}).get("country", {})
            kwargs = dict((name, visit[name]) for name in FIELDS if name in visit)
            kwargs["date"] = kwargs.get("date", None) or int(time.time())
            kwargs["country"] = country.get("iso_code", None)
            entities.append(cls(**kwargs))

        for entity in entities:
            entity.save()
        return entities

    @classmethod
    def count_days(cls, start, end, channel=None):
        """
        Counts the visits of every day from the start to the end date,
        grouped by channel, campaign and landing product, as needed by
        the marketing reports.

        The visits are retrieved one day at a time through the indexed
        day of the visit, so that only the visits in range are read.

        :type start: int
        :param start: The timestamp of the first day of the range.
        :type end: int
        :param end: The timestamp of the last day of the range, which
        is included in the count.
        :type channel: String
        :param channel: If provided only the visits of this channel
        are counted.
        :rtype: list
        :return: The sequence of dictionaries with the day, channel,
        campaign, landing product and count of visits, sorted by day.
        """

        counts = dict()
        for timestamp in range(start - start % 86400, end + 1, 86400):
            day = time.strftime("%Y-%m-%d", time.gmtime(timestamp))
            kwargs = dict(day=day)
            if channel:
                kwargs["channel"] = channel
            for visit in cls.find(map=True, **kwargs):
                key = (
                    day,
                    visit["channel"],
                    visit.get("campaign", None),
                    visit.get("landing_product", None),
                )
                counts[key] = counts.get(key, 0) + 1

        keys = sorted(
            counts.keys(),
            key=lambda key: (key[0], key[1], key[2] or "", key[3] or 0),
        )
        return [
            dict(
                day=key[0],
                channel=key[1],
                campaign=key[2],
                landing_product=key[3],
                count=counts[key],
            )
            for key in keys
        ]

    @classmethod
    @appier.view(name="Channel", parameters=(("Channel", "channel", str, "direct"),))
    def channel_v(cls, channel, *args, **kwargs):
        kwargs["sort"] = kwargs.get("sort", [("id", -1)])
        kwargs.update(channel=channel)
        return appier.lazy_dict(
            model=cls,
            kwargs=kwargs,
            entities=appier.lazy(lambda: cls.find(*args, **kwargs)),
            page=appier.lazy(lambda: cls.paginate(*args, **kwargs)),
        )

    def pre_save(self):
        base.BudyBase.pre_save(self)
        self.day = time.strftime("%Y-%m-%d", time.gmtime(self.date))
