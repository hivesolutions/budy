# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

*

### Changed

*

### Fixed

* Issues with the processing of MBWay

## [0.8.12] - 2025-01-03

### Changed

* Minimal support for MBWay

## [0.8.11] - 2024-12-31

### Added

* Additional validation to status changed in order for Seeplus, more pedantic
* Support for Easypay V2 integration

### Changed

* Made code compliant with black

## [0.8.10] - 2024-01-04

### Changed

* Bumping Appier version

## [0.8.9] - 2023-12-23

### Changed

* Added the `store` field to the "To Store" views

## [0.8.8] - 2023-12-23

### Added

* New views for "To Store" and "To Store Paid" handling

## [0.8.7] - 2023-12-23

### Added

* Support for automatic fill of Seeplus fulfillment and delivery data

## [0.8.6] - 2023-12-13

### Added

* Support for `fix_lines_s()` in `Bundle`

## [0.8.5] - 2023-06-29

### Fixed

* Bumped `appier` version

## [0.8.4] - 2023-06-01

### Added

* Support for `Mechandise` level import in Seeplus

## [0.8.3] - 2023-05-31

### Changed

* Bumped appier

## [0.8.2] - 2023-05-30

### Changed

* Bumped appier

## [0.8.1] - 2023-05-07

### Changed

* Unset of store by default when doing new shipping address

## [0.8.0] - 2023-05-03

### Added

* Support for `None` values in `Order` decrement inventory
* Support for the `store` API endpoints
* Support for the `set_store()` method in `Order`

## [0.7.13] - 2023-04-21

### Added

* Support for auto-decrement of stock on payment of `Order` using the `inventory_decremented` flag

## [0.7.12] - 2023-03-31

### Added

* Support for log of states in Seeplus update operation

## [0.7.11] - 2023-03-21

### Fixed

* Made part of the customer options optional in `Order`

## [0.7.10] - 2023-03-20

### Added

* Support for the `key` and `token` field for the secret key values

## [0.7.9] - 2023-03-20

### Fixed

* Validation of Seeplus integration

## [0.7.8] - 2023-03-20

### Fixed

* Variable naming typo

## [0.7.7] - 2023-03-20

### Added

* Support for Seeplus Order import operation
* Support for Webhook like update call from Seeplus at POST `/api/seeplus/update`
* Support for the `X-Seeplus-Key` authentication model

## [0.7.6] - 2022-08-29

### Added

* Support for merging of sale lines for same merchandise object ID in `import_omni()`

### Changed

* Support for observations in quote operation

## [0.7.5] - 2022-08-17

### Added

* Support for merging of sale lines for same merchandise object ID in `import_omni()`

## [0.7.4] - 2022-08-12

### Changed

* Removed `phone` from mandatory fields in product quote

## [0.7.3] - 2022-08-11

### Fixed

* Orderable quantity fix

## [0.7.2] - 2022-08-05

### Changed

* Usage of the `prefix` param in `url_for` avoiding possible race conditions

### Fixed

* Added "hack" to force `quantity_hand` greater than zero in orderable scenarios

## [0.7.1] - 2022-06-25

### Added

* Better logging support for the sync operation

## [0.7.0] - 2022-06-25

### Added

* Support for more information in order notes
* New `product.quote` and `product.quote.confirmation` events added

## [0.6.3] - 2021-05-03

### Fixed

* Python 3 syntax issue

## [0.6.2] - 2021-05-03

### Added

* Support for more information in order notes

## [0.6.1] - 2021-07-05

### Added

* Optional `OrderLine` attributes import as sale line metadata on Omni

## [0.6.0] - 2021-07-05

### Added

* Support for `features` in the `Product` model

### Changed

* Changed default value of `sync_prices` to `True` in `Order.import_omni_s`

## [0.5.1] - 2021-03-15

### Added

* Usage of discount operation for price setting in Omni `Order` import

## [0.5.0] - 2021-03-14

### Added

* Support for the `invoiced` state at the `Order` model
* Storage of `company_product_code` inside `Product` and `Measurement` on import data
* Support for price fixing on Omni import

## [0.4.2] - 2021-02-25

### Fixed

* Another version related issue

## [0.4.1] - 2021-02-25

### Fixed

* Small issue with pypi release

## [0.4.0] - 2021-02-25

### Added

* The field `title` to the `Group` model

## [0.3.4] - 2021-02-24

### Added

* Support for heuristic to determine the best name for account creation in Omni import

## [0.3.3] - 2021-02-24

### Fixed

* Issue related with bad import of Omni regarding `merchandise`

## [0.3.2] - 2021-02-21

### Added

* Support for gender and birth date integration in Omni orders
* Omni sale identified stored in order's metadata
* Support for notes metadata append, referencing budy order in Omni's money sale slip

### Changed

* Default payment method on Omni import to `CardPayment`

## [0.3.1] - 2021-02-21

### Added

* Support for gift wrap and shipping in import operation

## [0.3.0] - 2021-02-21

### Added

* More description to the status page
* Automatic VAT number update for customer upon Omni import
* Support for invoice issue in Omni import
* "Marking" of `Order` entity with metadata related to the Omni import

## [0.2.1] - 2021-02-20

### Added

* City and country support in Omni order import

## [0.2.0] - 2021-02-20

### Added

* Support for order importing in Omni
