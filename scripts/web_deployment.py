#!/usr/bin/env python3
"""Validate public release configuration and gate landing links on app readiness."""

import argparse
import json
from urllib.parse import urlsplit
from urllib.request import urlopen


def clean_https_origin(value: str) -> str:
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in ("", "/")
        or "?" in value
        or "#" in value
        or any(character.isspace() for character in value)
    ):
        raise ValueError("Release origins must contain only an HTTPS scheme, host, and optional port")
    # Accessing port also rejects invalid/non-numeric ports.
    _ = parsed.port
    return f"https://{parsed.netloc}"


def fetch(url: str) -> bytes:
    with urlopen(url, timeout=10) as response:
        if urlsplit(response.url).scheme != "https":
            raise ValueError("Release checks require HTTPS after redirects")
        return response.read(2_000_000)


def verify_app(origin: str) -> None:
    html = fetch(f"{origin}/")
    if b"flutter_bootstrap.js" not in html:
        raise ValueError("App domain does not serve the Flutter entrypoint")
    bootstrap = fetch(f"{origin}/flutter_bootstrap.js")
    if b"_flutter" not in bootstrap or b"<html" in bootstrap.lower():
        raise ValueError("App domain does not serve valid Flutter bootstrap JavaScript")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-origin", required=True)
    parser.add_argument("--app-origin", required=True)
    parser.add_argument("--check-api", action="store_true")
    parser.add_argument("--check-app", action="store_true")
    arguments = parser.parse_args()
    api_origin = clean_https_origin(arguments.api_origin)
    app_origin = clean_https_origin(arguments.app_origin)
    if arguments.check_api:
        if json.loads(fetch(f"{api_origin}/ready")).get("status") != "ready":
            raise ValueError("API readiness check failed")
    if arguments.check_app:
        verify_app(app_origin)
    print("Web release configuration and requested readiness checks passed.")


if __name__ == "__main__":
    main()
