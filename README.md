# [Budy](http://budy.hive.pt)

Simple E-commerce infra-structure, able to provide a simple experience equivalent to that
of platforms like [Shopify](http://www.shopify.com).

## Design

The main goal of the project is to provide a simple platform for e-commerce that does not
take care of all the transactional details like:

* [ACID](http://en.wikipedia.org/wiki/ACID) compliant transactions/operations
* Financial secure transactions
* Secure customer data

## Unit Testing

Test driven development should be a concern on the development of the Budy infra-structure
so that all the use cases are proper validated before implementation.

Code coverage of at least 75% of the code base should be considered a priority.

## Configuration

### General

| Name                       | Type   | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| -------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **BUDY_CURRENCY**          | `str`  | The currency to be "forced" for financial operations, this value is not set by default an automatic algorithm is used instead, to determine the best possible match for the currency to be used, use this value only for situations where binding a currency value is required (defaults to `None`).                                                                                                                                                                                    |
| **BUDY_ORDER_REF**         | `str`  | Defines the template to be used for order reference number generation (defaults to `BD-%06d`).                                                                                                                                                                                                                                                                                                                                                                                          |
| **BUDY_DISCOUNT**          | `str`  | String with the definition of the lambda function to be called for calculus of the discount value for a bundle (bag or order) the arguments provided are the discountable, taxes, quantity and bundle and the return value should be a valid float value for the discount (defaults to `None`).                                                                                                                                                                                         |
| **BUDY_JOIN_DISCOUNT**     | `bool` | If both the voucher and the base discount values should be applied at the same time for an order and/or bag or if instead only the largest of both should be used (defaults to `True`).                                                                                                                                                                                                                                                                                                 |
| **BUDY_FULL_DISCOUNTABLE** | `bool` | If the discountable value (value eligible to be discounted) should use the sub total amount including lines with line level discount together with the shipping costs, meaning that an end customer may not pay the shipping costs at all (if the discount covers that value) and also benefit from double discount (line and global level) or if otherwise only the sub total with no line level discount (and without shipping costs) is eligible for discount (defaults to `False`). |
| **BUDY_SHIPPING**          | `str`  | String with the definition of the lambda function to be called for calculus of the shipping costs for a bundle (bag or order) the arguments provided are the sub total, taxes, quantity and bundle and the return value should be a valid float value for the shipping costs (defaults to `None`).                                                                                                                                                                                      |
| **BUDY_JOIN_SHIPPING**     | `bool` | If both the order and/or bag static shipping value and the order and/or bag dynamic shipping value should be summed to calculate the total shipping cost or if instead only the largest of both should be used (defaults to `True`).                                                                                                                                                                                                                                                    |
| **BUDY_TAXES**             | `str`  | String with the definition of the lambda function to be called for calculus of the taxes for a bundle (bag or order) the arguments provided are the sub total, taxes, quantity and bundle and the return value should be a valid float value for the total taxes (defaults to `None`).                                                                                                                                                                                                  |
| **BUDY_JOIN_TAXES**        | `bool` | If both the order and/or bag line taxes (static) and the dynamic order and/or bag taxes should be summed to calculate the total taxes or if instead only the largest of both should be used (defaults to `True`).                                                                                                                                                                                                                                                                       |

### Payments

| Name                   | Type   | Description                                                                                                                                                                                                                                                            |
| ---------------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **BUDY_STRIPE_LEGACY** | `bool` | If the legacy mode (old Stripe API no credit card sources) should be used (defaults to `False`).                                                                                                                                                                       |
| **BUDY_3D_SECURE**     | `bool` | If the [3-D Secure](https://en.wikipedia.org/wiki/3-D_Secure) mode should be enabled for cards that require or support that mode of execution, note that "normal" card execution mode will be applied for cards that do not support this method (defaults to `False`). |
| **BUDY_3D_ENSURE**     | `bool` | If the [3-D Secure](https://en.wikipedia.org/wiki/3-D_Secure) mode is enabled, forces all the credit card operations to be performed using the 3-D Secure approach (defaults to `False`).                                                                              |

### Omni Bot

| Name                   | Type   | Description                                                                                     |
| ---------------------- | ------ | ----------------------------------------------------------------------------------------------- |
| **OMNI_BOT_ENABLED**   | `bool` | If the Omni bot should be enabled at startup.                                                   |
| **OMNI_BOT_STORE**     | `int`  | Object ID of the store that is going to be used for the sync and import operations.             |
| **OMNI_BOT_SHIPPING**  | `int`  | Object ID of the shipping service that is going to be used for the sync and import operations.  |
| **OMNI_BOT_GIFT_WRAP** | `int`  | Object ID of the gift wrap service that is going to be used for the sync and import operations. |
| **OMNI_BOT_RECORDS**   | `int`  | The number of records to be retrieved per each remote API call.                                 |

### Tracking Bot

| Name                     | Type   | Description                                                                       |
| ------------------------ | ------ | --------------------------------------------------------------------------------- |
| **TRACKING_BOT_ENABLED** | `bool` | If the Tracking bot should be enabled at startup.                                 |
| **TRACKING_BOT_WINDOW**  | `int`  | The window (in seconds) to look back in terms of orders (older orders tolerance). |

### Seeplus

| Name               | Type  | Description                                                                                   |
| ------------------ | ----- | --------------------------------------------------------------------------------------------- |
| **SEEPLUS_ORIGIN** | `str` | The origin token to be used in Seeplus integration (defaults to: `63971c5c62bd0a62b956b4f3`). |
| **SEEPLUS_KEY**    | `str` | If provided offer a way to ensure shared key authentication to Webhooks.                      |

## License

Budy is currently licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/).

## Build Automation

[![Build Status](https://app.travis-ci.com/hivesolutions/budy.svg?branch=master)](https://travis-ci.com/github/hivesolutions/budy)
[![Build Status GitHub](https://github.com/hivesolutions/budy/workflows/Main%20Workflow/badge.svg)](https://github.com/hivesolutions/budy/actions)
[![Coverage Status](https://coveralls.io/repos/hivesolutions/budy/badge.svg?branch=master)](https://coveralls.io/r/hivesolutions/budy?branch=master)
[![PyPi Status](https://img.shields.io/pypi/v/budy.svg)](https://pypi.python.org/pypi/budy)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://www.apache.org/licenses/)
