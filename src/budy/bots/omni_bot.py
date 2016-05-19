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

import appier

import budy

from . import base

RECORDS = 100

class OmniBot(base.Bot):

    def __init__(self, *args, **kwargs):
        base.Bot.__init__(self, *args, **kwargs)
        self.enabled = appier.conf("OMNI_BOT_ENABLED", False, cast = bool)
        self.store = appier.conf("OMNI_BOT_STORE", None, cast = int)
        self.records = appier.conf("OMNI_BOT_RECORDS", RECORDS)
        self.enabled = kwargs.get("enabled", self.enabled)
        self.store = kwargs.get("store", self.store)
        self.records = kwargs.get("records", self.records)
        self.api = None

    def tick(self):
        if not self.enabled: return
        self.sync_products()
        self.fix_products()

    def sync_products(self):
        self.owner.logger.info("Starting Omni sync ...")
        self.sync_products_store()
        self.sync_products_db()
        self.sync_measurements_db()
        self.owner.logger.info("Ended Omni sync")

    def fix_products(self):
        self.owner.logger.info("Starting Omni fix ...")
        self.fix_products()
        self.fix_measurements_db()
        self.owner.logger.info("Ended Omni fix")

    def sync_products_store(self):
        api = self.get_api()
        offset = 0

        while True:
            kwargs = {
                "filter_string" : "",
                "start_record" : offset,
                "number_records" : self.records,
                "filters[]" : [
                    "sellable:equals:2"
                ]
            }
            merchandise = api.list_store_merchandise(
                store_id = self.store,
                **kwargs
            )
            if not merchandise: break
            offset += len(merchandise)

            for merchandise in merchandise:
                _class = merchandise["_class"]
                is_product = _class in ("Product",)
                is_sub_product = _class in ("SubProduct",)
                is_valid = is_product or is_sub_product
                if not is_valid: continue
                if is_product: self.sync_product(merchandise)
                else: self.sync_sub_product(merchandise)

    def sync_products_db(self):
        api = self.get_api()
        products = budy.Product.find()

        self.owner.logger.info(
            "Syncing %d products in database ..." % len(products)
        )

        for product in products:
            object_id = product.meta.get("object_id", None)
            if not object_id: continue
            merchandise = api.get_product(object_id)
            if not merchandise: continue
            merchandise.pop("stock_on_hand", None)
            merchandise.pop("retail_price", None)
            self.sync_product(merchandise)

    def sync_measurements_db(self):
        api = self.get_api()
        measurements = budy.Measurement.find()

        self.owner.logger.info(
            "Syncing %d measurements in database ..." % len(measurements)
        )

        for measurement in measurements:
            object_id = measurement.meta.get("object_id", None)
            if not object_id: continue
            merchandise = api.get_sub_product(object_id)
            if not merchandise: continue
            merchandise.pop("stock_on_hand", None)
            merchandise.pop("retail_price", None)
            self.sync_sub_product(merchandise)

    def fix_products_db(self):
        products = budy.Product.find()

        self.owner.logger.info(
            "Fixing %d products in database ..." % len(products)
        )

        for product in products: product.fix_s()

    def fix_measurements_db(self):
        measurements = budy.Measurement.find()

        self.owner.logger.info(
            "Fixing %d measurements in database ..." % len(measurements)
        )

        for measurement in measurements: measurement.fix_s()

    def sync_product(self, merchandise, force = False):
        # retrieves the reference to the api object that is
        # going to be used for api based operations
        api = self.get_api()

        # retrieves some of the most general attributes of the
        # merchandise that is going to be integrated as a product
        _class = merchandise["_class"]
        object_id = merchandise["object_id"]

        # builds a new product instance from the merchandise
        # information that has just been retrieved
        product = budy.Product.from_omni(merchandise, force = force)
        product.save()
        product.images = []

        # retrieves the media information associated with the
        # current merchandise to be able to sync it by either
        # creating new local medias or re-using existing ones
        media = api.info_media_entity(
            object_id, dimensions = "original"
        )

        # iterates over the complete set of media associated with
        # the current product to try to create/update its media
        for item in media:
            # creates the unique value for the media from its object
            # identifier and its last modification data, using this
            # value tries to retrieve a possible already existing
            # and equivalent media (avoids duplication)
            unique = "%d-%d" % (item["object_id"], item["modify_date"])
            _media = budy.Media.get(unique = unique, raise_e = False)

            # in case the media does not exist, tries to retrieve the
            # new remote data from the source and create a new media
            if not _media:
                media_url = api.get_media_url(item["secret"])
                data = appier.get(media_url)
                _media = budy.Media(
                    description = item["dimensions"],
                    label = item["label"],
                    order = item["position"] or 1,
                    size = item["dimensions"],
                    unique = unique,
                    file = appier.File((item["label"], None, data))
                )
                _media.save()

            # iterates over the complete set of resized images to
            # be created and for each of them verifies it has to
            # be generated or if one already exists
            for suffix, size in (
                ("thumbnail", 260),
                ("thumbnail_2x", 540),
                ("large", 540),
                ("large_2x", 1080)
            ):
                resized_unique = "%s-%s" % (unique, suffix)
                resized = budy.Media.get(unique = resized_unique, raise_e = False)
                if not resized:
                    resized = _media.thumbnail_s(width = size, suffix = suffix)
                    resized.save()
                product.images.append(resized)

            product.images.append(_media)
            product.save()

    def sync_sub_product(self, merchandise, force = False):
        api = self.get_api()

        object_id = merchandise["object_id"]
        sub_product = api.get_sub_product(object_id)

        product = sub_product["product"]

        # tries to run the conversion process from the sub product and
        # associated merchandise value to the measurement in case it fails
        # (meaning that no product was found) a new try is made after the
        # proper associated (parent) product is created
        measurement = budy.Measurement.from_omni(
            merchandise,
            sub_product = sub_product,
            force = force
        )
        if not measurement:
            product = api.get_product(product["object_id"])
            self.sync_product(product, force = True)
            measurement = budy.Measurement.from_omni(
                merchandise,
                sub_product = sub_product,
                force = force
            )

        if not measurement: return

        measurement.save()

        parent = measurement.product

        if not measurement in parent.measurements:
            parent.measurements.append(measurement)
            parent.save()

    def get_api(self):
        import omni
        if self.api: return self.api
        self.api = omni.Api()
        return self.api
