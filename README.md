# GPoetr-3 
## a literary API

GPoetr-3 accesses OpenAI's GPT-3 API to create and store poems. It is hosted on heroku: 
> https://fsnd-poetry-app.herokuapp.com/ 

This project is meant to demonstrate and solidify the skills I have acquired in Udacity's Fullstack Nanodegree. 
It shows an understanding of Flask API development, database design with SQLAlchemy, testing with pytest and 
Authentication via Auth0.


All backend code follows PEP8 style guidelines.

## Installing Dependencies
### Python 3.8
Follow instructions to install the correct version of Python for your platform
in the python docs.

### Pipenv
I recommend using pipenv for Python projects. It is a combination of pip and a virtual env, so you can install and 
manage dependencies in one place. Install steps from here: 
> https://pipenv.pypa.io/en/latest/  

Once installed, navigate to the root directory and run:  

    pipenv install  


This will install all the required packages included in the Pipfile. If you add or edit a dependency and want to include
a requirements.txt run:

    pipenv lock -r > requirements.txt

This updates the .txt to match the actual dependencies.

### Loading vars into environment
To get all the config vars into your environment, run:

    source setup.sh

### Local Database Setup
Once you create the database, open your terminal, navigate to the root folder, and run:

    flask db init  
    flask db migrate -m "Initial migration."  
    flask db upgrade

After running, don't forget to modify the SQLALCHEMY_DATABASE_URI variable, if any of your settings
differ from the default: 

> postgresql://postgres:123@localhost:5432/local_poetry

For testing you also have to create a 

    test_local_poetry 

database (or call it what you want and edit the LOCAL_TEST_DATABASE_URL). If there are any errors double-check your URI.

### Local Testing
To test your local installation, run the following command from the root folder, which will test the public
endpoints:

    pytest tests/endpoint_tests.py -m 'not poet and not editor'

If all tests pass, your local installation is set up correctly.

### Running the server locally
From within the root directory, first ensure you're working with your created
pipenv. As the FLASK vars are already set, run the server, execute the following:

    flask run

### Heroku
Heroku uses a gunicorn server to host this application. It automatically deploys every new push from this repo!

### Authentication

Users get authorized over Auth0. To login, open this in your browser.
    
    https://fsnd-poetry-app.herokuapp.com/login

You get redirected to Auth0 where you can use the credentials specified below.  
After that you will be redirected to the /callback endpoint, 
where the browser should display an access_token, that you have to copy into your environment
like this:

    export TOKEN=

### Roles
#### Poet Role
_Permissions:_ 
- post:write-poem
- delete:poem
- delete:tag-from-poem
- patch:poem

Credentials:  
> username: poet@gmail.com 
> 
> password: heroku123!

#### Editor Role: 
_Permissions:_ 
- delete:poem
- delete:tag-from-poem
- patch:poem

Credentials:  
> username: editor@gmail.com 
> 
> password: heroku123!



### Advanced Testing
To test the protected endpoints that require at least **Editor** permissions:

    pytest tests/endpoint_tests.py -m 'editor' --token $TOKEN

To test the protected endpoints that require at least **Poet** permissions:

    pytest tests/endpoint_tests.py -m 'poet' --token $TOKEN 

### ENDPOINTS

**GET /poems**
- Returns all poems.
- Example:

```
curl https://fsnd-poetry-app.herokuapp.com/poems
```
```
{"poems":
    [
        {
        "content":"\n\nI believe in destiny,\nThat there's a reason for everything,\nThat everything happens for a reason,\n\nAnd that our lives are meant to be.\n\nI believe that we're all connected,\n\nAnd that our",
        "id":3,
        "name":null,
        "rating":null,
        "tags":[{"id":5,"name":"rich"}]
        },
        {
        "content":"\n\nThere are so many animals in the world\nEach with their own unique story\nSome are big, some are small\nSome are fast, some are slow\nSome can fly, some can't\nBut they all have one thing in common",
        "id":4,
        "name":null,
        "rating":null,
        "tags":[{"id":6,"name":"vast"}, [...]
    ]
}
```

**GET /poems/tag_name** 
- Returns all poems that share a tag.
- Example:

```
curl https://fsnd-poetry-app.herokuapp.com/poems/vast
```

**GET /poems/rating**
- Returns all poems that share the same rating.
- Example:

```
curl https://fsnd-poetry-app.herokuapp.com/poems/5
```

**GET /poem/poem_id**
- Returns the poem with poem_id.
- Example:

```
curl https://fsnd-poetry-app.herokuapp.com/poem/1
```

**GET /poem/poem_name**
- Returns the poem with poem_name.
- Example:

```
curl https://fsnd-poetry-app.herokuapp.com/poem/mountaintop
```

**POST /write-poem**

- Calls OpenAI's API to write a poem that gets saved to the db.
- Inputs are restricted to 25 chars each.
- Accepts json with required _'topic'_ and _'adjectives'_:

```
{
'topic': string, 
'adjectives': list(string), 
'temperature': int [optional]
}   
```

- Example:

```
curl -X POST https://fsnd-poetry-app.herokuapp.com/write-poem --header "Authorization: Bearer $TOKEN" --header "Content-Type: application/json" --data '{"adjectives":["vast", "flowery"], "topic":"mountains"}'
```
```
{
"poem":
    {
    "content":"\n\nTheodore Roosevelt once said, \"Climb the mountains and get their good tidings. Nature's peace will flow into you as sunshine flows into trees. The winds will blow their own freshness into you, and the storms their energy",
    "id":7,
    "tags":[{"id":1,"name":"vast"},{"id":2,"name":"flowery"}]
    }
}
```

**PATCH /poem/poem_id** 
- Updates a poem's name, rating or tags (tags don't get overwritten, but these get added to existing).
- Accepts json with at least one of the keys:

```
{
'name': string, 
'rating': int, 
'tags': list(string)
}   
```

- Example:

```
curl -X PATCH https://fsnd-poetry-app.herokuapp.com/poem/7 --header "Authorization: Bearer $TOKEN" --header "Content-Type: application/json" --data '{"name": "nature's gift", "rating": 1}'
```
```
{
"patched_poem":
    {
    "content":"\n\nTheodore Roosevelt once said, \"Climb the mountains and get their good tidings. Nature's peace will flow into you as sunshine flows into trees. The winds will blow their own freshness into you, and the storms their energy",
    "id":7,
    "name":"natures gift",
    "rating":1,
    "tags":[{"id":1,"name":"vast"},{"id":2,"name":"flowery"}]
    }
}
```

**DELETE /poem/poem_id**
- Deletes poem with poem_id.
- Example:

```
curl -X DELETE https://fsnd-poetry-app.herokuapp.com/poem/7 --header "Authorization: Bearer $TOKEN"
```
```
{
"deleted_poem_id":7
}
```
**DELETE /poem/poem_id/tag_name**
- Deletes tag with tag_name from poem with poem_id.
- Example:

```
curl -X DELETE https://fsnd-poetry-app.herokuapp.com/poem/7/vast --header "Authorization: Bearer $TOKEN"
```
```
{
"poem":
    {
    "content":"\n\nTheodore Roosevelt once said, \"Climb the mountains and get their good tidings. Nature's peace will flow into you as sunshine flows into trees. The winds will blow their own freshness into you, and the storms their energy",
    "id":7,
    "tags":[{"id":2,"name":"flowery"}]
    }
}

```
