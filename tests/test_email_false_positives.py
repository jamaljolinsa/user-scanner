import types
import pytest

from user_scanner.core.result import Status


class MockResponse:
    def __init__(self, status_code, data=None):
        self.status_code = status_code
        self._data = data

    def json(self):
        if isinstance(self._data, Exception):
            raise self._data
        return self._data


class MockClient:
    def __init__(self, response, **kwargs):
        self.response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, *args, **kwargs):
        return self.response

    async def post(self, *args, **kwargs):
        return self.response


@pytest.mark.asyncio
async def test_office365_200_is_not_automatically_registered(monkeypatch):
    from user_scanner.email_scan.other import office365

    monkeypatch.setattr(
        office365.httpx,
        "AsyncClient",
        lambda **kwargs: MockClient(MockResponse(200, {"unexpected": True}), **kwargs),
    )

    result = await office365.validate_office365("test@example.com")
    assert result.status is Status.ERROR


@pytest.mark.asyncio
async def test_office365_non_200_is_not_automatically_available(monkeypatch):
    from user_scanner.email_scan.other import office365

    monkeypatch.setattr(
        office365.httpx,
        "AsyncClient",
        lambda **kwargs: MockClient(MockResponse(500), **kwargs),
    )

    result = await office365.validate_office365("test@example.com")
    assert result.status is Status.ERROR


@pytest.mark.asyncio
async def test_uniscore_200_is_not_automatically_registered(monkeypatch):
    from user_scanner.email_scan.sports import uniscore

    monkeypatch.setattr(
        uniscore.httpx,
        "AsyncClient",
        lambda **kwargs: MockClient(MockResponse(200, {"message": "ok"}), **kwargs),
    )

    result = await uniscore.validate_uniscore("test@example.com")
    assert result.status is Status.ERROR


@pytest.mark.asyncio
async def test_cambly_captcha_is_not_registered(monkeypatch):
    from user_scanner.email_scan.learning import cambly

    monkeypatch.setattr(
        cambly.httpx,
        "AsyncClient",
        lambda **kwargs: MockClient(
            MockResponse(422, {"error": "nocaptcha", "error_text": "captcha required"}),
            **kwargs,
        ),
    )

    result = await cambly.validate_cambly("test@example.com")
    assert result.status is Status.ERROR
