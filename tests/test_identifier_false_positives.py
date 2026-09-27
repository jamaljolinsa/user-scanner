import pytest

from user_scanner.core.result import Status


@pytest.mark.parametrize(
    ("status_code", "body"),
    [
        (200, "<html><head><title>Sign in</title></head><body>generic page</body></html>"),
        (200, "<html><head><title>Challenge</title></head><body>challenge</body></html>"),
    ],
)
def test_github_html_200_without_canonical_profile_is_not_found(monkeypatch, status_code, body):
    from user_scanner.user_scan.dev import github

    class Response:
        def __init__(self):
            self.status_code = status_code
            self.text = body

        def json(self):
            return {}

    monkeypatch.setattr(
        github,
        "make_request",
        lambda *args, **kwargs: Response(),
    )

    result = github.validate_github("someuser")
    assert result.status is Status.ERROR


def test_leetcode_200_without_matched_user_is_not_available(monkeypatch):
    from user_scanner.user_scan.dev import leetcode

    class Response:
        status_code = 200

        def json(self):
            return {"data": {"matchedUser": None}}

    monkeypatch.setattr(
        leetcode,
        "make_request",
        lambda *args, **kwargs: Response(),
    )

    result = leetcode.validate_leetcode("someuser")
    assert result.status is Status.ERROR
