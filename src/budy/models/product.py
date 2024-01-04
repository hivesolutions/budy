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
import commons

import appier
import appier_extras

from . import base
from . import bundle
from . import currency as _currency


class Product(base.BudyBase):
    GENDER_S = {"Male": "Male", "Female": "Female", "Child": "Child", "Both": "Both"}
    """ The dictionary that maps the multiple gender
    enumeration values with their string representation """

    short_description = appier.field(
        index="hashed",
        default=True,
        observations="""A short description on the product
        that should be used as the title for the product""",
    )

    product_id = appier.field(
        index="hashed",
        description="Product ID",
        observations="""The primary identifier of the
        product, should be globally unique""",
    )

    supplier_code = appier.field(
        index="hashed",
        observations="""The identifier used by the
        (back) supplier of the product, should be considered
        a more unique way of identifying a product""",
    )

    sku = appier.field(
        index="hashed",
        description="SKU",
        observations="""The main identifier to be used for
        the keeping of the internal reference SKU (Stock Keeping
        Unit), should be considered the public way of representing
        the product""",
    )

    upc = appier.field(
        index="hashed",
        description="UPC",
        observations="""The standard Universal Product Code
        (UPC) value for this product""",
    )

    ean = appier.field(
        index="hashed",
        description="EAN",
        observations="""The standard European Article Number
        (EAN) value for this product""",
    )

    gender = appier.field(index="hashed", meta="enum", enum=GENDER_S)

    weight = appier.field(
        type=commons.Decimal,
        index=True,
        observations="""The weight of the current product in
        a unit defined by convention (defined before-hand)""",
    )

    quantity_hand = appier.field(
        type=commons.Decimal,
        index=True,
        observations="""The total quantity that is currently
        available (on hand) for the current product, if not
        set (none) the product is considered to have unlimited quantity
        (inventory is not controlled)""",
    )

    quantity_reserved = appier.field(
        type=commons.Decimal,
        index=True,
        observations="""The total quantity that is currently
        reserved (not available) for the current product, if not
        set (none) the product is considered to not have reservation
        control disabled (no reservations are possible)""",
    )

    price = appier.field(
        type=commons.Decimal,
        index=True,
        initial=commons.Decimal(0.0),
        observations="""Main retail price to be used for
        a possible sale transaction of the product (includes taxes)""",
    )

    price_compare = appier.field(
        type=commons.Decimal,
        index=True,
        initial=commons.Decimal(0.0),
        observations="""The price that is going to be used
        as the base for discount calculation purposes""",
    )

    taxes = appier.field(
        type=commons.Decimal,
        index=True,
        initial=commons.Decimal(0.0),
        observations="""The amount of taxes that are associated
        with the product this value can include the VAT value but
        it's not limited to it and more tax values can be included""",
    )

    currency = appier.field(index="hashed")

    order = appier.field(type=int, index="hashed")

    tag = appier.field()

    tag_description = appier.field()

    price_provider = appier.field(index=True)

    discountable = appier.field(
        type=bool,
        initial=True,
        observations="""Flag that indicates if the product is
        eligible for any kind of global discount""",
    )

    orderable = appier.field(
        type=bool,
        observations="""Flag that controls if the product is only
        meant to be used for pre-ordering and not direct sales""",
    )

    price_url = appier.field(index="hashed", meta="url", description="Price URL")

    farfetch_url = appier.field(index="hashed", meta="url", description="Farfetch URL")

    farfetch_male_url = appier.field(
        index="hashed", meta="url", description="Farfetch Male URL"
    )

    farfetch_female_url = appier.field(
        index="hashed", meta="url", description="Farfetch Female URL"
    )

    image_url = appier.field(index="hashed", meta="image_url", description="Image URL")

    thumbnail_url = appier.field(
        index="hashed",
        meta="image_url",
        description="Thumbnail URL",
        observations="""The URL to the thumbnail image (low resolution)
        to be used in listing contexts""",
    )

    characteristics = appier.field(
        type=list,
        observations="""The sequence of characteristics that
        define the product under unstructured language""",
    )

    features = appier.field(
        type=dict,
        observations="""Dictionary that maps a set of optional
        features with their corresponding configuration, for example
        the `initials` feature can be associated with the rules
        that control those same initials""",
    )

    labels = appier.field(
        type=list,
        observations="""Set of simple tag labels that define the
        product behavior, this value is a calculated one based on
        the labels provided by the complete set of collections""",
    )

    brand_s = appier.field(index="hashed")

    season_s = appier.field(index="hashed")

    color_s = appier.field(index="hashed")

    category_s = appier.field(index="hashed")

    collection_s = appier.field(index="hashed")

    colors = appier.field(type=appier.references("Color", name="id"))

    categories = appier.field(type=appier.references("Category", name="id"))

    collections = appier.field(type=appier.references("Collection", name="id"))

    variants = appier.field(type=appier.references("Product", name="id"))

    images = appier.field(type=appier.references("Media", name="id"))

    brand = appier.field(type=appier.reference("Brand", name="id"))

    season = appier.field(type=appier.reference("Season", name="id"))

    measurements = appier.field(type=appier.references("Measurement", name="id"))

    compositions = appier.field(type=appier.references("Composition", name="id"))

    live_model = appier.field(type=appier.references("LiveModel", name="id"))

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
            appier.not_empty("season_s"),
            appier.not_empty("color_s"),
            appier.not_empty("category_s"),
            appier.not_empty("collection_s"),
        ]

    @classmethod
    def list_names(cls):
        return [
            "id",
            "product_id",
            "short_description",
            "enabled",
            "gender",
            "tag",
            "image_url",
        ]

    @classmethod
    def order_name(cls):
        return ["id", -1]

    @classmethod
    def index_names(cls):
        return super(Product, cls).index_names() + ["product_id"]

    @classmethod
    def token_names(cls):
        return super(Product, cls).token_names() + [
            ("short_description", True),
            ("product_id", False),
            ("supplier_code", False),
            ("sku", False),
            ("upc", False),
            ("ean", False),
            ("brand.name", True),
            ("season.name", True),
            ("characteristics", False),
            ("features", False),
            ("colors.name", True),
            ("categories.name", True),
            ("collections.name", True),
            ("compositions.name", True),
        ]

    @classmethod
    def from_omni(
        cls,
        merchandise,
        inventory_line=None,
        inventory_lines=None,
        gender="Both",
        currency="EUR",
        patch=True,
        force=False,
    ):
        from . import brand
        from . import color
        from . import season
        from . import category
        from . import collection

        # gathers the complete set of element from the Omni
        # related merchandise element (product or sub-product)
        object_id = merchandise["object_id"]
        modify_date = merchandise["modify_date"]
        company_product_code = merchandise["company_product_code"]
        upc = merchandise["upc"]
        ean = merchandise["ean"]
        weight = merchandise["weight"]
        metadata = merchandise["metadata"] or dict()
        price_compare = metadata.get("compare_price") or None
        discount = metadata.get("discount") or None
        _color = metadata.get("material") or []
        _category = metadata.get("category") or []
        _collection = metadata.get("collection") or []
        _brand = metadata.get("brand")
        _season = metadata.get("season")
        gender = metadata.get("gender") or gender
        order = metadata.get("order")
        discountable = metadata.get("discountable", True)
        orderable = metadata.get("orderable", False)
        sku_field = metadata.get("sku_field")

        # verifies if an inventory line has been provided, if that's the case
        # it's possible to determine a proper modification date for the product
        # taking into account also the modification date of its inventory line
        if inventory_line:
            modify_date_line = inventory_line["modify_date"]
            if modify_date_line > modify_date:
                modify_date = modify_date_line

        # creates the stocks list in case there are valid inventory lines being
        # passed on the current product update/creation
        stocks = None if inventory_lines == None else []

        # iterates over the complete set of available inventory lines to build the
        # associated stock dictionary with the information on the stock point, this
        # is going to be added to the list of stocks to the product
        for inventory_line in inventory_lines if inventory_lines else []:
            stock_on_hand = inventory_line.get("stock_on_hand", 0)
            stock_reserved = inventory_line.get("stock_reserved", 0)
            stock_in_transit = inventory_line.get("stock_in_transit", 0)
            retail_price = inventory_line.get("retail_price", {}).get("value", 0.0)
            functional_unit = inventory_line.get("functional_unit", None)

            is_valid = functional_unit and functional_unit.get("status") == 1
            if not is_valid:
                continue

            stock_m = dict(
                store_id=functional_unit["object_id"],
                store_name=functional_unit["name"],
                stock_on_hand=stock_on_hand,
                stock_reserved=stock_reserved,
                stock_in_transit=stock_in_transit,
                retail_price=retail_price,
            )
            stocks.append(stock_m)

        colors = _color if isinstance(_color, list) else [_color]
        categories = _category if isinstance(_category, list) else [_category]
        collections = _collection if isinstance(_collection, list) else [_collection]
        colors = [color.Color.ensure_s(_color) for _color in colors]
        categories = [category.Category.ensure_s(_category) for _category in categories]
        collections = [
            collection.Collection.ensure_s(_collection) for _collection in collections
        ]
        if _brand:
            _brand = brand.Brand.ensure_s(_brand)
        if _season:
            _season = season.Season.ensure_s(_season)
        product = cls.get(product_id=company_product_code, raise_e=False)
        if not product:
            product = cls()

        # in case the weight contains the special 1.0 value then
        # it must be set to invalid as this is considered to be
        # a dummy (and invalid value), this is only performed in
        # case there's a valid season value (eg: watches) set and
        # the patch mode is set (to enable automatic data correction)
        # this is considered a hack to reverse the invalid data source
        # values and should be used with proper care
        if patch and weight == 1.0 and _season:
            weight = None

        product.product_id = company_product_code
        product.supplier_code = upc
        product.sku = merchandise.get(sku_field) or upc or company_product_code
        product.upc = upc
        product.ean = ean
        product.weight = weight
        product.short_description = merchandise["name"] or company_product_code
        product.description = merchandise["description"]
        product.gender = gender
        product.price_compare = price_compare
        product.currency = currency
        product.order = order
        product.discountable = discountable
        product.orderable = orderable
        product.characteristics = metadata.get("characteristics", [])
        product.features = metadata.get("features", {})
        product.colors = colors
        product.categories = categories
        product.collections = collections
        product.brand = _brand
        product.season = _season

        meta = dict(
            object_id=object_id,
            company_product_code=company_product_code,
            modify_date=modify_date,
            discount=discount,
        )
        if hasattr(product, "meta") and product.meta:
            product.meta.update(meta)
        else:
            product.meta = meta
        if not stocks == None:
            product.meta["stocks"] = stocks

        if "stock_on_hand" in merchandise or force:
            product.quantity_hand = merchandise.get("stock_on_hand", 0.0)
        if "retail_price" in merchandise or force:
            # "grabs" the retail price from the original merchandise entity
            # from Omni to be used as the base calculus
            retail_price = merchandise.get("retail_price", 0.0)

            # stores the "original" retail price in the product's metadata
            # storage may be needed latter for update operations
            product.meta["retail_price"] = retail_price
        if "price" in merchandise or force:
            # "grabs" the (untaxed) price from the original merchandise entity
            # from Omni to be used as the base calculus
            untaxed_price = merchandise.get("price", 0.0)

            # stores the "original" untaxed price in the product's metadata
            # storage may be needed latter for update operations
            product.meta["untaxed_price"] = untaxed_price

        # in case all of the required "original" financial information (prices)
        # is available then the price, taxes and price compare are calculated
        if "retail_price" in product.meta and "untaxed_price" in product.meta:
            untaxed_price = (
                _currency.Currency.round(
                    product.meta["untaxed_price"] * ((100.0 - discount) / 100.0),
                    currency,
                )
                if discount
                else product.meta["untaxed_price"]
            )
            product.price = (
                _currency.Currency.round(
                    product.meta["retail_price"] * ((100.0 - discount) / 100.0),
                    currency,
                )
                if discount
                else product.meta["retail_price"]
            )
            product.taxes = product.price - untaxed_price
            if not product.price_compare and discount:
                product.price_compare = product.meta["retail_price"]

        # returns the "final" product instance to the caller so that it's possible
        # to properly save the newly generated product instance according to omni
        return product

    @classmethod
    @appier.operation(
        name="Import Omni",
        parameters=(("Product", "product", "longtext"),),
        factory=True,
    )
    def import_omni_s(cls, product, safe=True):
        product = json.loads(product)
        product = cls.from_omni(product)
        product.save()
        return product

    @classmethod
    @appier.operation(
        name="Import CSV",
        parameters=(
            ("CSV File", "file", "file"),
            ("Empty source", "empty", bool, False),
        ),
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

            (
                description,
                short_description,
                product_id,
                gender,
                price,
                order,
                tag,
                tag_description,
                farfetch_url,
                farfetch_male_url,
                farfetch_female_url,
                colors,
                categories,
                collections,
                variants,
                _brand,
                _season,
                measurements,
                compositions,
                price_provider,
                price_url,
            ) = line

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
            colors = color.Color.find(name={"$in": colors})

            categories = categories.split(";") if categories else []
            categories = category.Category.find(name={"$in": categories})

            collections = collections.split(";") if collections else []
            collections = collection.Collection.find(name={"$in": collections})

            variants = variants.split(";") if variants else []
            variants = Product.find(product_id={"$in": variants})

            _brand = brand.Brand.find(name=_brand) if _brand else None
            _season = season.Season.find(name=_season) if _season else None

            measurements = measurements.split(";") if measurements else []
            measurements = measurement.Measurement.find(name={"$in": measurements})

            compositions = compositions.split(";") if compositions else []
            compositions = composition.Composition.find(name={"$in": compositions})

            product = cls(
                description=description,
                short_description=short_description,
                product_id=product_id,
                gender=gender,
                price=price,
                order=order,
                tag=tag,
                tag_description=tag_description,
                farfetch_url=farfetch_url,
                farfetch_male_url=farfetch_male_url,
                farfetch_female_url=farfetch_female_url,
                colors=colors,
                categories=categories,
                collections=collections,
                variants=variants,
                brand=_brand,
                season=_season,
                measurements=measurements,
                compositions=compositions,
                price_provider=price_provider,
                price_url=price_url,
            )
            product.save()

        if empty:
            cls.delete_c()
        cls._csv_import(file, callback)

    @classmethod
    @appier.link(name="Export Simple")
    def simple_csv_url(cls, absolute=False):
        return appier.get_app().url_for("product_api.simple_csv", absolute=absolute)

    @classmethod
    def _build(cls, model, map):
        super(Product, cls)._build(model, map)

        # retrieves the multiple values from the product model that are
        # going to be used in the calculated attributes construction
        price = model.get("price", None)
        price_compare = model.get("price_compare", None)
        labels = model.get("labels", ())

        # verifies if the current product is considered to be a discounted
        # one, that happens when the price compare is greater than price
        is_discounted = bool(price and price_compare and price_compare > price)

        # calculates the shipping costs taking into account if the price
        # is currently defined for the product defaulting to none otherwise
        if price == None:
            shipping_cost = None
        else:
            shipping_cost = bundle.Bundle.eval_shipping(price, 0.0, 1.0, None)

        # sets the multiple attributes of the product that describe it through
        # calculated attributes (as expected by model retriever)
        model["is_discounted"] = is_discounted
        model["is_discounted_s"] = "discounted" if is_discounted else "not-discounted"
        model["shipping_cost"] = shipping_cost
        for label in labels:
            model[label] = label
            model[label + "_s"] = "true"

    def pre_validate(self):
        base.BudyBase.pre_validate(self)
        self.build_images()
        self.build_names()
        self.build_labels()

    def pre_save(self):
        base.BudyBase.pre_save(self)
        if not self.measurements:
            return
        quantities_hand = [
            measurement.quantity_hand or 0.0
            for measurement in self.measurements
            if hasattr(measurement, "quantity_hand")
            and not measurement.quantity_hand == None
        ]
        prices = [
            measurement.price or 0.0
            for measurement in self.measurements
            if hasattr(measurement, "price") and not measurement.price == None
        ]
        taxes = [
            measurement.taxes or 0.0
            for measurement in self.measurements
            if hasattr(measurement, "taxes") and not measurement.taxes == None
        ]
        prices_compare = [
            measurement.price_compare or 0.0
            for measurement in self.measurements
            if hasattr(measurement, "price_compare")
            and not measurement.price_compare == None
        ]
        self.quantity_hand = sum(quantities_hand) if quantities_hand else None
        self.price = max(prices) if prices else 0.0
        self.taxes = max(taxes) if taxes else 0.0
        self.price_compare = max(prices_compare) if prices_compare else None

        # in case the product is orderable then the quantity on hand must
        # be forced to be greater than zero so that the product can be
        # listed as available (otherwise it would not be listed), this is
        # considered to be a "hack"
        if self.orderable and self.quantity_hand <= 0:
            self.quantity_hand = 1

    def build_images(self):
        thumbnail = self.get_image(size="thumbnail", order=1)
        thumbnail = thumbnail or self.get_image(size="thumbnail")
        image = self.get_image(size="large", order=1)
        image = image or self.get_image(size="large")
        self.thumbnail_url = thumbnail.get_url() if thumbnail else None
        self.image_url = image.get_url() if image else None

    def build_names(self):
        self.brand_s = self.brand.name if self.brand else None
        self.season_s = self.season.name if self.season else None
        self.color_s = self.colors[0].name if self.colors else None
        self.category_s = self.categories[0].name if self.categories else None
        self.collection_s = self.collections[0].name if self.collections else None

    def build_labels(self):
        self._reset_labels()
        self._build_labels(self.brand)
        self._build_labels(self.season)
        self._build_labels(self.colors)
        self._build_labels(self.categories)
        self._build_labels(self.collections)

    def related(self, limit=6, available=True, enabled=True):
        cls = self.__class__
        kwargs = dict()
        if available:
            kwargs["quantity_hand"] = {"$gt": 0}
        if self.collections:
            kwargs["collections"] = {"$in": [self.collections[0].id]}
        elif self.categories:
            kwargs["categories"] = {"$in": [self.categories[0].id]}
        elif self.colors:
            kwargs["colors"] = {"$in": [self.colors[0].id]}
        elif self.brand:
            kwargs["brand"] = {"$in": [self.brand.id]}
        elif self.season:
            kwargs["season"] = {"$in": [self.season.id]}
        kwargs["id"] = {"$nin": [self.id]}
        kwargs["sort"] = [("id", 1)]
        count = cls.count(**kwargs)
        skip = self._get_offset(count, limit, kwargs=kwargs)
        delta = skip + limit - count
        if delta > 0:
            skip = count - skip - delta
        if skip < 0:
            skip = 0
        find = cls.find_e if enabled else cls.find
        products = find(eager=("images",), skip=skip, limit=limit, map=True, **kwargs)
        return products

    def get_measurement(self, value, name=None):
        for measurement in self.measurements:
            if not measurement:
                continue
            if not hasattr(measurement, "value"):
                continue
            if not hasattr(measurement, "name"):
                continue
            if not measurement.value == value:
                continue
            if not measurement.name == name:
                continue
            return measurement
        return None

    def get_price(self, currency=None, country=None, attributes=None):
        if not self.price_provider:
            return self.price
        method = getattr(self, "get_price_%s" % self.price_provider)
        return method(currency=currency, country=country, attributes=attributes)

    def get_taxes(self, currency=None, country=None, attributes=None):
        if not self.price_provider:
            return self.taxes
        method = getattr(self, "get_taxes_%s" % self.price_provider, None)
        if not method:
            return self.taxes
        return method(currency=currency, country=country, attributes=attributes)

    def get_price_ripe(self, currency=None, country=None, attributes=None):
        if not self.price_url:
            return self.price

        result = self.get_availability_ripe(
            currency=currency, country=country, attributes=attributes
        )
        total = result["total"]
        return total["price_final"]

    def get_taxes_ripe(self, currency=None, country=None, attributes=None):
        if not self.price_url:
            return self.price

        result = self.get_availability_ripe(
            currency=currency, country=country, attributes=attributes
        )
        total = result["total"]
        return total["ddp"] + total["vat"]

    def get_availability_ripe(self, currency=None, country=None, attributes=None):
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

        params = dict(product_id=self.product_id, p=p)
        if currency:
            params["currency"] = currency
        if country:
            params["country"] = country
        if embossing:
            params["embossing"] = embossing
        if letters:
            params["letters"] = letters

        result = appier.get(self.price_url, params=params)
        return result

    def get_currency(self, currency=None):
        if not self.price_provider:
            return self.currency or currency
        method = getattr(self, "get_currency_%s" % self.price_provider)
        return method(currency=currency)

    def get_currency_ripe(self, currency=None):
        return self.currency or currency

    def get_image(self, size=None, order=None):
        for image in self.images:
            if not image:
                continue
            if not hasattr(image, "size"):
                continue
            if not hasattr(image, "order"):
                continue
            is_size = size == None or image.size == size
            if not is_size:
                continue
            is_order = order == None or image.order == order
            if not is_order:
                continue
            return image
        return None

    def get_size(self, currency=None, country=None, attributes=None):
        if not self.price_provider:
            return None, None
        method = getattr(self, "get_size_%s" % self.price_provider)
        return method(country=country, attributes=attributes)

    def get_size_ripe(self, currency=None, country=None, attributes=None):
        attributes_m = json.loads(attributes)
        size = attributes_m["size"]
        scale = attributes_m["scale"]
        gender = attributes_m["gender"]

        if gender == "male":
            converter = lambda native: ((native - 17) / 2) + 36
        else:
            converter = lambda native: ((native - 17) / 2) + 34

        return converter(size), scale

    @appier.operation(
        name="Add Collection",
        parameters=(
            ("Collection", "collection", appier.reference("Collection", name="id")),
        ),
    )
    def add_collection_s(self, collection):
        if not collection:
            return
        if collection in self.collections:
            return
        self.collections.append(collection)
        self.save()

    @appier.operation(
        name="Remove Collection",
        parameters=(
            ("Collection", "collection", appier.reference("Collection", name="id")),
        ),
    )
    def remove_collection_s(self, collection):
        if not collection:
            return
        if not collection in self.collections:
            return
        self.collections.remove(collection)
        self.save()

    @appier.operation(
        name="Add Image",
        parameters=(("Image", "image", appier.reference("Media", name="id")),),
    )
    def add_image_s(self, image):
        if not image:
            return
        if image in self.images:
            return
        self.images.append(image)
        self.save()

    @appier.operation(
        name="Remove Image",
        parameters=(("Image", "image", appier.reference("Media", name="id")),),
    )
    def remove_image_s(self, image):
        if not image:
            return
        if not image in self.images:
            return
        self.images.remove(image)
        self.save()

    @appier.operation(name="Fix")
    def fix_s(self):
        if not self.exists():
            return
        self.save()

    @appier.operation(name="Ensure Quantity", level=2, devel=True)
    def ensure_quantity_s(self, quantity=1.0):
        if self.quantity_hand:
            return
        self.quantity_hand = quantity
        self.save()

    @appier.operation(name="Ensure Price", level=2, devel=True)
    def ensure_price_s(self, price=100.0):
        if self.price:
            return
        self.price = price
        self.save()

    @appier.operation(name="Notify", parameters=(("Email", "email", str),))
    def notify(self, name=None, *args, **kwargs):
        name = name or "product.new"
        product = self.reload(map=True)
        receiver = kwargs.get("email", None)
        appier_extras.admin.Event.notify_g(
            name,
            arguments=dict(
                params=dict(
                    payload=product, product=product, receiver=receiver, extra=kwargs
                )
            ),
        )

    @appier.operation(
        name="Share",
        parameters=(
            ("Sender", "sender", appier.legacy.UNICODE),
            ("Email", "email", str),
        ),
    )
    def share(self, *args, **kwargs):
        self.notify(name="product.share", *args, **kwargs)

    @appier.operation(
        name="Quote",
        parameters=(
            ("Requester", "requester", appier.legacy.UNICODE),
            ("Email", "email", str),
            ("Phone", "phone", str),
            ("Observations", "observations", str),
        ),
    )
    def quote(self, *args, **kwargs):
        # patches the email attribute for the quote call so
        # that the receiver value can be "manipulated" by
        # configuration as it must be a admin user of the
        # store by default and not the end-user
        kwargs_quote = dict(kwargs)
        kwargs_quote["_email"] = kwargs_quote.pop("email", None)

        # runs the notification process for the product quote making
        # sure that all of the notification names are used
        self.notify(name="product.quote", *args, **kwargs_quote)
        self.notify(name="product.quote.confirmation", *args, **kwargs)

    @appier.view(name="Measurements")
    def measurements_v(self, *args, **kwargs):
        kwargs["sort"] = kwargs.get("sort", [("id", 1)])
        return appier.lazy_dict(
            model=self.measurements._target,
            kwargs=kwargs,
            entities=appier.lazy(lambda: self.measurements.find(*args, **kwargs)),
            page=appier.lazy(lambda: self.measurements.paginate(*args, **kwargs)),
        )

    @property
    def quantity(self):
        return self.quantity_hand

    @property
    def discount(self):
        if not self.price:
            return commons.Decimal(0.0)
        if not self.price_compare:
            return commons.Decimal(0.0)
        return self.price_compare - self.price

    @property
    def discount_percent(self):
        if not self.discount:
            return commons.Decimal(0.0)
        return self.discount / self.price_compare * commons.Decimal(100.0)

    @property
    def is_parent(self):
        if not hasattr(self, "measurements"):
            return False
        if not self.measurements:
            return False
        return len(self.measurements) > 0

    @property
    def is_discounted(self):
        return self.discount > 0.0

    @property
    def is_discountable(self):
        return self.discountable

    @property
    def is_price_provided(self):
        return True if self.price_provider else False

    def _reset_labels(self):
        self.labels = []

    def _build_labels(self, groups):
        if not isinstance(groups, (list, tuple, appier.References)):
            groups = (groups,) if groups else []
        for group in groups:
            for label in group.labels:
                if label in self.labels:
                    continue
                self.labels.append(label)

    def _get_offset(self, count, limit, kwargs):
        return self._get_offset_offset(count, limit, kwargs)

    def _get_offset_simple(self, count, limit, kwargs):
        return self.id % count

    def _get_offset_offset(self, count, limit, kwargs):
        cls = self.__class__
        kwargs = dict(kwargs)
        kwargs["id"] = {"$lt": self.id}
        offset = cls.count(**kwargs)
        return offset
