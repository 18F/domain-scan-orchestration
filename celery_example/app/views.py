from app import app
from app.models import Domains
from app import db
from flask import render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from app import celery_obj
import pandas as pd
import os
import datetime as dt
from app.tasks import uswds, gatherer

ALLOWED_EXTENSIONS = set(['csv'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_csv_to_db(file_path):
    df = pd.read_csv(file_path)
    for index in df.index:
        # dt.datetime.now is bad, change this in the near future
        domain = Domains(df.ix[index]["domain"], dt.datetime.now())
        db.session.add(domain)
        db.session.commit()

@app.route("/initialize_database", methods=["GET","POST"])
def init_db():
    db.create_all()
    return "database created"


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            save_csv_to_db(file_path)
            return render_template("index.html")
    return render_template("index.html")


@app.route("/kick_off", methods=["GET","POST"])
def kick_off():
    """
    Kicks off a scan rather than waiting for the scheduler
    """
    uswds.delay()
    return "scanners engaged"

@app.route("/gather", methods=["GET","POST"])
def gather():
    # fix this
    gatherer.delay()
    return "success"
