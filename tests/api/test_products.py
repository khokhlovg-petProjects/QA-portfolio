"""Reading, searching and mutating the product catalogue.

DummyJSON simulates writes instead of persisting them: it validates the
request and answers as though it had saved, but the catalogue is unchanged on
the next call. The mutation tests below therefore assert on the response
contract only. Asserting that a created product can be read back would be
testing the fixture host rather than anything useful.
"""

import allure
import pytest

from api.client import DummyJsonClient
from api.models import (
    ApiError,
    CatalogueProduct,
    CreatedProduct,
    DeletedProduct,
    Product,
    ProductSlice,
)

pytestmark = [pytest.mark.api, allure.feature("API: products")]

KNOWN_PRODUCT_ID = 1
MISSING_PRODUCT_ID = 0


@allure.story("Reading one")
@pytest.mark.smoke
def test_a_product_matches_the_documented_schema(api: DummyJsonClient):
    response = api.get_product(KNOWN_PRODUCT_ID)

    assert response.status_code == 200
    product = CatalogueProduct.model_validate(response.json())
    assert product.id == KNOWN_PRODUCT_ID


@allure.story("Reading one")
def test_an_unknown_id_is_a_404_naming_the_id(api: DummyJsonClient):
    response = api.get_product(MISSING_PRODUCT_ID)

    assert response.status_code == 404
    assert str(MISSING_PRODUCT_ID) in ApiError.model_validate(response.json()).message


@allure.story("Listing")
@pytest.mark.smoke
def test_the_catalogue_lists_products(api: DummyJsonClient):
    response = api.list_products()

    assert response.status_code == 200
    catalogue = ProductSlice.model_validate(response.json())
    assert catalogue.products
    assert catalogue.total >= len(catalogue.products)


@allure.story("Listing")
@pytest.mark.parametrize("limit", [1, 5, 20], ids=lambda value: f"limit-{value}")
def test_the_limit_is_honoured(api: DummyJsonClient, limit):
    catalogue = ProductSlice.model_validate(api.list_products(limit=limit).json())

    assert catalogue.limit == limit
    assert len(catalogue.products) == limit


@allure.story("Listing")
def test_consecutive_pages_do_not_overlap(api: DummyJsonClient):
    """Off-by-one errors in paging show up as a product on two pages at once."""
    first = ProductSlice.model_validate(api.list_products(limit=5, skip=0).json())
    second = ProductSlice.model_validate(api.list_products(limit=5, skip=5).json())

    assert second.skip == 5
    assert {p.id for p in first.products}.isdisjoint({p.id for p in second.products})


@allure.story("Searching")
def test_search_results_are_relevant_to_the_query(api: DummyJsonClient):
    response = api.search_products("mascara")

    assert response.status_code == 200
    results = ProductSlice.model_validate(response.json())
    assert results.products
    for product in results.products:
        haystack = f"{product.title} {product.model_extra.get('description', '')}".lower()
        assert "mascara" in haystack


@allure.story("Searching")
def test_a_query_matching_nothing_returns_an_empty_page(api: DummyJsonClient):
    results = ProductSlice.model_validate(api.search_products("zzzznotaproduct").json())

    assert results.products == []
    assert results.total == 0


@allure.story("Writing")
def test_creating_a_product_answers_201_with_an_id(api: DummyJsonClient):
    response = api.add_product(title="Portfolio probe", price=19.99, category="beauty")

    assert response.status_code == 201
    created = CreatedProduct.model_validate(response.json())
    assert created.title == "Portfolio probe"
    assert created.id > 0


@allure.story("Writing")
def test_updating_a_product_returns_the_new_value(api: DummyJsonClient):
    response = api.update_product(KNOWN_PRODUCT_ID, title="Renamed by the suite")

    assert response.status_code == 200
    product = Product.model_validate(response.json())
    assert product.id == KNOWN_PRODUCT_ID
    assert product.title == "Renamed by the suite"


@allure.story("Writing")
def test_updating_one_field_leaves_the_others_alone(api: DummyJsonClient):
    before = CatalogueProduct.model_validate(api.get_product(KNOWN_PRODUCT_ID).json())
    after = Product.model_validate(
        api.update_product(KNOWN_PRODUCT_ID, title="Renamed by the suite").json()
    )

    assert after.price == before.price
    assert after.category == before.category


@allure.story("Writing")
def test_deleting_a_product_marks_it_deleted(api: DummyJsonClient):
    response = api.delete_product(KNOWN_PRODUCT_ID)

    assert response.status_code == 200
    deleted = DeletedProduct.model_validate(response.json())
    assert deleted.id == KNOWN_PRODUCT_ID
    assert deleted.is_deleted is True
    assert deleted.deleted_on
