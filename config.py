from os import environ as env
from dotenv import load_dotenv
import logging

'''
LOGGING CONFIG
'''

logging.basicConfig(level=logging.INFO)

'''
APP CONFIG
'''

# loads .env into environment; separates local build and heroku
load_dotenv()

AUTH0_DOMAIN = 'dev-edtgxxcz.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'https://poetry-api'

AUTH0_CLIENT_ID="QYhS1Lqo5NQZRckZg59XPy2DfcXD61WQ"
API_CLIENT_ID="HlQcyOXJaH5jnR9mFIrF5u3ABHRtlFke"

TESTUSER_NAME="testuser1@gmail.com"
TESTUSER_PASSWORD="@23qdyG6Rw&z"

heroku_test_db_url = env.get('HEROKU_POSTGRESQL_BROWN_URL')

class Config(object):

    SQLALCHEMY_DATABASE_URI = env.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(object):
    # switch url if testing online/local
    if heroku_test_db_url:
        SQLALCHEMY_DATABASE_URI = heroku_test_db_url
    else:
        SQLALCHEMY_DATABASE_URI = env.get('TEST_DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

