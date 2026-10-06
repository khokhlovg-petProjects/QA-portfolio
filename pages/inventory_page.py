"""The saucedemo product catalogue."""

from __future__ import annotations

from typing import Self

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.cart_page import CartPage


class InventoryPage(BasePage):
    path = "/inventory.html"

    #: Readable names for the opaque values behind the sort dropdown.
    SORT_OPTIONS = {
        "name-asc": "az",
        "name-desc": "za",
        "price-asc": "lohi",
        "price-desc": "hilo",
    }

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.items = page.get_by_test_id("inventory-item")
        self.item_names = page.get_by_test_id("inventory-item-name")
        self.item_prices = page.get_by_test_id("inventory-item-price")
        self.cart_link = page.get_by_test_id("shopping-cart-link")
        self.cart_badge = page.get_by_test_id("shopping-cart-badge")
        self.sort_dropdown = page.get_by_test_id("product-sort-container")

    @allure.step("Add '{product}' to the cart")
    def add_to_cart(self, product: str) -> Self:
        self.page.get_by_test_id(f"add-to-cart-{product}").click()
        return self

    @allure.step("Remove '{product}' from the cart")
    def remove_from_cart(self, product: str) -> Self:
        self.page.get_by_test_id(f"remove-{product}").click()
        return self

    @allure.step("Sort the catalogue by {order}")
    def sort_by(self, order: str) -> Self:
        self.sort_dropdown.select_option(self.SORT_OPTIONS[order])
        return self

    def prices(self) -> list[float]:
        """Every visible price as a number, in the order the catalogue shows."""
        return [float(text.removeprefix("$")) for text in self.item_prices.all_inner_texts()]

    def names(self) -> list[str]:
        return self.item_names.all_inner_texts()

    @allure.step("Open the cart")
    def open_cart(self) -> CartPage:
        self.cart_link.click()
        return CartPage(self.page)
