from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

from models import Poem, Tag
from models import db, setup_db


def create_app(testing=False):
    app = Flask(__name__)
    setup_db(app, testing)
    CORS(app)
    migrate = Migrate(app, db)

    @app.route('/poems')
    def get_poems():
        poem = Poem.query.get(1).format()
        return poem

    return app


app = create_app()
