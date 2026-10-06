"""The checkout flow, including the totals arithmetic."""

import allure
import pytest
from playwright.sync_api import expect

from pages.checkout_pages import CheckoutOverviewPage
from pages.inventory_page import InventoryPage

pytestmark = [pytest.mark.ui, allure.feature("Checkout")]

BACKPACK = "sauce-labs-backpack"
FLEECE_JACKET = "sauce-labs-fleece-jacket"

TAX_RATE = 0.08

BUYER = ("Grigoriy", "Khokhlov", "111222")


def overview_for(inventory: InventoryPage, *products: str) -> CheckoutOverviewPage:
    """Carry `products` as far as the order summary."""
    for product in products:
        inventory.add_to_cart(product)
    return inventory.open_cart().checkout().complete(*BUYER)


@allure.story("Happy path")
@pytest.mark.smoke
def test_an_order_can_be_placed_end_to_end(inventory: InventoryPage):
    complete = overview_for(inventory, BACKPACK).finish()

    expect(complete.header).to_contain_text("Thank you for your order")


@allure.story("Totals")
def test_the_subtotal_matches_the_line_items(inventory: InventoryPage):
    overview = overview_for(inventory, BACKPACK, FLEECE_JACKET)

    assert overview.subtotal() == pytest.approx(overview.item_total())


@allure.story("Totals")
def test_tax_and_total_are_derived_from_the_subtotal(inventory: InventoryPage):
    overview = overview_for(inventory, BACKPACK, FLEECE_JACKET)
    subtotal = overview.subtotal()

    assert overview.tax() == pytest.approx(round(subtotal * TAX_RATE, 2), abs=0.01)
    assert overview.total() == pytest.approx(subtotal + overview.tax(), abs=0.01)


@allure.story("Form validation")
@pytest.mark.parametrize(
    ("first_name", "last_name", "postal_code", "message"),
    [
        ("", "Khokhlov", "111222", "First Name is required"),
        ("Grigoriy", "", "111222", "Last Name is required"),
        ("Grigoriy", "Khokhlov", "", "Postal Code is required"),
        ("", "", "", "First Name is required"),
    ],
    ids=["no-first-name", "no-last-name", "no-postal-code", "empty-form"],
)
def test_incomplete_details_are_rejected(
    inventory: InventoryPage,
    first_name,
    last_name,
    postal_code,
    message,
):
    information = inventory.add_to_cart(BACKPACK).open_cart().checkout()
    information.fill_details(first_name, last_name, postal_code)
    information.submit_expecting_rejection()

    expect(information.error).to_contain_text(message)
