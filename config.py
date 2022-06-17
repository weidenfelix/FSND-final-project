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

load_dotenv()

AUTH0_DOMAIN = 'dev-edtgxxcz.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'https://poetry-api'

AUTH0_CLIENT_ID="QYhS1Lqo5NQZRckZg59XPy2DfcXD61WQ"
API_CLIENT_ID="HlQcyOXJaH5jnR9mFIrF5u3ABHRtlFke"

TESTUSER_NAME="testuser1@gmail.com"
TESTUSER_PASSWORD="@23qdyG6Rw&z"


class Config(object):
    # we switch DB URI if we are local or in heroku; assuming that DATABASE_URL and HEROKU_..._URL only exist in heroku
    try:
        # heroku calls db starting with URL postgres:// but within psql this has changed to postgresql, so we edit
        # manually
        SQLALCHEMY_DATABASE_URI = env.get('DATABASE_URL').replace("://", "ql://", 1)
    except:
        SQLALCHEMY_DATABASE_URI = env.get('LOCAL_DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(object):
    SQLALCHEMY_DATABASE_URI = env.get('LOCAL_TEST_DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

