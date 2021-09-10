import os
import json

from flask import Flask, request

app = Flask(__name__)

config = {
    'DATABASE_URI': os.environ.get('DATABASE_URI', ''),
}

from sqlalchemy import create_engine
engine = create_engine(config['DATABASE_URI'], echo=True)

@app.route('/users/me')
def me():
    if not 'X-UserId' in request.headers:
        return "Not authenticated"
    data = {}
    data['id'] = request.headers['X-UserId']
    data['login'] = request.headers['X-User']
    data['email'] = request.headers['X-Email']
    data['first_name'] = request.headers['X-First-Name']
    data['last_name'] = request.headers['X-Last-Name']

    rows = []
    with engine.connect() as connection:
        result = connection.execute(
            "select avatar_uri, age from user_profile "
            "where id={} limit 1".format(data['id']))
        rows = [dict(r.items()) for r in result]

    if rows:
        data['avatar_uri'] = rows[0]['avatar_uri']
        data['age'] = rows[0]['age']

    return data

@app.route("/users/me", methods=["PUT"])
def updateMe():
    if not 'X-UserId' in request.headers:
        return "Not authenticated"
    request_data = request.get_json()
    id = request.headers['X-UserId']
    avatar_uri = request_data['avatar_uri']
    age = request_data['age']
    with engine.connect() as connection:
        connection.execute(
            """
            insert into user_profile (id, avatar_uri, age)
            values ('{}', '{}', {})
            on conflict (id)
            do update set
                avatar_uri = excluded.avatar_uri,
                 age = excluded.age;
            """.format(id, avatar_uri, age))
    data = {}
    data['id'] = id
    data['avatar_uri'] = avatar_uri
    data['age'] = age

    return data

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80', debug=True)
