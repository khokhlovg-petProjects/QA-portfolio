"""The three screens of the saucedemo checkout.

They are modelled separately rather than as one `CheckoutPage` because each
step has its own URL, its own controls and its own failure modes; folding them
together would mean a single object whose locators are only valid part of the
time.
"""

from __future__ import annotations

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage


class CheckoutInformationPage(BasePage):
    """Step one: the buyer's name and postcode."""

    path = "/checkout-step-one.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.first_name = page.get_by_test_id("firstName")
        self.last_name = page.get_by_test_id("lastName")
        self.postal_code = page.get_by_test_id("postalCode")
        self.continue_button = page.get_by_test_id("continue")
        self.cancel = page.get_by_test_id("cancel")
        self.error = page.get_by_test_id("error")

    @allure.step("Fill in the buyer's details")
    def fill_details(self, first_name: str, last_name: str, postal_code: str) -> None:
        self.first_name.fill(first_name)
        self.last_name.fill(last_name)
        self.postal_code.fill(postal_code)

    @allure.step("Continue to the order overview")
    def submit(self) -> CheckoutOverviewPage:
        self.continue_button.click()
        return CheckoutOverviewPage(self.page)

    def complete(self, first_name: str, last_name: str, postal_code: str) -> CheckoutOverviewPage:
        """Fill the step in one call, for tests that only pass through it."""
        self.fill_details(first_name, last_name, postal_code)
        return self.submit()

    @allure.step("Continue, expecting the form to be rejected")
    def submit_expecting_rejection(self) -> None:
        """Submit without promising the next screen, for the validation tests."""
        self.continue_button.click()


class CheckoutOverviewPage(BasePage):
    """Step two: the order summary and totals."""

    path = "/checkout-step-two.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.items = page.get_by_test_id("inventory-item")
        self.item_prices = page.get_by_test_id("inventory-item-price")
        self.subtotal_label = page.get_by_test_id("subtotal-label")
        self.tax_label = page.get_by_test_id("tax-label")
        self.total_label = page.get_by_test_id("total-label")
        self.finish_button = page.get_by_test_id("finish")

    def subtotal(self) -> float:
        """The pre-tax total, parsed out of 'Item total: $29.99'."""
        return self._amount(self.subtotal_label.inner_text())

    def tax(self) -> float:
        return self._amount(self.tax_label.inner_text())

    def total(self) -> float:
        return self._amount(self.total_label.inner_text())

    def item_total(self) -> float:
        """What the listed line items add up to, independent of the subtotal label."""
        return sum(float(text.removeprefix("$")) for text in self.item_prices.all_inner_texts())

    @staticmethod
    def _amount(label: str) -> float:
        return float(label.split("$")[1])

    @allure.step("Place the order")
    def finish(self) -> CheckoutCompletePage:
        self.finish_button.click()
        return CheckoutCompletePage(self.page)


class CheckoutCompletePage(BasePage):
    """Step three: the confirmation."""

    path = "/checkout-complete.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header = page.get_by_test_id("complete-header")
        self.text = page.get_by_test_id("complete-text")
        self.back_home = page.get_by_test_id("back-to-products")
