import json
import random
import time

from flask import Flask, abort

app = Flask(__name__)

def do_staff():
    time.sleep(random.gammavariate(alpha=3, beta=.1))

def do_slow():
    time.sleep(random.gammavariate(alpha=30, beta=0.3))

@app.route('/common')
def root():
    do_staff()
    return "I'm OK, I'm not alcoholic!"

@app.route('/slow')
def slow():
    if random.random() > .5:
        do_slow()
    else:
        do_staff()
    return "I'm a bit tired sometimes!"

@app.route('/fail')
def fail():
    do_staff()
    if random.random() > .9:
        abort(500)
    else:
        return "Move fast, break things!"

@app.route('/outage/<float:fail_rate>')
def outage(fail_rate):
    if random.random() < fail_rate:
        abort(500)
    else:
        do_staff()
        return "This is the end, my friend!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80', debug=True)
