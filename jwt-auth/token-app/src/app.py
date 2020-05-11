import os
import json
import jwt
from functools import wraps

from flask import Flask, request, abort, g

app = Flask(__name__)

config = {
    'PUBLIC_KEY': os.environ.get('PUBLIC_KEY', '')
}

def get_user_from_token():
    id_token = request.headers['Authorization'].split(' ')[1].strip()
    decoded = jwt.decode(id_token, config['PUBLIC_KEY'], algorithms=['RS256'])
    request._id_token = decoded

@app.route('/users/me/token')
def me():
    return request._id_token

if __name__ == "__main__":
    app.before_request(get_user_from_token)
    app.run(host='0.0.0.0', port='80', debug=True)
