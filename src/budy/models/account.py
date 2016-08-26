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
import appier_extras

from . import bag

class BudyAccount(appier_extras.admin.Account):

    PREFIXES = appier_extras.admin.Account.PREFIXES + [
        "budy."
    ]

    GENDER_S = dict(
        Male = "Male",
        Female = "Female"
    )

    first_name = appier.field(
        index = True
    )

    last_name = appier.field(
        index = True
    )

    gender = appier.field(
        meta = "enum",
        enum = GENDER_S
    )

    birth_date = appier.field(
        type = int,
        index = True,
        meta = "date"
    )

    country = appier.field(
        meta = "country"
    )

    phone_number = appier.field()

    receive_newsletters = appier.field(
        type = bool,
        initial = False
    )

    avatar = appier.field(
        type = appier.image(
            width = 400,
            height = 400,
            format = "png"
        ),
        private = True
    )

    store = appier.field(
        type = appier.reference(
            "Store",
            name = "id"
        ),
        eager = True
    )

    addresses = appier.field(
        type = appier.references(
            "Address",
            name = "id"
        )
    )

    @classmethod
    def _build(cls, model, map):
        id = model.get("id", None)
        first_name = model.get("first_name", None)
        last_name = model.get("last_name", None)
        full_name = cls._build_full_name(first_name, last_name)
        short_name = cls._build_short_name(first_name, last_name)
        if id: model["bag_key"] = cls._get_bag_key(id)
        if full_name: model["full_name"] = full_name
        if short_name: model["short_name"] = short_name

    @classmethod
    def _get_bag_key(cls, id):
        _bag = bag.Bag.get(account = id, raise_e = False)
        if not _bag: return None
        return _bag.key

    @classmethod
    def _build_full_name(cls, first_name, last_name):
        first_name = first_name or ""
        last_name = last_name or ""
        return first_name + (" " + last_name if last_name else "")

    @classmethod
    def _build_short_name(cls, first_name, last_name, limit = 16):
        first_name = first_name or ""
        last_name = last_name or ""
        first = first_name.split(" ")[0].strip()
        last = last_name.split(" ")[-1].strip()
        short_name = first + (" " + last if last else "")
        if len(short_name) <= limit: return short_name
        last = last_name[0] + "." if last_name else ""
        return first + (" " + last if last else "")

    @classmethod
    @appier.operation(
        name = "Import Social CSV",
        parameters = (
            ("CSV File", "file", "file"),
            ("Strict", "strict", bool, False)
        )
    )
    def import_social_csv_s(cls, file, strict):

        def callback(line):
            username, facebook_id, google_id = line
            account = cls.get(username = username, raise_e = strict)
            if not account: return
            if facebook_id: account.facebook_id = facebook_id
            if google_id: account.google_id = google_id
            account.save()

        cls._csv_import(file, callback)

    @classmethod
    @appier.link(name = "Export Simple")
    def simple_csv_url(cls, absolute = False):
        return appier.get_app().url_for(
            "account_api.simple_csv",
            absolute = absolute
        )

    def pre_create(self):
        appier_extras.admin.Account.pre_create(self)
        if not hasattr(self, "first_name") or not self.first_name:
            self.first_name = self.username
        if not hasattr(self, "avatar") or not self.avatar:
            self._set_avatar_d()

    def post_create(self):
        appier_extras.admin.Account.post_create(self)
        self.ensure_bag_s()
        self.notify()

    def recover_s(self, send_email = False):
        result = appier_extras.admin.Account.recover_s(
            self,
            send_email = send_email
        )
        self.notify("account.recover")
        return result

    def ensure_bag_s(self, key = None):
        _bag = self.get_bag()
        if _bag: return _bag
        _bag = bag.Bag(key = key)
        _bag.account = self
        _bag.save()
        return _bag

    def get_bag(self):
        return bag.Bag.get(account = self.id, raise_e = False)

    @appier.operation(
        name = "Set Store",
        parameters = (
            (
                "Store",
                "store",
                appier.reference("Store", name = "id")
            ),
        )
    )
    def set_store_s(self, store):
        if not store: return
        self.store = store
        self.save()

    @appier.operation(name = "Notify")
    def notify(self, name = None, *args, **kwargs):
        name = name or "account.new"
        account = self.reload(rules = False, map = True)
        receiver = account.get("email", None)
        receiver = kwargs.get("email", receiver)
        appier_extras.admin.Event.notify_g(
            name,
            arguments = dict(
                params = dict(
                    payload = account,
                    account = account,
                    receiver = receiver,
                    extra = kwargs
                )
            )
        )

    @property
    def title(self):
        return "Mrs." if self.gender == "Female" else "Mr."

    def _set_avatar_d(self, image = "avatar.png", mime = "image/png"):
        app = appier.get_app()

        file = open(app.static_path + "/images/" + image, "rb")
        try: data = file.read()
        finally: file.close()

        file_t = (image, mime, data)
        self.avatar = appier.File(file_t)
