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
from . import media
from . import order
from . import product
from . import referral
from . import root
from . import subscription
from . import voucher

from .account import AccountApiController
from .address import AddressApiController
from .bag import BagApiController
from .base import BaseApiController
from .brand import BrandApiController
from .category import CategoryApiController
from .collection import CollectionApiController
from .color import ColorApiController
from .country import CountryApiController
from .currency import CurrencyApiController
from .easypay import EasypayApiController
from .media import MediaApiController
from .order import OrderApiController
from .product import ProductApiController
from .referral import ReferralApiController
from .root import RootApiController
from .subscription import SubscriptionApiController
from .voucher import VoucherApiController
