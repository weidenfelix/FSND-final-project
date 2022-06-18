import logging

import pytest

from models import Poem, Tag

'''
ENDPOINT TESTING
'''

'''
GET
'''


def test_get_poems(client):
    response = client.get('/poems')
    poems = [poem.format() for poem in Poem.query.all()]
    assert response.json == {'poems': poems}


def test_get_poems_by_tag(client):
    tag_name = Poem.query.first().tags[0].name
    response = client.get(f'/poems/{tag_name}')
    poems_by_tag = list(map(lambda poem: poem.format(), Tag.query.filter_by(name=tag_name).first().poems))
    assert response.json == {'poems': poems_by_tag}


def test_get_poems_404_unknown_tag(client):
    response = client.get(f'/poems/THISISNOTATAG')
    assert response.status_code == 404


def test_get_poems_by_rating(client):
    rating = Poem.query.first().rating
    response = client.get(f'/poems/{rating}')
    poems_by_rating = list(map(lambda poem: poem.format(), Poem.query.filter_by(rating=rating).all()))
    assert response.json == {'poems': poems_by_rating}


def test_get_poem_by_id(client):
    id = Poem.query.first().id
    response = client.get(f'/poem/{id}')
    poem_by_id = Poem.query.get(id)
    assert response.json == {'poem': poem_by_id.format()}


def test_get_poem_by_name(client):
    name = Poem.query.first().name
    response = client.get(f'/poem/{name}')
    poem_by_name = Poem.query.filter_by(name=name).first()
    assert response.json == {'poem': poem_by_name.format()}


'''
POST
'''


@pytest.mark.auth_required
def test_post_write_poem(client, auth_header):
    response = client.post('/write-poem', headers=auth_header, json={
        'topic': 'tree in winter',
        'adjectives': ['strong', 'sleepy'],
        'temperature': 0.1
    })
    assert response.status_code == 200


@pytest.mark.auth_required
def test_post_write_poem_422_inputs_too_long(client, auth_header):
    response = client.post('/write-poem', headers=auth_header, json={
        'topic': 'treeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeees',
        'adjectives': ['strong', 'sleepy'],
        'temperature': 0.1
    })
    assert response.status_code == 422


'''
PATCH
'''


@pytest.mark.auth_required
def test_patch_poem(client, auth_header):
    poem = Poem.query.first()
    response = client.patch(f'/poem/{poem.id}', headers=auth_header, json={
        'name': 'This was patched. 555',
        'rating': 5,
        'tags': []
    })
    assert response.status_code == 200
    # assert change, maybe more needed?
    assert Poem.query.get(poem.id) != poem


@pytest.mark.auth_required
def test_patch_wrong_keys_422(client, auth_header):
    poem = Poem.query.first()
    response = client.patch(f'/poem/{poem.id}', headers=auth_header, json={
        'WRONG': 'This was patched. 555',
        'rating': 5,
        'tags': []
    })
    assert response.status_code == 422


'''
DELETE
'''


@pytest.mark.auth_required
def test_delete_poem(client, auth_header):
    poem_id = Poem.query.first().id
    response = client.delete(f'/poem/{poem_id}', headers=auth_header)
    assert response.status_code == 200
    assert Poem.query.get(poem_id) is None
    assert response.json == {'deleted_poem_id': poem_id}


@pytest.mark.auth_required
def test_delete_poem_404_not_found(client, auth_header):
    response = client.delete(f'/poem/1000', headers=auth_header)
    assert response.status_code == 404


@pytest.mark.auth_required
def test_delete_tag_from_poem(client, auth_header):
    poem = Poem.query.first().format()
    tag = poem['tags'][0]
    response = client.delete(f'/poem/{poem["id"]}/{tag["name"]}', headers=auth_header)
    poem['tags'].remove(tag)
    assert response.status_code == 200
    assert response.json == {'poem': poem}


'''
AUTH_TESTING
'''


@pytest.mark.editor
def test_editor_cant_write_poems(client, auth_header):
    response = client.post('/write-poem', headers=auth_header, json={
        'topic': 'tree in winter',
        'adjectives': ['strong', 'sleepy'],
        'temperature': 0.1
    })
    assert response.status_code == 403

@pytest.mark.editor
def test_editor_can_delete_poem(client, auth_header):
    poem_id = Poem.query.first().format().get('id')
    response = client.delete(f'/poem/{poem_id}', headers=auth_header)
    assert response.status_code == 200
