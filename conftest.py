"""Fixtures shared by the whole suite.

The browser-level fixtures (`browser`, `context`, `page`) come from
pytest-playwright. What is added here is either configuration that has to run
once per session, or a shortcut that stops the UI suite from paying for a login
it is not testing.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

import allure
import pytest
from playwright.sync_api import Browser, Page, Playwright, expect

from api.client import DummyJsonClient
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from settings import settings

#: Fixtures that hand a test a browser page, in the order we look for one when
#: a test fails and we want a screenshot.
PAGE_FIXTURES = ("logged_in_page", "page")


@pytest.fixture(scope="session", autouse=True)
def _configure_playwright(playwright: Playwright) -> None:
    """Set the test-id attribute and the assertion timeout once per session.

    saucedemo marks its elements with `data-test`, so teaching Playwright about
    it here is what lets every page object use `get_by_test_id` instead of
    repeating a CSS attribute selector. Setting the `expect` timeout in one
    place stops individual tests from inventing their own.
    """
    playwright.selectors.set_test_id_attribute("data-test")
    expect.set_options(timeout=settings.expect_timeout_ms)


@pytest.fixture(scope="session")
def base_url(request: pytest.FixtureRequest) -> str:
    """Resolve the UI host, letting `--base-url` win over configuration.

    pytest-playwright feeds this into every browser context, which is what
    makes `page.goto("/inventory.html")` work in the page objects.
    """
    return request.config.getoption("--base-url") or settings.ui_base_url


@pytest.fixture(scope="session")
def storage_state(
    browser: Browser,
    browser_context_args: dict,
    tmp_path_factory: pytest.TempPathFactory,
) -> Path:
    """Log in once per session and hand back a reusable session file.

    Authentication is covered by its own tests; repeating it before every other
    UI test only adds wall-clock time, and on a suite large enough to matter it
    adds CI minutes too.

    The file lives in pytest's temp directory rather than at a fixed path
    because under xdist each worker runs its own session. A shared filename
    would have several workers writing it at the same moment, and one of them
    reading it half-written.
    """
    state_path = tmp_path_factory.getbasetemp() / "storage-state.json"
    context = browser.new_context(**browser_context_args)
    page = context.new_page()

    inventory = LoginPage(page).open().login(settings.ui_username, settings.ui_password)
    # The cookie only exists once the catalogue has actually rendered, so the
    # state has to be saved after the navigation settles, not after the click.
    expect(inventory.items.first).to_be_visible()

    context.storage_state(path=state_path)
    context.close()
    return state_path


@pytest.fixture
def logged_in_page(
    browser: Browser,
    browser_context_args: dict,
    storage_state: Path,
) -> Iterator[Page]:
    """A page that starts out already signed in."""
    context = browser.new_context(**browser_context_args, storage_state=storage_state)
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def inventory(logged_in_page: Page) -> InventoryPage:
    """The catalogue, open and ready, for the tests that start from there."""
    return InventoryPage(logged_in_page).open()


@pytest.fixture
def api() -> Iterator[DummyJsonClient]:
    """An unauthenticated API client."""
    with DummyJsonClient() as client:
        yield client


@pytest.fixture
def authorized_api(api: DummyJsonClient) -> DummyJsonClient:
    """An API client that already carries a bearer token."""
    api.authorize(settings.api_username, settings.api_password)
    return api


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """Attach browser evidence to the Allure report whenever a UI test fails.

    Collected here rather than in the tests because a failing assertion never
    reaches its own cleanup code, and a screenshot taken after the context
    closes is useless.
    """
    report = yield
    if report.when == "call" and report.failed:
        _attach_browser_evidence(item)
    return report


def _attach_browser_evidence(item: pytest.Item) -> None:
    page = next(
        (item.funcargs[name] for name in PAGE_FIXTURES if name in item.funcargs),
        None,
    )
    if page is None:
        return

    try:
        allure.attach(
            page.screenshot(full_page=True),
            name="screenshot",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(page.url, name="url", attachment_type=allure.attachment_type.TEXT)
        allure.attach(page.content(), name="dom", attachment_type=allure.attachment_type.HTML)
    except Exception as error:  # noqa: BLE001
        # A crashed or already-closed page must not turn one failure into two.
        allure.attach(
            f"Could not collect browser evidence: {error!r}",
            name="evidence-collection-failed",
            attachment_type=allure.attachment_type.TEXT,
        )
