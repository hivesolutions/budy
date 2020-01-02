#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Budy
# Copyright (c) 2008-2020 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2020 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import appier
import appier_extras

from . import bundle
from . import wishlist_line

class Wishlist(bundle.Bundle):

    lines = appier.field(
        type = appier.references(
            "WishlistLine",
            name = "id"
        ),
        eager = True
    )

    account = appier.field(
        type = appier.reference(
            "BudyAccount",
            name = "id"
        ),
        eager = True
    )

    @classmethod
    def list_names(cls):
        return ["id", "key", "total", "currency", "account"]

    @classmethod
    def line_cls(cls):
        return wishlist_line.WishlistLine

    @classmethod
    def from_session(cls, ensure = True, raise_e = False):
        from . import BudyAccount
        account = BudyAccount.from_session(raise_e = raise_e)
        if account: return account.ensure_wishlist_s()
        session = appier.get_session()
        key = session.get("wishlist", None)
        wishlist = cls.get(key = key, raise_e = raise_e) if key else None
        if wishlist: return wishlist
        if not ensure: return None
        wishlist = cls()
        wishlist.save()
        session["wishlist"] = wishlist.key
        return wishlist

    @classmethod
    def ensure_s(cls, key = None):
        from . import BudyAccount
        account = BudyAccount.from_session(raise_e = False)
        if account: return account.ensure_wishlist_s(key = key)
        wishlist = cls(key = key)
        wishlist.save()
        return wishlist

    def pre_validate(self):
        bundle.Bundle.pre_validate(self)
        self.try_valid()

    def pre_delete(self):
        bundle.Bundle.pre_delete(self)
        for line in self.lines: line.delete()

    def add_line_s(self, line):
        line.wishlist = self
        return bundle.Bundle.add_line_s(self, line)

    @appier.operation(name = "Garbage Collect")
    def collect_s(self):
        self.delete()

    @appier.operation(name = "Fix Orphans")
    def fix_orphans_s(self):
        for line in self.lines:
            line.wishlist = self
            line.save()

    @appier.operation(name = "Notify")
    def notify(self, name = None, *args, **kwargs):
        name = name or "wishlist.new"
        wishlist = self.reload(map = True)
        account = wishlist.get("account", {})
        account = kwargs.get("account", account)
        receiver = account.get("email", None)
        receiver = kwargs.get("email", receiver)
        appier_extras.admin.Event.notify_g(
            name,
            arguments = dict(
                params = dict(
                    payload = wishlist,
                    wishlist = wishlist,
                    receiver = receiver,
                    extra = kwargs
                )
            )
        )

    @appier.operation(name = "Remind")
    def remind(self):
        self.notify("wishlist.remind")
