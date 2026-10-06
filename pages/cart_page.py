"""The saucedemo cart."""

from __future__ import annotations

from typing import Self

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.checkout_pages import CheckoutInformationPage


class CartPage(BasePage):
    path = "/cart.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.items = page.get_by_test_id("inventory-item")
        self.item_names = page.get_by_test_id("inventory-item-name")
        self.checkout_button = page.get_by_test_id("checkout")
        self.continue_shopping = page.get_by_test_id("continue-shopping")

    def names(self) -> list[str]:
        return self.item_names.all_inner_texts()

    @allure.step("Remove '{product}' from the cart")
    def remove(self, product: str) -> Self:
        self.page.get_by_test_id(f"remove-{product}").click()
        return self

    @allure.step("Start checkout")
    def checkout(self) -> CheckoutInformationPage:
        self.checkout_button.click()
        return CheckoutInformationPage(self.page)
