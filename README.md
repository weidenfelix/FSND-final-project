# GPoetr-3 
## a literary API

This API accesses OpenAI's GPT-3 API to create and store 
poems. GPoetr-3 is hosted on heroku: https://fsnd-poetry-app.herokuapp.com/ 

### Authentication

Users get authorized over Auth0. You first have to curl the /login endpoint. It returns
a link to Auth0, where you can either log in as yourself, without permissions or try out
the following pre-made accounts:

Poet Role: poet@gmail.com heroku123!
Editor Role: editor@gmail.com heroku123!

Auth0 redirects back to /callback and your browser should display the Authorization Header needed
for the protected endpoints. Copy the header and add it to your future curl requests!

PS: The Poet has access to all endpoints, while the editor cannot write poems by themselves.

### Tests

In order to run tests, clone the repo, create a database named test_local_poetry, and you 
can run pytest from the console, with a custom arg --token as the access_token from above.

**run all public tests:**
pytest tests/endpoint_tests.py -m 'not auth_required and not editor' --token $TOKEN

**run tests that require auth with an access_token from the poet role:**
pytest tests/endpoint_tests.py -m 'auth_required' --token $POET_TOKEN

**run tests that check the seperation between editor and poet:**
pytest tests/endpoint_tests.py -m 'editor' --token $EDITOR_TOKEN 

### ENDPOINTS
**The GETs are pretty straight forward:**

GET /poems

GET /poems/tag_name 

GET /poems/rating

_Get all poems or grouped by tag or rating._

GET /poem/poem_id

GET /poem/poem_name

_Get a single poem by id or name._

**POST takes a list of adjective strings and a topic_string (and an optional "temperature" key
that from 0-1 ~says how deterministic the content is going to be), communicates
with OpenAI's API and saves the created poem to the db.**

POST /write-poem

*curl -X POST https://fsnd-poetry-app.herokuapp.com/write-poem --header "Authorization: Bearer $TOKEN" --header "Content-Type: application/json"  
    --data '{"adjectives":["vast", "flowery"], "topic":"mountains"}'*

PS: inputs are limited to 25 characters each

**PATCH lets one add a name, rating and tags to a poem. 
Ratings are only allowed from 1-5.**

PATCH /poem/poem_id 

*curl -X PATCH https://fsnd-poetry-app.herokuapp.com/poem/1 --header "Authorization: Bearer $TOKEN" --header "Content-Type: application/json"  
    --data '{"name": "the peak above", "rating": 1}'*

**DELETE**

DELETE /poem/poem_id

DELETE /poem/poem_id/tag_name

_The latter removes a tag from a poem._
