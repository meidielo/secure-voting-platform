import hashlib
import hmac
import os
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError


def _voter_token(user_id: int) -> str:
    """
    Compute a one-way blind token for the voter.

    Uses HMAC-SHA256 keyed with an application secret so the token is
    deterministic (same user always produces the same token) but cannot
    be reversed to a user_id without the secret key.
    """
    secret = os.environ.get("SECRET_KEY", "dev-secret").encode("utf-8")
    msg = f"voter:{user_id}".encode("utf-8")
    return hmac.new(secret, msg, hashlib.sha256).hexdigest()


def cast_anonymous_vote(db, user, candidate):
    """
    Cast an anonymous vote.

    The vote record stores a blind voter_token (HMAC of user-id) instead
    of the raw user_id, breaking the direct link between identity and
    ballot while still enforcing one-vote-per-person via a DB unique
    constraint on voter_token.
    """
    from app.models import Vote

    token = _voter_token(user.id)

    # Integrity hash covers the token + candidate + timestamp
    ts = datetime.now(timezone.utc).isoformat()
    payload = f"{token}:{candidate.id}:{ts}".encode()
    vote_hash = hashlib.sha256(payload).hexdigest()

    vote = Vote(
        voter_token=token,
        candidate_id=candidate.id,
        position=candidate.position,
        vote_hash=vote_hash,
        created_at=datetime.now(timezone.utc),
    )
    db.session.add(vote)

    # Mark user as having voted (application-level guard)
    user.has_voted = True
    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        # Unique(voter_token) enforces one vote per person
        raise
