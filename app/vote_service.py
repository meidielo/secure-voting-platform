from datetime import datetime
import hashlib
from flask import current_app
from sqlalchemy.exc import IntegrityError
from app.models import Ballot, Attendance
from app.security.attendance import voter_key_from_identifier


def cast_anonymous_vote(db, user, candidate, *, election_id=None, identifier=None, fail_after_ballot=False):
    """
    Atomically record an anonymous ballot and attendance.

    Parameters:
    - db: SQLAlchemy instance (from app.db)
    - user: models.User
    - candidate: models.Candidate
    - election_id: optional override; defaults to app.config['ELECTION_ID']
    - identifier: optional voter identifier for key derivation; defaults to user.driver_lic_no or user.id
    - fail_after_ballot: when True, raises RuntimeError after inserting ballot (for tests)

    Returns: (ballot, attendance)
    Raises: IntegrityError for duplicate attendance (one vote per person)
    """
    election = election_id or current_app.config.get('ELECTION_ID', 'ELECTION2025')
    ident = identifier or getattr(user, 'driver_lic_no', None) or str(user.id)
    vkey = voter_key_from_identifier(ident)

    now = datetime.utcnow()
    payload = f"{election}|{candidate.id}|{candidate.position}|{now.isoformat()}"
    ihash = hashlib.sha256(payload.encode('utf-8')).hexdigest()

    # Use a nested transaction to play nicely with Flask-SQLAlchemy's
    # per-request transaction while still guaranteeing atomicity for
    # these two inserts together.
    with db.session.begin_nested():
        ballot = Ballot(
            election_id=election,
            candidate_id=candidate.id,
            position=candidate.position,
            integrity_hash=ihash,
            created_at=now,
        )
        db.session.add(ballot)

        if fail_after_ballot:
            raise RuntimeError("Injected failure after ballot insert for test")

        attendance = Attendance(
            election_id=election,
            voter_key=vkey,
            ballot_link=None,
        )
        db.session.add(attendance)

        # Mark user as voted for quick checks
        user.has_voted = True
        db.session.add(user)

    return ballot, attendance
