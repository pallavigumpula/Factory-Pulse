"""
Security utilities: password hashing, verification, and JWT generation/decoding.
Uses standard PBKDF2-HMAC-SHA256 (NIST recommended) and RFC 7519 HMAC-SHA256 JWT tokens.
Fully compatible without external C-extensions or network requirements.
"""

import hmac
import hashlib
import base64
import json
import time
import secrets
from typing import Optional, Dict, Any


def hash_password(password: str) -> str:
    """Generate secure salted PBKDF2-HMAC-SHA256 hash."""
    salt = secrets.token_hex(16)
    iterations = 100_000
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        iterations
    )
    return f"pbkdf2:sha256:{iterations}${salt}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against PBKDF2 hash."""
    try:
        parts = hashed_password.split('$')
        if len(parts) != 3:
            return False
        algo_iter, salt, expected_hex = parts
        _, _, iter_str = algo_iter.split(':')
        iterations = int(iter_str)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations
        )
        return hmac.compare_digest(key.hex(), expected_hex)
    except Exception:
        return False


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')


def _base64url_decode(data: str) -> bytes:
    padding = '=' * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_access_token(payload: Dict[str, Any], secret_key: str, expires_in_seconds: int = 86400) -> str:
    """Create a signed RFC 7519 JWT token with HS256."""
    header = {"alg": "HS256", "typ": "JWT"}
    body = payload.copy()
    now = int(time.time())
    if "iat" not in body:
        body["iat"] = now
    if "exp" not in body:
        body["exp"] = now + expires_in_seconds

    header_b64 = _base64url_encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    body_b64 = _base64url_encode(json.dumps(body, separators=(',', ':')).encode('utf-8'))
    signing_input = f"{header_b64}.{body_b64}".encode('utf-8')

    signature = hmac.new(secret_key.encode('utf-8'), signing_input, hashlib.sha256).digest()
    sig_b64 = _base64url_encode(signature)

    return f"{header_b64}.{body_b64}.{sig_b64}"


def decode_access_token(token: str, secret_key: str) -> Optional[Dict[str, Any]]:
    """Decode and verify an RFC 7519 JWT token with HS256."""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        header_b64, body_b64, sig_b64 = parts

        signing_input = f"{header_b64}.{body_b64}".encode('utf-8')
        expected_sig = hmac.new(secret_key.encode('utf-8'), signing_input, hashlib.sha256).digest()
        provided_sig = _base64url_decode(sig_b64)

        if not hmac.compare_digest(expected_sig, provided_sig):
            return None

        body_bytes = _base64url_decode(body_b64)
        payload = json.loads(body_bytes.decode('utf-8'))

        now = int(time.time())
        if "exp" in payload and payload["exp"] < now:
            return None

        return payload
    except Exception:
        return None
