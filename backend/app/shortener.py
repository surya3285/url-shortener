import secrets
import string

ALPHABET = string.ascii_letters + string.digits  # base62


def generate_code(length=6):
    """Return a random base62 string of the given length."""
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def generate_unique_code(exists, length=6, max_attempts=10):
    """Generate a code not already present.

    `exists` is a callable taking a code and returning True if it is taken.
    Grows the length after repeated collisions to stay robust as the table fills.
    """
    for attempt in range(max_attempts):
        code = generate_code(length + attempt // 3)
        if not exists(code):
            return code
    raise RuntimeError("Unable to generate a unique short code")
