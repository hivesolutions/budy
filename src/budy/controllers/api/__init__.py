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

__copyright__ = "Copyright (c) 2008-2024 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

from . import account
from . import address
from . import bag
from . import base
from . import brand
from . import category
from . import collection
from . import color
from . import country
from . import currency
from . import easypay
from . import easypay_v2
from . import media
from . import order
from . import product
from . import referral
from . import root
from . import section
from . import seeplus
from . import store
from . import subscription
from . import voucher

from .account import AccountAPIController
from .address import AddressAPIController
from .bag import BagAPIController
from .base import BaseAPIController
from .brand import BrandAPIController
from .category import CategoryAPIController
from .collection import CollectionAPIController
from .color import ColorAPIController
from .country import CountryAPIController
from .currency import CurrencyAPIController
from .easypay import EasypayAPIController
from .easypay_v2 import EasypayV2APIController
from .media import MediaAPIController
from .order import OrderAPIController
from .product import ProductAPIController
from .referral import ReferralAPIController
from .root import RootAPIController
from .season import SeasonAPIController
from .section import SectionAPIController
from .seeplus import SeeplusAPIController
from .store import StoreAPIController
from .subscription import SubscriptionAPIController
from .voucher import VoucherAPIController
