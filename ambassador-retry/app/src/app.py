import os
import json
import random
import time

from flask import Flask, abort

app = Flask(__name__)

FAIL_RATE=float(os.environ.get('FAIL_RATE', '0.01'))
SLOW_RATE=float(os.environ.get('SLOW_RATE', '0.01'))

def do_staff():
    time.sleep(random.gammavariate(alpha=3, beta=.1))

def do_slow():
    time.sleep(random.gammavariate(alpha=30, beta=0.3))

@app.route('/probe')
def probe():
    if random.random() < FAIL_RATE:
        abort(500)
    if random.random() < SLOW_RATE:
        do_slow()
    else:
        do_staff()
    return "I'm ok! I'm not alcoholic"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80', debug=True)
