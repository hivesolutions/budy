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

import json
import time
import logging
import unittest

import appier

import budy


class VisitTest(unittest.TestCase):
    def setUp(self):
        self.app = budy.BudyApp(level=logging.ERROR)

    def tearDown(self):
        self.app.unload()
        adapter = appier.get_adapter()
        adapter.drop_db()

    def test_create_many_s(self):
        resolve = appier.GeoResolver.__dict__["resolve"]
        appier.GeoResolver.resolve = classmethod(
            lambda cls, address, simplified=True: (
                dict(country=dict(iso_code="PT")) if address == "1.2.3.4" else None
            )
        )
        try:
            before = int(time.time())
            visits = budy.Visit.create_many_s(
                [
                    dict(
                        date=1795615200,
                        channel="paid_social",
                        source="facebook",
                        medium="paid_social",
                        campaign="6777381566382",
                        landing="/produtos/anel",
                        landing_product=12,
                        ip_address="1.2.3.4",
                        user_agent="Mozilla/5.0",
                    ),
                    dict(channel="direct", ip_address="5.6.7.8"),
                    dict(
                        channel="organic_search",
                        source="google",
                        referer="www.google.com",
                        gclid=True,
                    ),
                ]
            )
            after = int(time.time())
        finally:
            appier.GeoResolver.resolve = resolve

        self.assertEqual(len(visits), 3)
        self.assertEqual(len(budy.Visit.find()), 3)

        visit = budy.Visit.get(id=visits[0].id)

        self.assertEqual(visit.date, 1795615200)
        self.assertEqual(visit.day, "2026-11-25")
        self.assertEqual(visit.channel, "paid_social")
        self.assertEqual(visit.campaign, "6777381566382")
        self.assertEqual(visit.landing, "/produtos/anel")
        self.assertEqual(visit.landing_product, 12)
        self.assertEqual(visit.gclid, False)
        self.assertEqual(visit.country, "PT")

        visit = budy.Visit.get(id=visits[0].id, map=True)

        self.assertEqual("ip_address" in visit, False)
        self.assertEqual("user_agent" in visit, False)

        visit = budy.Visit.get(id=visits[1].id)

        self.assertEqual(visit.channel, "direct")
        self.assertEqual(before <= visit.date <= after, True)
        self.assertEqual(visit.country, None)

        visit = budy.Visit.get(id=visits[2].id)

        self.assertEqual(visit.referer, "www.google.com")
        self.assertEqual(visit.gclid, True)
        self.assertEqual(visit.country, None)

        self.assertRaises(
            appier.AssertionError,
            lambda: budy.Visit.create_many_s(
                [dict(channel="direct"), dict(channel="television")]
            ),
        )
        self.assertRaises(
            appier.AssertionError,
            lambda: budy.Visit.create_many_s([dict(source="google")]),
        )
        self.assertRaises(
            appier.AssertionError,
            lambda: budy.Visit.create_many_s(dict(channel="direct")),
        )
        self.assertRaises(
            appier.AssertionError, lambda: budy.Visit.create_many_s(["direct"])
        )
        self.assertEqual(len(budy.Visit.find()), 3)

        visits = budy.Visit.create_many_s([])

        self.assertEqual(visits, [])

    def test_count_days(self):
        day = 1795564800

        budy.Visit.create_many_s(
            [
                dict(
                    date=day + 3600,
                    channel="paid_social",
                    campaign="6777381566382",
                    landing_product=12,
                ),
                dict(
                    date=day + 7200,
                    channel="paid_social",
                    campaign="6777381566382",
                    landing_product=12,
                ),
                dict(date=day + 7200, channel="paid_social", campaign="6777381566382"),
                dict(date=day + 9000, channel="direct"),
                dict(date=day - 60, channel="direct"),
                dict(date=day + 86400 * 2, channel="direct"),
            ]
        )

        counts = budy.Visit.count_days(day - 86400, day + 86399)

        self.assertEqual(
            counts,
            [
                dict(
                    day="2026-11-24",
                    channel="direct",
                    campaign=None,
                    landing_product=None,
                    count=1,
                ),
                dict(
                    day="2026-11-25",
                    channel="direct",
                    campaign=None,
                    landing_product=None,
                    count=1,
                ),
                dict(
                    day="2026-11-25",
                    channel="paid_social",
                    campaign="6777381566382",
                    landing_product=None,
                    count=1,
                ),
                dict(
                    day="2026-11-25",
                    channel="paid_social",
                    campaign="6777381566382",
                    landing_product=12,
                    count=2,
                ),
            ],
        )

        counts = budy.Visit.count_days(day + 43200, day + 43200, channel="direct")

        self.assertEqual(
            counts,
            [
                dict(
                    day="2026-11-25",
                    channel="direct",
                    campaign=None,
                    landing_product=None,
                    count=1,
                )
            ],
        )

        counts = budy.Visit.count_days(day + 86400 * 5, day + 86400 * 6)

        self.assertEqual(counts, [])

    def test_channel_v(self):
        budy.Visit.create_many_s(
            [
                dict(channel="direct"),
                dict(channel="email", source="newsletter"),
                dict(channel="direct"),
            ]
        )

        view = budy.Visit.channel_v("direct")

        self.assertEqual(view["model"], budy.Visit)
        self.assertEqual(len(view["entities"]), 2)

        view = budy.Visit.channel_v("email")

        self.assertEqual(len(view["entities"]), 1)
        self.assertEqual(view["entities"][0].source, "newsletter")

    def test_pre_save(self):
        visit = budy.Visit(date=1795564800 - 60, channel="direct")
        visit.save()

        self.assertEqual(visit.day, "2026-11-24")

        visit.date = 1795564800
        visit.save()
        visit = visit.reload()

        self.assertEqual(visit.day, "2026-11-25")

    def test_create(self):
        controller = self.app.get_controller("VisitAPIController")

        request = appier.Request("POST", "/api/visits")
        request.set_data(
            json.dumps(
                [
                    dict(channel="email", source="newsletter"),
                    dict(channel="referral", referer="www.kuantokusta.pt"),
                ]
            )
        )
        self.app._request = request

        self.assertRaises(appier.AppierException, controller.create)

        request.session["username"] = "username"
        request.session["tokens"] = ["user"]

        self.assertRaises(appier.AppierException, controller.create)

        request.session["tokens"] = ["admin"]

        result = controller.create()

        self.assertEqual(result, dict(count=2))
        self.assertEqual(len(budy.Visit.find(channel="referral")), 1)

        request = appier.Request("POST", "/api/visits")
        request.set_data(json.dumps(dict(visits=[])))
        request.session["username"] = "username"
        request.session["tokens"] = ["admin"]
        self.app._request = request

        self.assertRaises(appier.AssertionError, controller.create)
        self.assertEqual(len(budy.Visit.find()), 2)
