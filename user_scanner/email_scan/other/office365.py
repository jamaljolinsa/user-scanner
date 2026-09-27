import httpx
import random
import string
from user_scanner.core.result import Result


async def _check(email: str) -> Result:
    base_url = "https://outlook.office365.com/autodiscover/autodiscover.json/v1.0"
    show_url = "https://office365.com"

    headers = {
        "User-Agent": "Microsoft Office/16.0 (Windows NT 10.0; Microsoft Outlook 16.0.12026; Pro)",
        "Accept": "application/json",
    }

    def get_random_string(length: int) -> str:
        return "".join(random.choice(string.digits) for _ in range(length))

    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=False) as client:
            r = await client.get(
                f"{base_url}/{email}?Protocol=Autodiscoverv1",
                headers=headers,
            )

        if r.status_code == 403:
            return Result.error("Caught by WAF or IP Block (403)", url=show_url)

        if r.status_code == 429:
            return Result.error("Rate limited (429)", url=show_url)

        # A successful Autodiscover HTTP response is not, by itself, proof that
        # the mailbox exists. Treat unvalidated responses as unknown/error
        # instead of turning every 200 (or every other status) into a verdict.
        return Result.error(
            f"Could not verify Office 365 mailbox registration (HTTP {r.status_code})",
            url=show_url,
        )

    except httpx.ConnectTimeout:
        return Result.error("Connection timed out", url=show_url)

    except httpx.ReadTimeout:
        return Result.error("Server took too long to respond", url=show_url)

    except Exception as e:
        return Result.error(e, url=show_url)


async def validate_office365(email: str) -> Result:
    return await _check(email)
