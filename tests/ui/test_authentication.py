"""Sign-in behaviour, the one area the rest of the UI suite takes for granted."""

import allure
import pytest
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage
from settings import settings

pytestmark = [pytest.mark.ui, allure.feature("Authentication")]


@allure.story("Sign-in page")
@pytest.mark.smoke
def test_login_page_loads(page: Page):
    login_page = LoginPage(page).open()
    expect(page).to_have_title("Swag Labs")
    expect(login_page.submit).to_be_visible()


@allure.story("Sign-in page")
@pytest.mark.smoke
def test_valid_credentials_land_on_the_catalogue(page: Page):
    inventory = LoginPage(page).open().login(settings.ui_username, settings.ui_password)

    expect(page).to_have_url(f"{settings.ui_base_url}/inventory.html")
    expect(inventory.items).to_have_count(6)


@allure.story("Rejected sign-in")
@pytest.mark.parametrize(
    ("username", "password", "message"),
    [
        ("standard_user", "wrong_password", "Username and password do not match"),
        ("no_such_user", "secret_sauce", "Username and password do not match"),
        ("locked_out_user", "secret_sauce", "Sorry, this user has been locked out"),
        ("", "secret_sauce", "Username is required"),
        ("standard_user", "", "Password is required"),
        ("", "", "Username is required"),
    ],
    ids=[
        "wrong-password",
        "unknown-username",
        "locked-out-account",
        "missing-username",
        "missing-password",
        "empty-form",
    ],
)
def test_rejected_credentials_explain_why(page: Page, username, password, message):
    login_page = LoginPage(page).open()
    login_page.submit_credentials(username, password)

    expect(login_page.error).to_contain_text(message)


@allure.story("Rejected sign-in")
def test_a_rejected_sign_in_leaves_the_user_on_the_login_page(page: Page):
    """Guards against the catalogue being reachable after a failed attempt."""
    login_page = LoginPage(page).open()
    login_page.submit_credentials("standard_user", "wrong_password")

    expect(login_page.error).to_be_visible()
    expect(page).to_have_url(f"{settings.ui_base_url}/")


@allure.story("Access control")
def test_the_catalogue_is_not_reachable_without_signing_in(page: Page):
    page.goto("/inventory.html")

    expect(page.get_by_test_id("error")).to_contain_text("You can only access '/inventory.html'")
