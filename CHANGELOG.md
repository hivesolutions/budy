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

* Issue related with bad import of Omni regarding `mechandise`

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
