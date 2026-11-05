
import hashlib
import hmac
import secrets


ITERATIONS = 600_000


def hash_password(password):
    if not isinstance(password, str) or len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")

    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        ITERATIONS,
    )

    return (
        f"pbkdf2_sha256${ITERATIONS}$"
        f"{salt.hex()}${password_hash.hex()}"
    )


def verify_password(password, stored_hash):
    try:
        algorithm, iterations, salt_hex, hash_hex = stored_hash.split("$")

        if algorithm != "pbkdf2_sha256":
            return False

        iterations = int(iterations)

        if iterations < 600_000 or iterations > 2_000_000:
            return False

        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
        )

        return hmac.compare_digest(actual_hash, expected_hash)

    except (ValueError, TypeError, AttributeError):
        return False
