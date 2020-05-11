import os
import json

from flask import Flask, request, abort, redirect

app = Flask(__name__)

config = {
    'DATABASE_URI': os.environ.get('DATABASE_URI', ''),
    'PRIVATE_KEY': os.environ.get('PRIVATE_KEY', ''),
    'PUBLIC_KEY': os.environ.get('PUBLIC_KEY', ''),
}

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError

engine = create_engine(config['DATABASE_URI'], echo=True)

def register_user(login, password, email, first_name, last_name):
    try:
        with engine.connect() as connection:
            result = connection.execute(
                """
                insert into auth_user (login, password, email, first_name, last_name)
                values ('{}', '{}', '{}', '{}', '{}') returning id;
                """.format(login, password, email, first_name, last_name)).first()
            id_ = result['id']
        return {"id": id_}
    except IntegrityError:
        abort(400, "login/email already exists")

def get_user_by_credentials(login, password):
    rows = []
    with engine.connect() as connection:
        result = connection.execute(
            "select id, login, email, first_name, last_name from auth_user "
            "where login='{}' and password='{}'".format(login, password))
        rows = [dict(r.items()) for r in result]
    return rows[0]

def create_id_token(user_info):
    import jwt
    import datetime
    data = {
        "iss": "http://arch.homework",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
        "sub": user_info["id"],
        "email": user_info["email"],
        "given_name": user_info["first_name"],
        "family_name": user_info["last_name"]
    }
    encoded = jwt.encode(data, config['PRIVATE_KEY'], algorithm='RS256', headers={'kid': '1'})
    return encoded.decode('utf-8')

@app.route("/register", methods=["POST"])
def register():
    request_data = request.get_json()
    # add validation
    login = request_data['login']
    password = request_data['password']
    email = request_data['email']
    first_name = request_data['first_name']
    last_name = request_data['last_name']
    return register_user(login, password, email, first_name, last_name)

@app.route("/login", methods=["POST"])
def login():
    request_data = request.get_json()
    login = request_data['login']
    password = request_data['password']
    user_info = get_user_by_credentials(login, password)
    if user_info:
        id_token = create_id_token(user_info)
        response = app.make_response({"IDtoken": id_token})
        return response
    else:
        abort(401)

@app.route( "/.well-known/jwks.json")
def jwks():
    from authlib.jose import JsonWebKey
    from authlib.jose import JWK_ALGORITHMS
    jwk = JsonWebKey(algorithms=JWK_ALGORITHMS)
    key = jwk.dumps(config['PUBLIC_KEY'], kty='RSA')
    key['kid'] = '1'
    return {"keys": [key]}

@app.route("/health")
def health():
    return {"status": "OK"}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80', debug=True)
