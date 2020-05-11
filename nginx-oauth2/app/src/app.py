import os
from flask import Flask, request

app = Flask(__name__)

@app.route('/users/me')
def me():
    if not 'X-Auth-Request-User' in request.headers:
        return "Not authenticated"
    data = {}
    data['email'] = request.headers['X-Auth-Request-Email']
    data['user'] = request.headers['X-Auth-Request-User']
    return data

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80', debug=True)
