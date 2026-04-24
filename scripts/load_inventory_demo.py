#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Demo data loader utility that populates a Budy instance with sample
products, addresses and orders for exercising the inventory report at
`/api/orders/inventory`.

Creates a small catalog of products spread across genders, and a set
of orders (mostly paid, a few still unpaid) with multiple lines per
order, including the same product with different sizes and the same
product across different orders, so that the row explosion and
ordering behavior of the inventory report can be verified end-to-end.

Run from the project root:

    python scripts/load_inventory_demo.py --verbose

The script appends to the currently configured MongoDB database. No
existing data is removed.
"""

import logging
import random

from sys import exit
from traceback import print_exc
from argparse import ArgumentParser, Namespace

import appier

import budy


class InventoryDemoLoader:
    """
    Demo data loader that populates a Budy instance with a small set
    of products and orders, tailored to exercise the inventory report.
    """

    PRODUCTS = (
        dict(
            sku="SHIRT-BLUE",
            short_description="Blue Cotton Shirt",
            gender="Male",
            price=29.9,
            quantity_hand=100.0,
            thumbnail_url="https://picsum.photos/seed/SHIRT-BLUE/120/120",
            image_url="https://picsum.photos/seed/SHIRT-BLUE/600/600",
        ),
        dict(
            sku="JEANS-SLIM",
            short_description="Slim Fit Jeans",
            gender="Male",
            price=59.9,
            quantity_hand=100.0,
            thumbnail_url="https://picsum.photos/seed/JEANS-SLIM/120/120",
            image_url="https://picsum.photos/seed/JEANS-SLIM/600/600",
        ),
        dict(
            sku="DRESS-RED",
            short_description="Red Summer Dress",
            gender="Female",
            price=79.9,
            quantity_hand=100.0,
            thumbnail_url="https://picsum.photos/seed/DRESS-RED/120/120",
            image_url="https://picsum.photos/seed/DRESS-RED/600/600",
        ),
        dict(
            sku="SKIRT-BLACK",
            short_description="Black Pencil Skirt",
            gender="Female",
            price=49.9,
            quantity_hand=100.0,
            thumbnail_url="https://picsum.photos/seed/SKIRT-BLACK/120/120",
            image_url="https://picsum.photos/seed/SKIRT-BLACK/600/600",
        ),
        dict(
            sku="TSHIRT-KIDS",
            short_description="Kids Striped T-Shirt",
            gender="Child",
            price=14.9,
            quantity_hand=100.0,
            thumbnail_url="https://picsum.photos/seed/TSHIRT-KIDS/120/120",
            image_url="https://picsum.photos/seed/TSHIRT-KIDS/600/600",
        ),
        dict(
            sku="HOODIE-GREY",
            short_description="Grey Cotton Hoodie",
            gender="Both",
            price=39.9,
            quantity_hand=100.0,
            thumbnail_url="https://picsum.photos/seed/HOODIE-GREY/120/120",
            image_url="https://picsum.photos/seed/HOODIE-GREY/600/600",
        ),
    )
    """ The catalog of demo products, spread across the supported
    genders and with enough on-hand stock to absorb any order mix """

    SIZES = (36, 38, 40, 42, 44)
    """ The set of sizes randomly assigned to order lines, picked
    small enough so that collisions across lines are common """

    def __init__(
        self,
        orders_count=12,
        paid_ratio=0.75,
        seed=42,
        verbose=True,
    ):
        """
        Initializes the inventory demo loader.

        :param orders_count: The total number of orders to create.
        :param paid_ratio: The fraction of orders that are marked paid.
        :param seed: The seed for the pseudo random generator, so that
        successive runs produce a deterministic data set.
        :param verbose: Whether to print verbose output.
        """

        self.orders_count = orders_count
        self.paid_ratio = paid_ratio
        self.random = random.Random(seed)
        self.verbose = verbose
        self.app = None
        self.products = []

    def log(self, message, level="INFO"):
        """
        Logs a message if verbose mode is enabled.

        :param message: The message to log.
        :param level: The level of the message.
        """

        if not self.verbose:
            return
        for part in message.split("\n"):
            print("[%s] %s" % (level, part))

    def init_app(self):
        """
        Initializes the underlying Budy application so that model
        operations can be executed against the configured database.
        """

        self.log("Initializing Budy application...")
        self.app = budy.BudyApp(level=logging.ERROR)
        self.log("Budy application initialized successfully")

    def stop_app(self):
        """
        Unloads the Budy application, ensuring that any open
        resources (scheduler, database connection) are released.
        """

        if self.app == None:
            return
        self.app.unload()
        self.app = None

    def load_products(self):
        """
        Loads the demo products into the database.
        """

        self.log("=" * 60)
        self.log("Loading Products")
        self.log("=" * 60)
        for product_data in self.PRODUCTS:
            base_data = {
                key: value
                for key, value in product_data.items()
                if key not in ("thumbnail_url", "image_url")
            }
            product = budy.Product(**base_data)
            product.save()
            self.products.append(product)
            self.log("  + Created Product: %s (%s)" % (product.sku, product.gender))

    def load_orders(self):
        """
        Loads the demo orders into the database, creating a mix of
        paid and unpaid orders and exploding multi-size product
        combinations across the generated lines.
        """

        self.log("\n" + "=" * 60)
        self.log("Loading Orders")
        self.log("=" * 60)
        paid_count = int(round(self.orders_count * self.paid_ratio))
        for index in range(self.orders_count):
            paid = index < paid_count
            self._create_order(index, paid)

    def load_product_images(self):
        """
        Applies the pre-defined thumbnail and full-size image URLs to
        each product by bypassing the normal save pipeline, so that
        the URLs survive the inventory decrement pass that re-saves
        the referenced products and would otherwise clear them.
        """

        self.log("\n" + "=" * 60)
        self.log("Loading Product Images")
        self.log("=" * 60)
        collection = budy.Product._collection()
        by_sku = dict(
            (product_data["sku"], product_data) for product_data in self.PRODUCTS
        )
        for product in self.products:
            data = by_sku.get(product.sku, {})
            thumbnail_url = data.get("thumbnail_url")
            image_url = data.get("image_url")
            if not thumbnail_url and not image_url:
                continue
            collection.update(
                dict(id=product.id),
                {"$set": dict(thumbnail_url=thumbnail_url, image_url=image_url)},
            )
            product.thumbnail_url = thumbnail_url
            product.image_url = image_url
            self.log("  + Applied Images: %s" % product.sku)

    def _create_order(self, index, paid):
        """
        Creates a single demo order with a random set of lines and,
        if requested, marks it as paid so that it shows up under the
        default `paid=True` filter of the inventory report.

        :param index: The sequential index of the order being created,
        used for logging purposes only.
        :param paid: Whether the order should end up in the paid state.
        """

        order = budy.Order()
        order.save()

        lines_count = self.random.randint(2, 4)
        selected_products = self.random.sample(
            self.products, min(lines_count, len(self.products))
        )
        for product in selected_products:
            self._add_line(order, product)
            if self.random.random() < 0.35:
                self._add_line(order, product)

        address = budy.Address(
            first_name="Demo",
            last_name="Customer %d" % (index + 1),
            address="Rua Demo %d" % (index + 1),
            city="Lisboa",
            postal_code="1000-001",
            country="PT",
            phone_number="+351910000000",
        )
        address.save()

        order.shipping_address = address
        order.billing_address = address
        order.email = "demo%d@budy.test" % (index + 1)
        order.save()

        if not paid:
            self.log(
                "  + Created Order: %s (%d lines, unpaid)"
                % (order.reference, len(order.lines))
            )
            return

        order.mark_waiting_payment_s()
        order.mark_paid_s()
        self.log(
            "  + Created Order: %s (%d lines, paid)"
            % (order.reference, len(order.lines))
        )

    def _add_line(self, order, product):
        """
        Appends a new order line for the given product into the
        provided order, assigning a random quantity and size.

        :param order: The order that will own the new line.
        :param product: The product associated with the new line.
        """

        line = budy.OrderLine(quantity=float(self.random.randint(1, 3)))
        line.product = product
        line.size = self.random.choice(self.SIZES)
        line.size_s = str(line.size)
        line.save()
        order.add_line_s(line)

    def load_all_data(self):
        """
        Loads all demo data into the database, ensuring that
        dependencies are loaded in the correct order.
        """

        self.log("\n" + "=" * 60)
        self.log("Budy Inventory Demo Loader")
        self.log("=" * 60)

        try:
            self.init_app()
            self.load_products()
            self.load_orders()
            self.load_product_images()
            self.log("\n" + "=" * 60)
            self.log("Demo Data Loading Complete!")
            self.log("=" * 60)
            self.log("\nSummary:")
            self.log("  - Products created: %d" % len(self.products))
            self.log("  - Orders created: %d" % self.orders_count)
            return True
        except Exception as exception:
            self.log("Error loading demo data: %s" % exception, "ERROR")
            print_exc()
            return False
        finally:
            self.stop_app()


def parse_args():
    """
    Parses command line arguments.
    """

    parser = ArgumentParser(
        description="Load inventory demo data into a local Budy instance"
    )
    parser.add_argument(
        "--orders",
        type=int,
        default=12,
        help="Number of orders to create (default: 12)",
    )
    parser.add_argument(
        "--paid-ratio",
        type=float,
        default=0.75,
        help="Fraction of orders that should be marked paid (default: 0.75)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Seed for the pseudo random generator (default: 42)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    return parser.parse_args()


def main():
    """
    Main entry point for the CLI.
    """

    args = parse_args()
    loader = InventoryDemoLoader(
        orders_count=args.orders,
        paid_ratio=args.paid_ratio,
        seed=args.seed,
        verbose=args.verbose,
    )
    success = loader.load_all_data()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
