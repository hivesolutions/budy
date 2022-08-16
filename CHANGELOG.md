# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

* Support for merging of sale lines for same merchandise object ID in `import_omni()`

### Changed

*

### Fixed

*

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
