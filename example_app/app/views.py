from app import app
from app import db
from flask import render_template, request, jsonify
from app import celery


@celery.task
def count_to_a_million():
    for i in range(1000000):
        i + 1
    return i

@app.route('/', methods=['GET','POST'])
def index():
    return "it works"


@app.route('/awaiting', methods=["GET", "POST"])
def awaiting():
    result = count_to_a_million.delay()
    return str(result.ready())
