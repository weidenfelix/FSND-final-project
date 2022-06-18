import pytest, logging
from app import create_app
from models import setup_db, db, Poem, Tag


# scope lets use only one app for all tests
@pytest.fixture(autouse=True, scope='session')
def app():
    app = create_app()
    app.app_context().push()
    logging.info('creating new app instance')
    app.testing = True
    return app


@pytest.fixture(autouse=True)
def setup_test_db(app):
    setup_db(app, testing=True)
    db.drop_all()
    db.create_all()
    logging.info('recreating test db')

    tag1 = Tag(name='poetic')
    tag2 = Tag(name='horrific')
    poem1 = Poem(name='testpoem1', content='testing is easy, life is easy, please freeze me', rating=5,
                 tags=[tag1])
    poem2 = Poem(name='testpoem2', content='rain is wet, I won a bet, because Jane, slipped in the rain',
                 rating=4,
                 tags=[tag1, tag2])
    test_data = [poem1, poem2]

    try:
        for obj in test_data:
            db.session.add(obj)
        db.session.commit()
    except:
        db.session.rollback()
        logging.error('TEST_DB COULD NOT BE SETUP')
    finally:
        db.session.close()
    yield
    # clean all sessions and empty db; without closing postgres gets stuck
    db.close_all_sessions()
    db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


# these 2 functions let us enter the access token via commandline
def pytest_addoption(parser):
    parser.addoption("--token", action="store", default="")


@pytest.fixture(scope="session")
def auth_header(pytestconfig):
    token = pytestconfig.getoption("token")
    return {'Authorization': f'Bearer {token}'}
