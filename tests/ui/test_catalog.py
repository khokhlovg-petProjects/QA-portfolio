"""Catalogue listing and sorting."""

import allure
import pytest
from playwright.sync_api import expect

from pages.inventory_page import InventoryPage

pytestmark = [pytest.mark.ui, allure.feature("Catalogue")]


@allure.story("Listing")
@pytest.mark.smoke
def test_every_product_is_listed(inventory: InventoryPage):
    expect(inventory.items).to_have_count(6)
    assert len(inventory.prices()) == 6


@allure.story("Sorting")
def test_sorting_by_price_ascending(inventory: InventoryPage):
    prices = inventory.sort_by("price-asc").prices()
    assert prices == sorted(prices)


@allure.story("Sorting")
def test_sorting_by_price_descending(inventory: InventoryPage):
    prices = inventory.sort_by("price-desc").prices()
    assert prices == sorted(prices, reverse=True)


@allure.story("Sorting")
def test_sorting_by_name_ascending(inventory: InventoryPage):
    names = inventory.sort_by("name-asc").names()
    assert names == sorted(names)


@allure.story("Sorting")
def test_sorting_by_name_descending(inventory: InventoryPage):
    names = inventory.sort_by("name-desc").names()
    assert names == sorted(names, reverse=True)


@allure.story("Sorting")
def test_sorting_reorders_rather_than_filters(inventory: InventoryPage):
    """A sort that drops or duplicates products would still pass an ordering check."""
    before = sorted(inventory.names())
    after = sorted(inventory.sort_by("price-desc").names())
    assert after == before
