import pytest
from app import db
from app.models import Ballot, Attendance, Candidate, User
from app.vote_service import cast_anonymous_vote
from app.security.attendance import voter_key_from_identifier


def login(client, username, password):
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)


def test_cast_creates_ballot_and_attendance(client, app):
    # login as voter1
    rv = login(client, 'voter1', 'VoterSecurePass123!')
    assert b'Welcome, voter1' in rv.data

    # pick a candidate
    with app.app_context():
        cand = Candidate.query.first()
        assert cand is not None

    # cast
    rv = client.post('/vote', data={'candidate_id': cand.id}, follow_redirects=True)
    assert b'Vote cast successfully!' in rv.data

    # verify DB state
    with app.app_context():
        assert Ballot.query.count() == 1
        assert Attendance.query.count() == 1
        voter = User.query.filter_by(username='voter1').first()
        expected_key = voter_key_from_identifier(voter.driver_lic_no)
        att = Attendance.query.first()
        assert att.voter_key == expected_key


def test_duplicate_vote_prevented(client, app):
    rv = login(client, 'voter1', 'VoterSecurePass123!')
    assert b'Welcome, voter1' in rv.data

    with app.app_context():
        cand = Candidate.query.first()

    # first vote
    client.post('/vote', data={'candidate_id': cand.id}, follow_redirects=True)

    # second vote should be blocked
    rv2 = client.post('/vote', data={'candidate_id': cand.id}, follow_redirects=True)
    assert b'You have already voted' in rv2.data or b'Duplicate vote detected' in rv2.data

    with app.app_context():
        assert Ballot.query.count() == 1
        assert Attendance.query.count() == 1


def test_atomicity_rollback_on_failure(app):
    # Using service directly to inject a failure after ballot insert
    with app.app_context():
        voter = User.query.filter_by(username='voter1').first()
        cand = Candidate.query.first()

        bcount_before = Ballot.query.count()
        acount_before = Attendance.query.count()

        with pytest.raises(RuntimeError):
            cast_anonymous_vote(db, voter, cand, fail_after_ballot=True)

        # No new rows should be present after rollback
        assert Ballot.query.count() == bcount_before
        assert Attendance.query.count() == acount_before
