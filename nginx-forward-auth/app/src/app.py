import os
from flask import Flask, request

app = Flask(__name__)

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
    return data

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80', debug=True)
