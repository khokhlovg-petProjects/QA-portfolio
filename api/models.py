"""Response schemas for the DummyJSON API.

Validating responses against these models turns "the field I needed was
missing" and "the price came back as a string" into a failure at the boundary
with a precise message, instead of a `KeyError` three lines further down or a
silent pass.

Every model allows unknown fields. Rejecting them would make the suite fail the
moment the API adds something harmless, which is noise rather than signal; the
contract worth enforcing is that the fields we rely on are present and
correctly typed.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic.alias_generators import to_camel


class ApiModel(BaseModel):
    """Base for every response model.

    The API speaks camelCase and Python reads better in snake_case, so the
    alias generator bridges the two and attribute access stays idiomatic.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="allow",
    )


class LoginResponse(ApiModel):
    id: int
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    access_token: str = Field(min_length=1)
    refresh_token: str = Field(min_length=1)


class CurrentUser(ApiModel):
    id: int
    username: str
    email: EmailStr
    first_name: str
    last_name: str


class Product(ApiModel):
    """The fields every product-shaped response carries.

    Deliberately the intersection and not the union: `PUT /products/{id}`
    answers with a narrower projection than `GET` does, and a single model
    covering both would have to make real fields optional, which costs the
    contract check on the endpoints that do return them.
    """

    id: int
    title: str = Field(min_length=1)
    price: float = Field(ge=0)
    category: str
    stock: int = Field(ge=0)
    rating: float = Field(ge=0, le=5)


class CatalogueProduct(Product):
    """A fully populated catalogue entry, as read endpoints return it."""

    tags: list[str]


class ProductSlice(ApiModel):
    """One page of the catalogue, from the list and search endpoints."""

    products: list[CatalogueProduct]
    total: int = Field(ge=0)
    skip: int = Field(ge=0)
    limit: int = Field(ge=0)


class CreatedProduct(ApiModel):
    """What `POST /products/add` echoes back: an id plus whatever was sent."""

    id: int
    title: str = Field(min_length=1)


class DeletedProduct(CatalogueProduct):
    is_deleted: bool
    deleted_on: str = Field(min_length=1)


class ApiError(ApiModel):
    message: str = Field(min_length=1)
