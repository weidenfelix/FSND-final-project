import os
from dotenv import load_dotenv
import logging

'''
LOGGING CONFIG
'''

logging.basicConfig(level=logging.INFO)

'''
APP CONFIG
'''


class Config(object):
    # loads .env into environment; separates local build and heroku
    load_dotenv()
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# TODO:
# make test db in heroku
class TestConfig(object):
    load_dotenv()
    SQLALCHEMY_DATABASE_URI = os.environ['TEST_DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
