import sys
import openai
import requests
import flask, logging
from flask import Flask, jsonify, abort, request, redirect, url_for
from flask_cors import CORS
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth
from os import environ as env

from config import AUTH0_CLIENT_ID, AUTH0_DOMAIN, API_AUDIENCE
from models import Poem, Tag
from models import db, setup_db
from auth.auth_decorator import requires_auth, AuthError


def create_app():
    app = Flask(__name__)
    app.secret_key = env.get('APP_SECRET_KEY')

    CORS(app)
    migrate = Migrate(app, db)

    # https://auth0.com/docs/quickstart/webapp/python/01-login
    oauth = OAuth(app)
    oauth.register(
        "auth0",
        client_id=AUTH0_CLIENT_ID,
        client_secret=env.get('AUTH0_CLIENT_SECRET'),
        client_kwargs={
            "scope": "openid profile email",
        },
        server_metadata_url=f'https://{AUTH0_DOMAIN}/.well-known/openid-configuration'
    )

    '''
    LOGIN
    '''

    @app.route("/login")
    def login():
        return oauth.auth0.authorize_redirect(
            redirect_uri=url_for("callback", _external=True),
            audience=API_AUDIENCE
        )

    @app.route("/callback", methods=["GET", "POST"])
    def callback():
        token = oauth.auth0.authorize_access_token()['access_token']
        return jsonify({
            'Authorization': f'Bearer {token}'
        })

    '''
    GET
    '''

    @app.route('/', methods=['GET'])
    def info():
        return (
            '##########################################\n'
            'WELCOME TO GPoetr-3\n\n'
            'THE LITERARY API ACCESSING OPEN AI\'S GPT-3\n\n'
            'FOR YOUR POETIC NEEDS\n'
            '##########################################\n'
        )

    @app.route('/poems', methods=['GET'])
    def get_poems():
        poems = Poem.query.all()
        return jsonify({'poems': [poem.format() for poem in poems]})

    @app.route('/poems/<string:tag_name>', methods=['GET'])
    def get_poems_by_tag(tag_name):
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            abort(404)
        poems = tag.poems
        return jsonify({'poems': [poem.format() for poem in poems]})

    @app.route('/poems/<int:rating>', methods=['GET'])
    def get_poems_by_id(rating):
        poems = Poem.query.filter_by(rating=rating).all()
        if not poems:
            abort(404)
        return jsonify({'poems': [poem.format() for poem in poems]})

    @app.route('/poem/<int:poem_id>', methods=['GET'])
    def get_poem_by_id(poem_id):
        poem = Poem.query.get(poem_id)
        if not poem:
            abort(404)
        return jsonify({'poem': poem.format()})

    @app.route('/poem/<string:poem_name>', methods=['GET'])
    def get_poem_by_name(poem_name):
        poem = Poem.query.filter_by(name=poem_name).first()
        if not poem:
            abort(404)
        return jsonify({'poem': poem.format()})

    '''
    POST
    '''

    @app.route('/write-poem', methods=['POST'])
    @requires_auth(permission='post:write-poem')
    def post_write_poem():
        r = request.get_json()
        topic = r.get('topic', 0)
        adjectives = r.get('adjectives', 0)
        if not topic or not adjectives:
            abort(422)
        # restrict length of query
        if len(''.join(r.get('topic'))) > 25 or len(''.join(adjectives)) > 25:
            abort(422)
        openai.api_key = env.get('OPENAI_API_KEY')
        openai.Model.list()

        prompt = f'Write a {", ".join(adjectives)} poem about {topic}.'
        response = requests.post(url='https://api.openai.com/v1/completions',
                                 json={'model': 'text-davinci-002',
                                       'prompt': f'{prompt}',
                                       'temperature': r.get('temperature', 0.7),
                                       'max_tokens': 50},
                                 headers={'Authorization': f'Bearer {openai.api_key}'})
        if response.status_code != 200:
            abort(500)
        content = response.json().get('choices')[0].get('text')
        # check if tag already exists, if not create
        tags = []
        for adjective in adjectives:
            tag = Tag.query.filter_by(name=adjective).first()
            if not tag:
                tag = Tag(name=adjective)
            tags.append(tag)
        poem = Poem(content=content, tags=tags)
        try:
            poem.insert()
            poem_id = poem.id
        except:
            db.session.rollback()
            logging.error(f'{poem} could not be added:\n'
                          f'{sys.exc_info()}')
            abort(500)
        finally:
            db.session.close()

        return {'poem': Poem.query.get(poem_id).format()}

    '''
    PATCH
    '''

    @app.route('/poem/<int:poem_id>', methods=['PATCH'])
    @requires_auth(permission='patch:poem')
    def patch_poem(poem_id):
        r = request.get_json()
        allowed_keys = ['name', 'rating', 'tags']
        # if request is empty or there is a request key that is not allowed, 422
        if not r or not all(map(lambda key: key in allowed_keys, r)):
            abort(422)
        poem = Poem.query.get(poem_id)
        if not poem:
            abort(404)
        try:
            # patched tags get appended to existing
            if 'tags' in r:
                for tag_name in r['tags']:
                    poem.tags.append(Tag(name=tag_name))
                # and when done removed from keys
                r.pop('tags')
            for key in r:
                setattr(poem, key, r[key])
            poem.insert()
            f_poem = poem.format()
        except:
            db.session.rollback()
            logging.error(f'{poem} could not be patched:\n'
                          f'{sys.exc_info()}')
            abort(500)
        finally:
            db.session.close()
        return jsonify({
            'patched_poem': f_poem
        })

    '''
    DELETE
    '''

    @app.route('/poem/<int:poem_id>', methods=['DELETE'])
    @requires_auth(permission='delete:poem')
    def delete_poem(poem_id):
        poem = Poem.query.get(poem_id)
        if not poem:
            abort(404)
        try:
            poem.delete()
        except:
            db.session.rollback()
            logging.error(f'{poem} could not be deleted:\n'
                          f'{sys.exc_info()}')
            abort(500)
        finally:
            db.session.close()
        return jsonify({
            'deleted_poem_id': poem_id
        })

    @app.route('/poem/<int:poem_id>/<string:tag_name>', methods=['DELETE'])
    @requires_auth(permission='delete:tag-from-poem')
    def delete_tag_from_poem(poem_id, tag_name):
        poem = Poem.query.get(poem_id)
        tag = Tag.query.filter_by(name=tag_name).first()
        # check that both exist and related
        if not (poem and tag) or poem not in tag.poems:
            abort(404)
        try:
            poem.tags.remove(tag)
            poem.insert()
            f_poem = poem.format()
        except:
            db.session.rollback()
            logging.error(f'{tag} could not be deleted from {poem}:\n{sys.exc_info()}')
            abort(500)
        finally:
            db.session.close()
        return jsonify({
            'poem': f_poem
        })

    '''
    ERROR HANDLING
    '''

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'error': 422,
            'message': 'unprocessable entity'
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'error': 500,
            'message': 'internal server error'
        }), 500

    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        response = jsonify(ex.error)
        response.status = ex.status_code
        return response

    return app


app = create_app()
setup_db(app)
