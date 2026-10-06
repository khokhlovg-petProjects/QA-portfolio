"""Shared plumbing for every page object."""

from __future__ import annotations

from typing import Self

from playwright.sync_api import Page


class BasePage:
    """Common behaviour for page objects.

    Subclasses declare `path` relative to the context's base_url and build their
    locators in `__init__`. Locators are descriptions rather than resolved
    elements, so building them once in the constructor stays correct across
    navigations and re-renders.
    """

    path: str = "/"

    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self) -> Self:
        self.page.goto(self.path)
        return self
