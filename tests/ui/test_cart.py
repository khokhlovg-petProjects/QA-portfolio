"""Adding to and removing from the cart."""

import allure
import pytest
from playwright.sync_api import expect

from pages.inventory_page import InventoryPage

pytestmark = [pytest.mark.ui, allure.feature("Cart")]

BACKPACK = "sauce-labs-backpack"
BIKE_LIGHT = "sauce-labs-bike-light"


@allure.story("Adding")
@pytest.mark.smoke
def test_adding_a_product_updates_the_badge(inventory: InventoryPage):
    inventory.add_to_cart(BACKPACK)
    expect(inventory.cart_badge).to_have_text("1")


@allure.story("Adding")
def test_the_badge_counts_every_product_added(inventory: InventoryPage):
    inventory.add_to_cart(BACKPACK).add_to_cart(BIKE_LIGHT)
    expect(inventory.cart_badge).to_have_text("2")


@allure.story("Adding")
def test_an_empty_cart_shows_no_badge(inventory: InventoryPage):
    """saucedemo removes the element rather than showing a zero."""
    expect(inventory.cart_badge).to_have_count(0)


@allure.story("Removing")
def test_removing_from_the_catalogue_empties_the_badge(inventory: InventoryPage):
    inventory.add_to_cart(BACKPACK)
    expect(inventory.cart_badge).to_have_text("1")

    inventory.remove_from_cart(BACKPACK)
    expect(inventory.cart_badge).to_have_count(0)


@allure.story("Removing")
def test_removing_inside_the_cart_empties_it(inventory: InventoryPage):
    cart = inventory.add_to_cart(BACKPACK).open_cart()
    expect(cart.items).to_have_count(1)

    cart.remove(BACKPACK)
    expect(cart.items).to_have_count(0)


@allure.story("Contents")
def test_the_cart_holds_exactly_what_was_added(inventory: InventoryPage):
    inventory.add_to_cart(BACKPACK).add_to_cart(BIKE_LIGHT)
    cart = inventory.open_cart()

    expect(cart.items).to_have_count(2)
    assert sorted(cart.names()) == ["Sauce Labs Backpack", "Sauce Labs Bike Light"]


@allure.story("Contents")
def test_the_cart_survives_going_back_to_the_catalogue(inventory: InventoryPage):
    cart = inventory.add_to_cart(BACKPACK).open_cart()
    cart.continue_shopping.click()

    expect(inventory.cart_badge).to_have_text("1")
