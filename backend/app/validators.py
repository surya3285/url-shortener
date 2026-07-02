from urllib.parse import urlparse

MAX_URL_LENGTH = 2048
ALLOWED_SCHEMES = {"http", "https"}


def normalize_and_validate(raw_url):
    """Validate a user-supplied URL.

    Returns the cleaned URL string, or raises ValueError with a message.
    """
    if not raw_url or not isinstance(raw_url, str):
        raise ValueError("A URL is required")

    url = raw_url.strip()
    if len(url) > MAX_URL_LENGTH:
        raise ValueError("URL is too long")

    # Default to https if the user omitted a scheme.
    if "://" not in url:
        url = "https://" + url

    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError("URL must use http or https")
    if not parsed.netloc or "." not in parsed.netloc:
        raise ValueError("URL must include a valid domain")

    return url
