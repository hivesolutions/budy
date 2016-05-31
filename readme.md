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

* `BUDY_CURRENCY` (`str`) - The currency to be "forced" for financial operations, this value is not
set by default an an automatic algorithm is used instead, to determine the best possible match for the
currency to be used, use this value only for situations where binding a currency value is required (default to `None`)
* `BUDY_ORDER_REF` (`str`) - Defines the template to be used for order reference number generation (default to `BD-%06d`)
* `BUDY_DISCOUNT` (`str`) - String with the definition of the lambda function to be called for calculus of the
discount value for a bundle (bag or order) the arguments provided are the sub total, taxes and quantity and the return
value should be a valid float value for the discount (default to `None`)
* `BUDY_SHIPPING` (`str`) - String with the definition of the lambda function to be called for calculus of the
shipping costs for a bundle (bag or order) the arguments provided are the sub total, taxes and quantity and the return
value should be a valid float value for the shipping costs (default to `None`)

## License

Budy is currently licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/).

## Build Automation

[![Build Status](https://travis-ci.org/hivesolutions/budy.svg?branch=master)](https://travis-ci.org/hivesolutions/budy)
[![Coverage Status](https://coveralls.io/repos/hivesolutions/budy/badge.svg?branch=master)](https://coveralls.io/r/hivesolutions/budy?branch=master)
[![PyPi Status](https://img.shields.io/pypi/v/budy.svg)](https://pypi.python.org/pypi/budy)
