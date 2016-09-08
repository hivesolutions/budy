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

import json
import commons

import appier
import appier_extras

from . import base
from . import bundle

class Product(base.BudyBase):

    GENDER_S = {
        "Male" : "Male",
        "Female" : "Female",
        "Both" : "Both"
    }

    short_description = appier.field(
        index = True,
        default = True
    )

    product_id = appier.field(
        index = True
    )

    gender = appier.field(
        index = True,
        meta = "enum",
        enum = GENDER_S
    )

    quantity_hand = appier.field(
        type = commons.Decimal,
        index = True
    )

    quantity_reserved = appier.field(
        type = commons.Decimal,
        index = True
    )

    price = appier.field(
        type = commons.Decimal,
        index = True,
        initial = commons.Decimal(0.0)
    )

    taxes = appier.field(
        type = commons.Decimal,
        index = True,
        initial = commons.Decimal(0.0)
    )

    currency = appier.field(
        index = True
    )

    order = appier.field(
        type = int,
        index = True
    )

    tag = appier.field()

    tag_description = appier.field()

    price_provider = appier.field(
        index = True
    )

    price_url = appier.field(
        index = True,
        meta = "url"
    )

    farfetch_url = appier.field(
        index = True,
        meta = "url"
    )

    farfetch_male_url = appier.field(
        index = True,
        meta = "url"
    )

    farfetch_female_url = appier.field(
        index = True,
        meta = "url"
    )

    image_url = appier.field(
        index = True,
        meta = "url"
    )

    thumbnail_url = appier.field(
        index = True,
        meta = "url"
    )

    characteristics = appier.field(
        type = list
    )

    brand_s = appier.field(
        index = True
    )

    color_s = appier.field(
        index = True
    )

    category_s = appier.field(
        index = True
    )

    collection_s = appier.field(
        index = True
    )

    colors = appier.field(
        type = appier.references(
            "Color",
            name = "id"
        )
    )

    categories = appier.field(
        type = appier.references(
            "Category",
            name = "id"
        )
    )

    collections = appier.field(
        type = appier.references(
            "Collection",
            name = "id"
        )
    )

    variants = appier.field(
        type = appier.references(
            "Product",
            name = "id"
        )
    )

    images = appier.field(
        type = appier.references(
            "Media",
            name = "id"
        )
    )

    brand = appier.field(
        type = appier.reference(
            "Brand",
            name = "id"
        )
    )

    season = appier.field(
        type = appier.reference(
            "Season",
            name = "id"
        )
    )

    measurements = appier.field(
        type = appier.references(
            "Measurement",
            name = "id"
        )
    )

    compositions = appier.field(
        type = appier.references(
            "Composition",
            name = "id"
        )
    )

    live_movel = appier.field(
        type = appier.references(
            "LiveModel",
            name = "id"
        )
    )

    @classmethod
    def validate(cls):
        return super(Product, cls).validate() + [
            appier.not_null("short_description"),
            appier.not_empty("short_description"),

            appier.not_null("gender"),
            appier.not_empty("gender"),

            appier.not_null("price"),
            appier.gte("price", 0.0),

            appier.not_null("taxes"),
            appier.gte("taxes", 0.0),

            appier.not_empty("brand_s"),

            appier.not_empty("color_s"),

            appier.not_empty("category_s"),

            appier.not_empty("collection_s")
        ]

    @classmethod
    def list_names(cls):
        return ["id", "product_id", "short_description", "enabled", "gender", "tag"]

    @classmethod
    def order_name(self):
        return ["id", -1]

    @classmethod
    def index_names(cls):
        return super(Product, cls).index_names() + ["product_id"]

    @classmethod
    def token_names(cls):
        return super(Product, cls).token_names() + [
            ("short_description", True),
            ("product_id", False),
            ("brand.name", True),
            ("season.name", True),
            ("characteristics", False),
            ("colors.name", True),
            ("categories.name", True),
            ("collections.name", True),
            ("compositions.name", True)
        ]

    @classmethod
    def from_omni(
        cls,
        merchandise,
        inventory_line = None,
        gender = "Both",
        currency = "EUR",
        force = False
    ):
        from . import brand
        from . import color
        from . import category
        from . import collection
        object_id = merchandise["object_id"]
        modify_date = merchandise["modify_date"]
        company_product_code = merchandise["company_product_code"]
        metadata = merchandise["metadata"] or dict()
        _color = metadata.get("material") or []
        _category = metadata.get("category") or []
        _collection = metadata.get("collection") or []
        _brand = metadata.get("brand")
        order = metadata.get("order")

        # verifies if an inventory line has been provided, if that's the case
        # it's possible to determine a proper modification date for the product
        # taking into account also the modification date of its inventory line
        if inventory_line:
            modify_date_line = inventory_line["modify_date"]
            if modify_date_line > modify_date: modify_date = modify_date_line

        colors = _color if isinstance(_color, list) else [_color]
        categories = _category if isinstance(_category, list) else [_category]
        collections = _collection if isinstance(_collection, list) else [_collection]
        colors = [color.Color.ensure_s(_color) for _color in colors]
        categories = [category.Category.ensure_s(_category) for _category in categories]
        collections = [collection.Collection.ensure_s(_collection) for _collection in collections]
        if _brand: _brand = brand.Brand.ensure_s(_brand)
        product = cls.get(product_id = company_product_code, raise_e = False)
        if not product: product = cls()
        product.product_id = company_product_code
        product.short_description = merchandise["name"] or company_product_code
        product.description = merchandise["description"]
        product.gender = gender
        product.currency = currency
        product.order = order
        product.characteristics = metadata.get("characteristics", [])
        product.colors = colors
        product.categories = categories
        product.collections = collections
        product.brand = _brand
        product.meta = dict(
            object_id = object_id,
            modify_date = modify_date
        )
        if "stock_on_hand" in merchandise or force:
            product.quantity_hand = merchandise.get("stock_on_hand", 0.0)
        if "retail_price" in merchandise or force:
            product.price = merchandise.get("retail_price", 0.0)
        if "price" in merchandise or force:
            base_price = product.price if hasattr(product, "price") else 0.0
            base_price = base_price or 0.0
            product.taxes = base_price - merchandise.get("price", 0.0)
        return product

    @classmethod
    @appier.operation(
        name = "Import Omni",
        parameters = (
            ("Product", "product", "longtext"),
        ),
        factory = True
    )
    def import_omni_s(cls, product, safe = True):
        product = json.loads(product)
        product = cls.from_omni(product)
        product.save()

    @classmethod
    @appier.operation(
        name = "Import CSV",
        parameters = (
            ("CSV File", "file", "file"),
            ("Empty source", "empty", bool, True)
        )
    )
    def import_csv_s(cls, file, empty):

        def callback(line):
            from . import color
            from . import brand
            from . import season
            from . import category
            from . import collection
            from . import composition
            from . import measurement

            description,\
            short_description,\
            product_id,\
            gender,\
            price,\
            order,\
            tag,\
            tag_description,\
            farfetch_url,\
            farfetch_male_url,\
            farfetch_female_url,\
            colors,\
            categories,\
            collections, \
            variants,\
            _brand,\
            _season,\
            measurements,\
            compositions, \
            price_provider, \
            price_url = line

            product_id = product_id or None
            price = float(price) if price else None
            order = int(order) if order else None
            tag = tag or None
            tag_description = tag_description or None
            farfetch_url = farfetch_url or None
            farfetch_male_url = farfetch_male_url or None
            farfetch_female_url = farfetch_female_url or None
            price_provider = price_provider or None
            price_url = price_url or None

            colors = colors.split(";") if colors else []
            colors = color.Color.find(name = {"$in" : colors})

            categories = categories.split(";") if categories else []
            categories = category.Category.find(name = {"$in" : categories})

            collections = collections.split(";") if collections else []
            collections = collection.Collection.find(name = {"$in" : collections})

            variants = variants.split(";") if variants else []
            variants = Product.find(product_id = {"$in" : variants})

            _brand = brand.Brand.find(name = _brand) if _brand else None
            _season = season.Season.find(name = _season) if _season else None

            measurements = measurements.split(";") if measurements else []
            measurements = measurement.Measurement.find(name = {"$in" : measurements})

            compositions = compositions.split(";") if compositions else []
            compositions = composition.Composition.find(name = {"$in" : compositions})

            product = cls(
                description = description,
                short_description = short_description,
                product_id = product_id,
                gender = gender,
                price = price,
                order = order,
                tag = tag,
                tag_description = tag_description,
                farfetch_url = farfetch_url,
                farfetch_male_url = farfetch_male_url,
                farfetch_female_url = farfetch_female_url,
                colors = colors,
                categories = categories,
                collections = collections,
                variants = variants,
                brand = _brand,
                season = _season,
                measurements = measurements,
                compositions = compositions,
                price_provider = price_provider,
                price_url = price_url
            )
            product.save()

        if empty: cls.delete_c()
        cls._csv_import(file, callback)

    @classmethod
    @appier.link(name = "Export Simple")
    def simple_csv_url(cls, absolute = False):
        return appier.get_app().url_for(
            "product_api.simple_csv",
            absolute = absolute
        )

    @classmethod
    def _build(cls, model, map):
        price = model.get("price", None)
        if price == None: shipping_cost = None
        else: shipping_cost = bundle.Bundle.eval_shipping(price, 0.0, 1.0, None)
        model["shipping_cost"] = shipping_cost

    def pre_validate(self):
        base.BudyBase.pre_validate(self)
        self.build_images()
        self.build_names()

    def pre_save(self):
        base.BudyBase.pre_save(self)
        if not self.measurements: return
        quantities_hand = [measurement.quantity_hand or 0.0 for measurement in\
            self.measurements if hasattr(measurement, "quantity_hand") and\
            not measurement.quantity_hand == None]
        prices = [measurement.price or 0.0 for measurement in\
            self.measurements if hasattr(measurement, "price") and\
            not measurement.price == None]
        self.quantity_hand = sum(quantities_hand) if quantities_hand else None
        self.price = max(prices) if prices else 0.0

    def build_images(self):
        thumbnail = self.get_image(size = "thumbnail", order = 1)
        thumbnail = thumbnail or self.get_image(size = "thumbnail")
        image = self.get_image(size = "large", order = 1)
        image = image or self.get_image(size = "large")
        self.thumbnail_url = thumbnail.get_url() if thumbnail else None
        self.image_url = image.get_url() if image else None

    def build_names(self):
        self.brand_s = self.brand.name if self.brand else None
        self.color_s = self.colors[0].name if self.colors else None
        self.category_s = self.categories[0].name if self.categories else None
        self.collection_s = self.collections[0].name if self.collections else None

    def related(self, limit = 6, available = True):
        cls = self.__class__
        kwargs = dict()
        if available: kwargs["quantity_hand"] = {"$gt" : 0}
        if self.collections: kwargs["collections"] = {"$in" : [self.collections[0].id]}
        elif self.categories: kwargs["categories"] = {"$in" : [self.categories[0].id]}
        elif self.colors: kwargs["colors"] = {"$in" : [self.colors[0].id]}
        kwargs["id"] = {"$nin" : [self.id]}
        kwargs["sort"] = [("id", 1)]
        count = cls.count(**kwargs)
        skip = self._get_offset(count, limit, kwargs = kwargs)
        delta = skip + limit - count
        if delta > 0: skip = count - skip - delta
        if skip < 0: skip = 0
        products = cls.find(
            eager = ("images",),
            skip = skip,
            limit = limit,
            map = True,
            **kwargs
        )
        return products

    def get_measurement(self, value, name = None):
        for measurement in self.measurements:
            if not measurement: continue
            if not hasattr(measurement, "value"): continue
            if not hasattr(measurement, "name"): continue
            if not measurement.value == value: continue
            if not measurement.name == name: continue
            return measurement
        return None

    def get_price(
        self,
        currency = None,
        country = None,
        attributes = None
    ):
        if not self.price_provider: return self.price
        method = getattr(self, "get_price_%s" % self.price_provider)
        return method(
            currency = currency,
            country = country,
            attributes = attributes
        )

    def get_taxes(
        self,
        currency = None,
        country = None,
        attributes = None
    ):
        if not self.price_provider: return self.taxes
        method = getattr(self, "get_taxes_%s" % self.price_provider, None)
        if not method: return self.taxes
        return method(
            currency = currency,
            country = country,
            attributes = attributes
        )

    def get_price_ripe(
        self,
        currency = None,
        country = None,
        attributes = None
    ):
        if not self.price_url: return self.price

        result = self.get_availability_ripe(
            currency = currency,
            country = country,
            attributes = attributes
        )
        total = result["total"]
        return total["price_final"]

    def get_taxes_ripe(
        self,
        currency = None,
        country = None,
        attributes = None
    ):
        if not self.price_url: return self.price

        result = self.get_availability_ripe(
            currency = currency,
            country = country,
            attributes = attributes
        )
        total = result["total"]
        return total["ddp"] + total["vat"]

    def get_availability_ripe(
        self,
        currency = None,
        country = None,
        attributes = None
    ):
        attributes_m = json.loads(attributes)
        p = []
        parts = attributes_m.get("parts", {})
        embossing = attributes_m.get("embossing", None)
        letters = attributes_m.get("letters", None)

        for key, value in appier.legacy.iteritems(parts):
            material = value["material"]
            color = value["color"]
            triplet = "%s:%s:%s" % (key, material, color)
            p.append(triplet)

        params = dict(
            product_id = self.product_id,
            p = p
        )
        if currency: params["currency"] = currency
        if country: params["country"] = country
        if embossing: params["embossing"] = embossing
        if letters: params["letters"] = letters

        result = appier.get(
            self.price_url,
            params = params
        )
        return result

    def get_currency(self, currency = None):
        if not self.price_provider: return self.currency or currency
        method = getattr(self, "get_currency_%s" % self.price_provider)
        return method(currency = currency)

    def get_currency_ripe(self, currency = None):
        return self.currency or currency

    def get_image(self, size = None, order = None):
        for image in self.images:
            is_size = size == None or image.size == size
            if not is_size: continue
            is_order = order == None or image.order == order
            if not is_order: continue
            return image
        return None

    def get_size(self, currency = None, country = None, attributes = None):
        if not self.price_provider: return None, None
        method = getattr(self, "get_size_%s" % self.price_provider)
        return method(
            country = country,
            attributes = attributes
        )

    def get_size_ripe(
        self,
        currency = None,
        country = None,
        attributes = None
    ):
        attributes_m = json.loads(attributes)
        size = attributes_m["size"]
        scale = attributes_m["scale"]
        gender = attributes_m["gender"]

        if gender == "male": converter = lambda native: ((native - 17) / 2) + 36
        else: converter = lambda native: ((native - 17) / 2) + 34

        return converter(size), scale

    @appier.operation(
        name = "Add Collection",
        parameters = (
            (
                "Collection",
                "collection",
                appier.reference("Collection", name = "id")
            ),
        )
    )
    def add_collection_s(self, collection):
        if not collection: return
        if collection in self.collections: return
        self.collections.append(collection)
        self.save()

    @appier.operation(
        name = "Remove Collection",
        parameters = (
            (
                "Collection",
                "collection",
                appier.reference("Collection", name = "id")
            ),
        )
    )
    def remove_collection_s(self, collection):
        if not collection: return
        if not collection in self.collections: return
        self.collections.remove(collection)
        self.save()

    @appier.operation(
        name = "Add Image",
        parameters = (
            (
                "Image",
                "image",
                appier.reference("Media", name = "id")
            ),
        )
    )
    def add_image_s(self, image):
        if not image: return
        if image in self.images: return
        self.images.append(image)
        self.save()

    @appier.operation(
        name = "Remove Image",
        parameters = (
            (
                "Image",
                "image",
                appier.reference("Media", name = "id")
            ),
        )
    )
    def remove_image_s(self, image):
        if not image: return
        if not image in self.images: return
        self.images.remove(image)
        self.save()

    @appier.operation(name = "Fix")
    def fix_s(self):
        if not self.exists(): return
        self.save()

    @appier.operation(name = "Ensure Quantity", level = 2, devel = True)
    def ensure_quantity_s(self, quantity = 1.0):
        if self.quantity_hand: return
        self.quantity_hand = quantity
        self.save()

    @appier.operation(name = "Ensure Price", level = 2, devel = True)
    def ensure_price_s(self, price = 100.0):
        if self.price: return
        self.price = price
        self.save()

    @appier.operation(
        name = "Notify",
        parameters = (("Email", "email", str),)
    )
    def notify(self, name = None, *args, **kwargs):
        name = name or "product.new"
        product = self.reload(map = True)
        receiver = kwargs.get("email", None)
        appier_extras.admin.Event.notify_g(
            name,
            arguments = dict(
                params = dict(
                    payload = product,
                    product = product,
                    receiver = receiver,
                    extra = kwargs
                )
            )
        )

    @appier.operation(
        name = "Share",
        parameters = (
            ("Email", "email", str),
            ("Sender", "sender", appier.legacy.UNICODE)
        )
    )
    def share(self, *args, **kwargs):
        self.notify("product.share", *args, **kwargs)

    @property
    def quantity(self):
        return self.quantity_hand

    @property
    def is_parent(self):
        if not hasattr(self, "measurements"): return False
        if not self.measurements: return False
        return len(self.measurements) > 0

    def _get_offset(self, count, limit, kwargs):
        return self._get_offset_offset(count, limit, kwargs)

    def _get_offset_simple(self, count, limit, kwargs):
        return self.id % count

    def _get_offset_offset(self, count, limit, kwargs):
        cls = self.__class__
        kwargs = dict(kwargs)
        kwargs["id"] = {"$lt" : self.id}
        offset = cls.count(**kwargs)
        return offset
