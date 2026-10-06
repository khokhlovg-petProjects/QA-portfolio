"""The saucedemo sign-in screen."""

from __future__ import annotations

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.inventory_page import InventoryPage


class LoginPage(BasePage):
    path = "/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.username = page.get_by_test_id("username")
        self.password = page.get_by_test_id("password")
        self.submit = page.get_by_test_id("login-button")
        self.error = page.get_by_test_id("error")

    @allure.step("Log in as {username}")
    def login(self, username: str, password: str) -> InventoryPage:
        """Sign in and hand back the catalogue the user lands on."""
        self.submit_credentials(username, password)
        return InventoryPage(self.page)

    @allure.step("Submit the credentials of {username}")
    def submit_credentials(self, username: str, password: str) -> None:
        """Fill the form and submit it, without assuming the attempt succeeds.

        Negative tests need this: `login` promises an `InventoryPage` the user
        never reaches when the credentials are rejected, and returning one
        anyway would hand the test a page object pointed at the wrong screen.
        """
        self.username.fill(username)
        self.password.fill(password)
        self.submit.click()
