import os
import json

from flask import Flask
from metrics import register_metrics

app = Flask(__name__)

config = {
    'DATABASE_URI': os.environ.get('DATABASE_URI', ''),
    'HOSTNAME': os.environ['HOSTNAME'],
    'GREETING': os.environ.get('GREETING', 'Hello'),
}

@app.route("/")
def hello():
    return config['GREETING'] + ' from ' + config['HOSTNAME'] + '!'

@app.route("/config")
def configuration():
    return json.dumps(config)

@app.route('/db')
def db():
    from sqlalchemy import create_engine
    engine = create_engine(config['DATABASE_URI'], echo=True)
    rows = []
    with engine.connect() as connection:
        result = connection.execute("select id, name from client;")
        rows = [dict(r.items()) for r in result]
    return json.dumps(rows)

@app.route('/metrics')
def metrics():
    from prometheus_client import generate_latest
    return generate_latest()

if __name__ == "__main__":
    register_metrics(app)
    app.run(host='0.0.0.0', port='80', debug=True)
