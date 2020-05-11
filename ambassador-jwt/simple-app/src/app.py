import os
import json
import jwt
from functools import wraps

from flask import Flask, request

app = Flask(__name__)

@app.route('/users/me')
def me():
    user = {}
    user['id'] = request.headers['X-User-Id']
    user['email'] = request.headers['X-Email']
    user['first_name'] = request.headers['X-First-Name']
    user['last_name'] = request.headers['X-Last-Name']
    return user

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80', debug=True)
