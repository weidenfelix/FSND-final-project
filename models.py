import logging

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, CheckConstraint
from config import Config, TestConfig

db = SQLAlchemy()

"""
setup_db(app)
    binds a flask application and a SQLAlchemy service
"""


def setup_db(app, testing=False):
    with app.app_context():
        # change db uri if testing
        app.config.from_object(TestConfig if testing else Config)
        logging.info(f' Loading db with URI: {app.config["SQLALCHEMY_DATABASE_URI"]}')
        db.init_app(app)
        db.create_all()


'''
MODELS
'''

association_table = db.Table(
    'association table',
    Column('poem_id', db.ForeignKey('poem.id'), primary_key=True),
    Column('tag_id', db.ForeignKey('tag.id'), primary_key=True)
)

'''
Extend the base Model class to add common methods
'''


class helperClass(db.Model):
    __abstract__ = True

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()


class Poem(helperClass):
    __tablename__ = 'poem'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String, unique=True)
    content = Column(db.String, nullable=False, unique=True)
    # constraints are not working yet
    rating = Column(db.Integer, CheckConstraint('rating>=1'), CheckConstraint('rating<=5'))
    tags = db.relationship('Tag', secondary=association_table, backref='poems')

    def __repr__(self):
        return f'<Poem(id={self.id}, name={self.name}, content={self.content} tags={self.tags})>'

    def short(self):
        return {
            'id': self.id,
            'content': self.content,
            'tags': [tag.long() for tag in self.tags]
        }

    def long(self):
        return {
            'id': self.id,
            'name': self.name,
            'content': self.content,
            'rating': self.rating,
            'tags': [tag.long() for tag in self.tags]
        }


class Tag(helperClass):
    __tablename__ = 'tag'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(length=50), nullable=False, unique=True)

    def __repr__(self):
        return f'<Tag(id={self.id}, name={self.name})>'

    def long(self):
        return {
            'id': self.id,
            'name': self.name
        }
