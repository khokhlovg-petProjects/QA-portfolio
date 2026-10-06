"""Token issuing and the protection of an authenticated endpoint."""

import allure
import pytest

from api.client import DummyJsonClient
from api.models import ApiError, CurrentUser, LoginResponse
from settings import settings

pytestmark = [pytest.mark.api, allure.feature("API: authentication")]


@allure.story("Issuing a token")
@pytest.mark.smoke
def test_valid_credentials_return_a_usable_token(api: DummyJsonClient):
    response = api.login(settings.api_username, settings.api_password)

    assert response.status_code == 200
    session_user = LoginResponse.model_validate(response.json())
    assert session_user.username == settings.api_username
    assert session_user.access_token != session_user.refresh_token


@allure.story("Issuing a token")
@pytest.mark.parametrize(
    ("username", "password"),
    [
        (settings.api_username, "wrong-password"),
        ("no-such-user", settings.api_password),
        ("", ""),
    ],
    ids=["wrong-password", "unknown-username", "empty-credentials"],
)
def test_bad_credentials_are_refused_with_an_explanation(
    api: DummyJsonClient,
    username,
    password,
):
    response = api.login(username, password)

    assert response.status_code == 400
    assert ApiError.model_validate(response.json()).message


@allure.story("Issuing a token")
def test_the_response_never_echoes_the_submitted_password(api: DummyJsonClient):
    """A token response that leaked the password would be a real finding."""
    response = api.login(settings.api_username, settings.api_password)

    assert settings.api_password not in response.text


@allure.story("Protected endpoint")
@pytest.mark.smoke
def test_a_token_identifies_the_user_who_signed_in(authorized_api: DummyJsonClient):
    response = authorized_api.me()

    assert response.status_code == 200
    assert CurrentUser.model_validate(response.json()).username == settings.api_username


@allure.story("Protected endpoint")
def test_the_endpoint_is_closed_without_a_token(api: DummyJsonClient):
    response = api.me()

    assert response.status_code == 401
    assert ApiError.model_validate(response.json()).message


@allure.story("Protected endpoint")
def test_a_forged_token_is_rejected(api: DummyJsonClient):
    api.session.headers["Authorization"] = "Bearer not-a-real-token"
    response = api.me()

    assert response.status_code == 401
