import pytest
from app.main import create_app
from app.extensions import db as _db
from app.models.mst_user import User


@pytest.fixture(scope='session')
def app():
    """Create application with in-memory SQLite for testing."""
    test_app = create_app('testing')

    with test_app.app_context():
        _db.create_all()
        yield test_app
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    with app.app_context():
        yield _db
        _db.session.remove()


@pytest.fixture()
def test_user(db):
    user = User(username='testuser')
    user.set_password('testpass123')
    db.session.add(user)
    db.session.commit()
    yield user
    db.session.delete(user)
    db.session.commit()
