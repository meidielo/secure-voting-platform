from app import create_app, db
from app.models import User
import datetime


def ensure_demo_user(app):
    with app.app_context():
        if not User.query.filter_by(username='demo').first():
            u = User(username='demo', email='demo@example.com')
            u.set_password('password')
            db.session.add(u)
            db.session.commit()

        # seed candidates if none exist
        from app.models import Candidate
        if Candidate.query.count() == 0:
            c1 = Candidate(name='Alice Johnson', position='Mayor')
            c2 = Candidate(name='Bob Smith', position='Mayor')
            db.session.add_all([c1, c2])
            db.session.commit()


if __name__ == '__main__':
    app = create_app()
    ensure_demo_user(app)
    # Disable the reloader to avoid multiple processes when running in background
    import os
    port = int(os.environ.get('PORT', '5000'))
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
