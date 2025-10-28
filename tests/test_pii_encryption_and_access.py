import base64
import re
from sqlalchemy import text
from flask_login import login_user

from app import db
from app.models import ElectoralRoll, User


def is_base64_padded(s: str) -> bool:
    if not isinstance(s, str):
        return False
    if len(s) < 40:
        return False
    if len(s) % 4 != 0:
        return False
    return re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", s) is not None


def test_pii_encrypted_at_rest(app):
    with app.app_context():
        # Create a fresh enrolment to ensure the TypeDecorator's bind hook runs
        user = User.query.filter_by(username='voter1').first()
        assert user is not None

        # Use the same region as existing data
        from app.models import Region
        region = Region.query.first()
        assert region is not None

        new_enrol = ElectoralRoll(
            roll_number='TEST999',
            driver_license_number='DL999999',
            full_name='Alice Example',
            date_of_birth=user.created_at.date(),
            address_line1='9 Example Rd',
            suburb='Examplestan',
            state='NSW',
            postcode='2999',
            region=region,
            status='active',
            verified=True,
            user=user,
        )
        db.session.add(new_enrol)
        db.session.commit()

        # ORM returns plaintext
        assert new_enrol.full_name == 'Alice Example'

        # Raw storage is encrypted
        row = db.session.execute(
            text("SELECT full_name FROM electoral_roll WHERE id = :id"), {"id": new_enrol.id}
        ).fetchone()
        stored = row[0]
        assert isinstance(stored, str)
        assert stored != 'Alice Example'
        assert is_base64_padded(stored)


def test_admin_can_view_pii(client, app):
    # Login as admin (created in tests/conftest.py)
    resp = client.post("/login", data={"username": "admin", "password": "Admin@123456!"}, follow_redirects=True)
    assert resp.status_code == 200

    # Admin voters page should include decrypted full name
    resp = client.get("/admin/voters", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Test Voter" in resp.data


def test_voter_cannot_view_admin_voters(client, app):
    # Login as regular voter
    resp = client.post("/login", data={"username": "voter1", "password": "Password@123!"}, follow_redirects=True)
    assert resp.status_code == 200

    # Attempt to access admin voters page; should redirect or show access denied without PII
    resp = client.get("/admin/voters", follow_redirects=True)
    assert resp.status_code == 200
    # Should not leak PII on the redirected page
    assert b"Test Voter" not in resp.data
