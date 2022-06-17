from os import environ as env

import pytest, logging
from app import create_app
from models import setup_db, db, Poem, Tag
from requests import post
from config import AUTH0_DOMAIN, API_AUDIENCE, TESTUSER_NAME, TESTUSER_PASSWORD, API_CLIENT_ID
from dotenv import load_dotenv
from flask import abort


# scope lets us use the same app for every test
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

    tag1 = Tag(id=1, name='poetic')
    tag2 = Tag(id=2, name='horrific')
    poem1 = Poem(id=1, name='testpoem1', content='testing is easy, life is easy, please freeze me', rating=5,
                 tags=[tag1])
    poem2 = Poem(id=2, name='testpoem2', content='rain is wet, I won a bet, because Jane, slipped in the rain',
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

# login as testuser and provide access token for testing
@pytest.fixture()
def auth_header(client):
    load_dotenv()

    response = post(url=f'https://{AUTH0_DOMAIN}/oauth/token', headers={'content-type': 'application/json'}, json={
        'client_id': API_CLIENT_ID,
        'client_secret': env.get('API_CLIENT_SECRET'),
        'audience': API_AUDIENCE,
        'grant_type': 'password',
        'username': TESTUSER_NAME,
        'password': TESTUSER_PASSWORD
    }).json()
    if not response['access_token']:
        abort(500)
    auth_header = {'Authorization': f'Bearer {response["access_token"]}'}
    return auth_header
