# [Budy](http://budy.hive.pt)

Simple e-commerce infra-structure, able to provide a simple experience equivalent to that
of platforms like [Shopify](http://www.shopify.com).

## Design

The main goal of the project is to provide a simple platform for e-commerce that does not
take care of all the transactional details like:

*  [ACID](http://en.wikipedia.org/wiki/ACID) compliant transactions/operations
*  Financial secure transactions
*  Secure customer data

## Unit Testing

Test driven development should be a concern on the development of the Budy infra-structure
so that all the use cases are proper validated before implementation.

Code coverage of at least 75% of the code base should be considered a priority.

## Configuration

### General

* `BUDY_CURRENCY` (`str`) - The currency to be "forced" for financial operations, this value is not
set by default an an automatic algorithm is used instead, to determine the best possible match for the
currency to be used, use this value only for situations where binding a currency value is required (defaults to `None`)
* `BUDY_ORDER_REF` (`str`) - Defines the template to be used for order reference number generation (defaults to `BD-%06d`)
* `BUDY_DISCOUNT` (`str`) - String with the definition of the lambda function to be called for calculus of the
discount value for a bundle (bag or order) the arguments provided are the discountable, taxes, quantity and bundle and the return
value should be a valid float value for the discount (defaults to `None`)
* `BUDY_JOIN_DISCOUNT` (`bool`) - If both the voucher and the base discount values should be applied at the same time for
an order and/or bag or if instead only the largest of both should be used (defaults to `True`)
* `BUDY_FULL_DISCOUNTABLE` (`bool`) - If the discountable value (value eligible to be discounted) should include both the
sub total and the shipping costs, meaning that a end customer may not pay the shipping costs at all (if the discount covers that
value) or if otherwise only the sub total is eligible for discount (defaults to `False`)
* `BUDY_SHIPPING` (`str`) - String with the definition of the lambda function to be called for calculus of the
shipping costs for a bundle (bag or order) the arguments provided are the sub total, taxes, quantity and bundle and the return
value should be a valid float value for the shipping costs (defaults to `None`)
* `BUDY_JOIN_SHIPPING` (`bool`) - If both the order and/or bag static shipping value and the order and/or bag dynamic shipping value
should be summed to calculate the total shipping cost or if instead only the largest of both should be used (defaults to `True`)
* `BUDY_TAXES` (`str`) - String with the definition of the lambda function to be called for calculus of the
taxes for a bundle (bag or order) the arguments provided are the sub total, taxes, quantity and bundle and the return
value should be a valid float value for the total taxes (defaults to `None`)
* `BUDY_JOIN_TAXES` (`bool`) - If both the order and/or bag line taxes (static) and the dynamic order and/or bag taxes should
be summed to calculate the total taxes or if instead only the largest of both should be used (defaults to `True`)

### Payments

* `BUDY_STRIPE_LEGACY` (`bool`) - If the legacy mode (old Stripe API) should be used (defaults to `False`)
* `BUDY_3D_SECURE` (`bool`) - If the [3-D Secure](https://en.wikipedia.org/wiki/3-D_Secure) mode should be enabled for cards that
require or support that mode of execution, note that "normal" card execution mode will be applied for cards that do not support
this method (defaults to `False`)
* `BUDY_3D_ENSURE` (`bool`) - If the [3-D Secure](https://en.wikipedia.org/wiki/3-D_Secure) mode is enabled, forces all the credit
card operations to be performed using the 3-D Secure approach (defaults to `False`)

### Bots

* `OMNI_BOT_ENABLED` (`bool`) - If the Omni bot should be enabled at startup
* `OMNI_BOT_STORE` (`int`) - Object ID of the store that is going to be used for the sync operation
* `OMNI_BOT_RECORDS` (`int`) - The number of records to be retrieved per each remote API call

## License

Budy is currently licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/).

## Build Automation

[![Build Status](https://travis-ci.org/hivesolutions/budy.svg?branch=master)](https://travis-ci.org/hivesolutions/budy)
[![Coverage Status](https://coveralls.io/repos/hivesolutions/budy/badge.svg?branch=master)](https://coveralls.io/r/hivesolutions/budy?branch=master)
[![PyPi Status](https://img.shields.io/pypi/v/budy.svg)](https://pypi.python.org/pypi/budy)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://www.apache.org/licenses/)
