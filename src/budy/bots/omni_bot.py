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
        self.enabled = appier.conf("OMNI_BOT_ENABLED", False, cast = bool)
        self.store = appier.conf("OMNI_BOT_STORE", None, cast = int)
        self.records = appier.conf("OMNI_BOT_RECORDS", RECORDS)
        self.enabled = kwargs.get("enabled", self.enabled)
        self.store = kwargs.get("store", self.store)
        self.records = kwargs.get("records", self.records)

    def tick(self):
        if not self.enabled: return
        self.sync_products()

    def sync_products(self):
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
                object_id = merchandise["object_id"]
                is_product = _class in ("Product",)
                is_sub_product = _class in ("SubProduct",)
                is_valid = is_product or is_sub_product
                if not is_valid: continue

                if is_product:
                    product = budy.Product.from_omni(merchandise)
                    product.save()
                    media = api.info_media_entity(
                        object_id, dimensions = "original"
                    )
                    for item in media:
                        unique = "%d-%d" % (item["object_id"], item["modify_date"])
                        _media = budy.Media.get(unique = unique, raise_e = False)
                        if _media: continue
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

                        if _media.order == 1:
                            thumbnail = _media.thumbnail_s(width = 520, height = 520)
                            thumbnail.save()
                            product.images.append(thumbnail)

                        product.images.append(_media)
                        product.save()

                    #product.omni_media_s(media)
                else:
                    print("Sub produto %s" % str(object_id))

    def get_api(self):
        import omni
        api = omni.Api()
        return api
