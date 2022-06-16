import pytest
from models import db, Poem, Tag

'''
AUTH TESTING
'''

dummy_json = {
    'name': 'This should not get through',
    'rating': 5,
    'tags': []
}


def test_401_if_authorization_header_missing(client):
    response = client.post('/write-poem', json=dummy_json)
    assert response.status_code == 401

def test_401_if_header_invalid(client):
    headers = {'Authorization': 'Bear Token'}
    response = client.post('/write-poem', json=dummy_json, headers=headers)
    assert response.status_code == 401

    headers = {'Authorization': 'BearerToken'}
    response = client.post('/write-poem', json=dummy_json, headers=headers)
    assert response.status_code == 401

    headers = {'Authorization': 'Bear Token Token'}
    response = client.post('/write-poem', json=dummy_json, headers=headers)
    assert response.status_code == 401


