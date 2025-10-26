import hmac
import hashlib
from flask import current_app


def _normalize(text: str) -> str:
    if text is None:
        return ""
    return (str(text).strip().upper())


def voter_key_from_identifier(identifier: str) -> str:
    """Derive a deterministic, irreversible key for attendance linking.

    Uses HMAC-SHA256 over the normalized identifier with a secret pepper.
    Falls back to SECRET_KEY in development if VOTE_ATTENDANCE_PEPPER is unset.
    Returns a 64-character hex string.
    """
    pepper = current_app.config.get("VOTE_ATTENDANCE_PEPPER") or current_app.config.get("SECRET_KEY", "dev-secret")
    if not isinstance(pepper, (bytes, bytearray)):
        pepper = pepper.encode("utf-8")
    msg = _normalize(identifier).encode("utf-8")
    digest = hmac.new(pepper, msg, hashlib.sha256).hexdigest()
    return digest


def ballot_link_for_id(ballot_id: str) -> str:
    """Produce a peppered link value that auditors can recompute.

    Not a foreign key; just a deterministic tag usable for cross-checks.
    """
    pepper = current_app.config.get("VOTE_ATTENDANCE_PEPPER") or current_app.config.get("SECRET_KEY", "dev-secret")
    if not isinstance(pepper, (bytes, bytearray)):
        pepper = pepper.encode("utf-8")
    msg = str(ballot_id).encode("utf-8")
    return hmac.new(pepper, msg, hashlib.sha256).hexdigest()
