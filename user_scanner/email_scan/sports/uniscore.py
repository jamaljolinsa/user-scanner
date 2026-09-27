import httpx
from user_scanner.core.result import Result


async def _check(email: str) -> Result:
    # Target endpoint for password recovery checks
    url = "https://api.unik8s.com/api/v2/account/auth/forgot-password?language=en"
    show_url = "https://uniscore.com/"

    headers = {
        'User-Agent': "okhttp/4.12.0",
        'Accept': "application/json, text/plain, */*",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/json',
        'app-version': "1.8.5",
        'customer-id': "",
        'user-id': "",
        'platform': "android",
        'region': "IN",
        'phone-model': "REDMAGIC-X3",
        'os-version': "11",
        'device-language': "en"
    }

    payload = {
        "provider": "email",
        "locale": "en",
        "platform": "android",
        "clientId": "",
        "email": email
    }

    try:
        # Enforcing HTTP/2 protocol constraint matching mobile gateway standards
        async with httpx.AsyncClient(http2=True, timeout=15.0) as client:
            response = await client.post(url, json=payload, headers=headers)

            # Perimeter security filters
            if response.status_code == 403:
                return Result.error("Access rejected by API gateway firewall (403)")
            if response.status_code == 429:
                return Result.error("Rate limit triggered on recovery route (429)")

            try:
                data = response.json()
            except Exception:
                data = {}

            # Do not infer registration from HTTP 200 alone. The endpoint may
            # return a successful transport response without an account match.
            if response.status_code == 200:
                return Result.error(
                    "Unverified recovery response; account registration could not be confirmed",
                    url=show_url,
                )

            if response.status_code == 404:
                error_msg = data.get("message", "").lower() if isinstance(data, dict) else ""

                if "this email hasn't been registered to an account" in error_msg:
                    return Result.available(url=show_url)

                return Result.error(
                    "404 status received but payload body failed verification signature",
                    url=show_url,
                )

            return Result.error(
                f"Gateway returned unhandled status profile (HTTP {response.status_code})",
                url=show_url,
            )

    except Exception as e:
        return Result.error(str(e), url=show_url)


async def validate_uniscore(email: str) -> Result:
    return await _check(email)
