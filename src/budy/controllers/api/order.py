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

import appier

import budy

from . import root


class OrderAPIController(root.RootAPIController):
    @appier.route("/api/orders", "GET", json=True)
    @appier.ensure(token="admin")
    def list(self):
        object = appier.get_object(alias=True, find=True, sort=[("id", -1)])
        orders = budy.Order.find(eager_l=True, map=True, **object)
        return orders

    @appier.route("/api/orders/complex.csv", "GET")
    @appier.ensure(token="admin")
    def complex_csv(self):
        start = self.field("start", cast=int)
        end = self.field("end", cast=int)
        paid = self.field("paid", True, cast=bool)
        object = appier.get_object(alias=True, find=True, limit=0, sort=[("id", -1)])
        id = object.get("id", {})
        if start:
            id["$gte"] = start
        if end:
            id["$lte"] = end
        if start or end:
            object["id"] = id
        if paid:
            object["paid"] = True
        orders = budy.Order.find(**object)
        orders_s = [
            (
                "id",
                "reference",
                "date",
                "status",
                "email",
                "account",
                "store",
                "product",
                "gender",
                "size",
                "quantity",
                "total",
                "taxes",
                "currency",
                "first_name",
                "last_name",
                "billing_address",
                "billing_city",
                "billing_state",
                "billing_postal_code",
                "billing_country",
                "billing_phone",
                "shipping_address",
                "shipping_city",
                "shipping_state",
                "shipping_postal_code",
                "shipping_country",
                "shipping_phone",
                "shipping_cost",
            )
        ]
        for order in orders:
            for line in order.lines:
                if not line.product:
                    continue
                account = order.account
                shipping_address = order.shipping_address
                billing_address = order.billing_address
                shipping_cost = order.shipping_cost
                order_s = (
                    order.id,
                    order.reference,
                    order.created_d.strftime("%d/%m/%Y"),
                    order.status,
                    order.email,
                    account.username,
                    order.store and order.store.name,
                    line.product.short_description,
                    line.product.gender,
                    line.size,
                    line.quantity,
                    line.total,
                    line.taxes,
                    line.currency,
                    billing_address.first_name,
                    billing_address.last_name,
                    billing_address.address,
                    billing_address.city,
                    billing_address.state,
                    billing_address.postal_code,
                    billing_address.country,
                    billing_address.phone_number,
                    shipping_address and shipping_address.address,
                    shipping_address and shipping_address.city,
                    shipping_address and shipping_address.state,
                    shipping_address and shipping_address.postal_code,
                    shipping_address and shipping_address.country,
                    shipping_address and shipping_address.phone_number,
                    shipping_cost,
                )
                orders_s.append(order_s)
        result = appier.serialize_csv(orders_s, delimiter=",")
        self.content_type("text/csv")
        return result

    @appier.route("/api/orders/ctt.csv", "GET")
    @appier.ensure(token="admin")
    def ctt_csv(self):
        start = self.field("start", cast=int)
        end = self.field("end", cast=int)
        paid = self.field("paid", True, cast=bool)
        sms = self.field("sms", False, cast=bool)
        quantity = self.field("quantity", 1, cast=int)
        weight = self.field("weight", 100, cast=int)
        object = appier.get_object(alias=True, find=True, limit=0, sort=[("id", -1)])
        id = object.get("id", {})
        if start:
            id["$gte"] = start
        if end:
            id["$lte"] = end
        if start or end:
            object["id"] = id
        if paid:
            object["paid"] = True
        orders = self.admin_part._find_view(budy.Order, **object)
        orders_s = []
        for order in orders:
            shipping_address = order.shipping_address
            postal_code = shipping_address.postal_code or ""
            if not "-" in postal_code:
                postal_code += "-"
            weight_s = "%.2f" % (order.quantity * weight)
            weight_s = weight_s.replace(".", ",")
            line = dict(
                reference=order.reference,
                quantity=int(order.quantity) if quantity == None else quantity,
                weight=weight_s,
                price="0ue",
                destiny=shipping_address.full_name[:60],
                title=order.account.title[:20],
                name=shipping_address.full_name[:60],
                address=shipping_address.address[:60],
                town=shipping_address.city[:50],
                zip_code_4=postal_code.split("-", 1)[0][:4],
                zip_code_3=postal_code.split("-", 1)[1][:3],
                not_applicable_1="",
                observations="",
                back=0,
                document_code="",
                phone_number=(shipping_address.phone_number or "").replace("+", "00")[
                    :15
                ],
                saturday=0,
                email=(order.email or "")[:200],
                country=order.country,
                fragile=0,
                not_applicable_2="",
                document_collection="",
                code_email="",
                mobile_phone=(shipping_address.phone_number or "").replace("+", "00")[
                    :15
                ],
                second_delivery=0,
                delivery_date="",
                return_signed_document=0,
                expeditor_instructions=0,
                sms=1 if sms else 0,
                not_applicable_3="",
                printer="",
                ticket_machine="",
                at_code="",
            )
            order_s = (
                line["reference"],
                str(line["quantity"]),
                line["weight"],
                line["price"],
                line["destiny"],
                line["title"],
                line["name"],
                line["address"],
                line["town"],
                line["zip_code_4"],
                line["zip_code_3"],
                line["not_applicable_1"],
                line["observations"],
                str(line["back"]),
                line["document_code"],
                line["phone_number"],
                str(line["saturday"]),
                line["email"],
                line["country"],
                str(line["fragile"]),
                line["not_applicable_2"],
                line["document_collection"],
                line["code_email"],
                line["mobile_phone"],
                str(line["second_delivery"]),
                line["delivery_date"],
                str(line["return_signed_document"]),
                str(line["expeditor_instructions"]),
                str(line["sms"]),
                line["not_applicable_3"],
                line["printer"],
                line["ticket_machine"],
                line["at_code"],
            )
            orders_s.append(order_s)
        result = appier.serialize_csv(
            orders_s, encoding="Cp1252", errors="ignore", delimiter="+"
        )
        result = appier.legacy.bytes(result, encoding="Cp1252", errors="ignore")
        self.content_type("text/csv")
        return result

    @appier.route("/api/orders/<str:key>", "GET", json=True)
    def show(self, key):
        order = budy.Order.get(key=key)
        order.refresh_s(
            currency=order.payment_currency or self.currency,
            country=order.shipping_country or self.country,
        )
        order = order.reload(
            eager=("lines.product.images", "lines.product.brand"), map=True
        )
        return order

    @appier.route("/api/orders/<str:key>/store", "PUT", json=True)
    @appier.ensure(token="user")
    def set_store(self, key):
        data = appier.request_json()
        store_id = data["store_id"]
        store = budy.Store.get(id=store_id)
        order = budy.Order.get(key=key, rules=False)
        order.store = store
        order.save()
        order = order.reload(map=True)
        return order

    @appier.route("/api/orders/<str:key>/shipping_address", "PUT", json=True)
    @appier.ensure(token="user")
    def set_shipping_address(self, key):
        data = appier.request_json()
        unset_store = data.get("unset_store", True)
        address = budy.Address.new()
        address.save()
        order = budy.Order.get(key=key, rules=False)
        order.shipping_address = address
        if unset_store:
            order.store = None
        order.save()
        order = order.reload(map=True)
        return order

    @appier.route("/api/orders/<str:key>/billing_address", "PUT", json=True)
    @appier.ensure(token="user")
    def set_billing_address(self, key):
        data = appier.request_json()
        unset_store = data.get("unset_store", False)
        address = budy.Address.new()
        address.save()
        order = budy.Order.get(key=key, rules=False)
        order.billing_address = address
        if unset_store:
            order.store = None
        order.save()
        order = order.reload(map=True)
        return order

    @appier.route("/api/orders/<str:key>/store_shipping", "PUT", json=True)
    @appier.ensure(token="user")
    def set_store_shipping(self, key):
        order = budy.Order.get(key=key, rules=False)
        order.verify_store()
        store = order.store
        address = store.address.clone()
        address.save()
        order.shipping_address = address
        order.save()
        order = order.reload(map=True)
        return order

    @appier.route("/api/orders/<str:key>/store_billing", "PUT", json=True)
    @appier.ensure(token="user")
    def set_store_billing(self, key):
        order = budy.Order.get(key=key, rules=False)
        order.verify_store()
        store = order.store
        address = store.address.clone()
        address.save()
        order.billing_address = address
        order.save()
        order = order.reload(map=True)
        return order

    @appier.route("/api/orders/<str:key>/ip_address", "PUT", json=True)
    @appier.ensure(token="user")
    def set_ip_address(self, key):
        data = appier.request_json()
        ip_address = data["ip_address"]
        order = budy.Order.get(key=key, rules=False)
        order.set_ip_address_s(ip_address)
        order = order.reload(map=True)
        return order

    @appier.route("/api/orders/<str:key>/email", "PUT", json=True)
    @appier.ensure(token="user")
    def set_email(self, key):
        data = appier.request_json()
        email = data["email"]
        order = budy.Order.get(key=key, rules=False)
        order.email = email
        order.save()
        order = order.reload(map=True)
        return order

    @appier.route("/api/orders/<str:key>/gift_wrap", "PUT", json=True)
    @appier.ensure(token="user")
    def set_gift_wrap(self, key):
        data = appier.request_json()
        gift_wrap = data["gift_wrap"]
        order = budy.Order.get(key=key, rules=False)
        order.gift_wrap = gift_wrap
        order.save()
        order = order.reload(map=True)
        return order

    @appier.route("/api/orders/<str:key>/referral", "PUT", json=True)
    @appier.ensure(token="user")
    def set_referral(self, key):
        data = appier.request_json()
        referral_name = data["name"]
        order = budy.Order.get(key=key, rules=False)
        referral = budy.Referral.get(name=referral_name)
        order.set_referral_s(referral)
        order = order.reload(map=True)
        return order

    @appier.route("/api/orders/<str:key>/voucher", "PUT", json=True)
    @appier.ensure(token="user")
    def set_voucher(self, key):
        strict = self.field("strict", False, cast=bool)
        empty_vouchers = self.field("empty_vouchers", True, cast=bool)
        data = appier.request_json()
        voucher_key = data["key"]
        order = budy.Order.get(key=key, rules=False)
        if empty_vouchers:
            order.empty_vouchers_s()
        voucher = budy.Voucher.get(key=voucher_key, raise_e=strict)
        if not voucher:
            return
        order.set_voucher_s(voucher)
        order = order.reload(map=True)
        return order

    @appier.route("/api/orders/<str:key>/meta", "PUT", json=True)
    @appier.ensure(token="user")
    def set_meta(self, key):
        name = self.field("name", mandatory=True, not_empty=True)
        value = self.field("value", mandatory=True)
        order = budy.Order.get(key=key, rules=False)
        order.set_meta_s(name, value)
        order = order.reload(map=True)
        return order

    @appier.route("/api/orders/<str:key>/account", "PUT", json=True)
    @appier.ensure(token="user")
    def set_account(self, key):
        order = budy.Order.get(key=key, rules=False)
        account = budy.BudyAccount.from_session()
        order.set_account_s(account)
        order = order.reload(map=True)
        return order

    @appier.route("/api/orders/<str:key>/wait_payment", "PUT", json=True)
    @appier.ensure(token="user")
    def wait_payment(self, key):
        empty_bag = self.field("empty_bag", True, cast=bool)
        order = budy.Order.get(key=key, rules=False)
        result = order.wait_payment_s(notify=True)
        bag = budy.Bag.from_session()
        if empty_bag and bag:
            bag.empty_s()
        order = order.reload(map=True)
        redirect_url = result if appier.legacy.is_string(result) else None
        return dict(redirect_url=redirect_url, order=order)

    @appier.route("/api/orders/<str:key>/pay", "PUT", json=True)
    @appier.ensure(token="user")
    def pay(self, key):
        data = appier.request_json()
        empty_bag = self.field("empty_bag", True, cast=bool)
        order = budy.Order.get(key=key, rules=False)
        result = order.pay_s(payment_data=data, notify=True)
        bag = budy.Bag.from_session()
        if empty_bag and bag:
            bag.empty_s()
        order = order.reload(map=True)
        redirect_url = result if appier.legacy.is_string(result) else None
        return dict(redirect_url=redirect_url, order=order)

    @appier.route("/api/orders/<str:key>/end_pay", "PUT", json=True)
    @appier.ensure(token="user")
    def end_pay(self, key):
        data = appier.request_json()
        empty_bag = self.field("empty_bag", True, cast=bool)
        order = budy.Order.get(key=key, rules=False)
        result = order.end_pay_s(payment_data=data, strict=True, notify=True)
        bag = budy.Bag.from_session()
        if empty_bag and bag:
            bag.empty_s()
        order = order.reload(map=True)
        redirect_url = result if appier.legacy.is_string(result) else None
        return dict(redirect_url=redirect_url, order=order)

    @appier.route("/api/orders/<str:key>/cancel", "PUT", json=True)
    @appier.ensure(token="user")
    def cancel(self, key):
        data = appier.request_json()
        order = budy.Order.get(key=key, rules=False)
        result = order.cancel_s(data, notify=True)
        order = order.reload(map=True)
        redirect_url = result if appier.legacy.is_string(result) else None
        return dict(redirect_url=redirect_url, order=order)

    @appier.route("/api/orders/<str:key>/lines.csv", "GET")
    @appier.ensure(token="admin")
    def lines_csv(self, key):
        order = budy.Order.get(key=key)
        lines_s = [
            (
                "id",
                "product",
                "product_id",
                "quantity",
                "size",
                "scale",
                "gender",
                "line_total",
                "currency",
                "order_id",
                "order_reference",
                "order_total",
                "order_status",
                "account",
                "date",
            )
        ]
        for line in order.lines:
            if not line.product:
                continue
            line_s = (
                line.id,
                line.product.id,
                line.product.product_id,
                line.quantity,
                line.size,
                line.scale,
                line.product.gender,
                line.total,
                line.currency,
                order.id,
                order.reference,
                order.total,
                order.status,
                order.account.username,
                order.created_d.strftime("%d/%m/%Y"),
            )
            lines_s.append(line_s)

        result = appier.serialize_csv(lines_s, delimiter=",")
        self.content_type("text/csv")
        return result
