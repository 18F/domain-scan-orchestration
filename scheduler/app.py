from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask import render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import os
from celery import Celery
from celery.schedules import crontab
import cfenv
import pandas as pd
from io import StringIO
import requests
import datetime as dt
import json
import boto
from boto.s3.key import Key
from werkzeug.utils import secure_filename
import censys_api
from github import Github
from github import InputGitTreeElement

env = cfenv.AppEnv()


ALLOWED_EXTENSIONS = set(['csv'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    if not os.path.exists("csv_upload"):
        os.mkdir("csv_upload")

def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['result_backend'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


def get_redis_url():
    redis = env.get_service(label='redis28')
    if redis:
        url = redis.get_url(host='hostname', password='password', port='port')
        return 'redis://{}'.format(url)
    return env.get_credential('REDIS_URL', 'redis://localhost:6379')

def string_to_list(string):
    return string.split("\n")


def string_to_df_to_list(string):
    data = StringIO(string)
    df = pd.read_csv(data, sep=",")
    return list(df["Domain Name"])


def upload_to_s3(csv_file_contents, bucket_name):
    # Not currently working
    bucket_creds = {
        "access_key_id": "",
        "additional_buckets": [],
        "bucket": "",
        "region": "",
        "secret_access_key": "" 
    }
    vcap_services = os.getenv("VCAP_SERVICES")
    bucket_creds = json.loads(vcap_services)
    connection = boto.s3.connect_to_region(
        bucket_creds["region"],
        aws_access_key_id=bucket_creds["access_key_id"],
        aws_secret_access_key=bucket_creds["secret_access_key"],
        is_secure=True
    )
    bucket = connection.get_bucket(bucket_creds["bucket"])
    key = Key(bucket=bucket, name=bucket_name)
    f = StringIO(csv_file_contents)
    try:
        key.send_file(f)
        return "success"
    except:
        return "failed"


def pushing_to_github(csv_file_contents):
    token = json.load(open("github_token.creds","r"))
    g = Github(token)
    #repo = g.get_user().get_repo('domain-scan-orchestration')
    org = [org for org in list(g.get_user().get_orgs()) if "18F" in org.url][0]
    repo = org.get_repo('domain-scan-orchestration')
    github_object = [InputGitTreeElement(
        'data/domain-list.csv', 
        '100644', 
        'blob', 
        csv_file_contents)
    ]
    commit_message = 'updating file'
    master_ref = repo.get_git_ref('heads/master')
    master_sha = master_ref.object.sha
    base_tree = repo.get_git_tree(master_sha)
    tree = repo.create_git_tree(github_object, base_tree)
    parent = repo.get_git_commit(master_sha)
    commit = repo.create_git_commit(commit_message, tree, [parent])
    master_ref.edit(commit.sha)


app = Flask(__name__)
redis_url = get_redis_url()
app.config.update(
    CELERY_BROKER_URL=redis_url,
    result_backend=redis_url
)


schedule = {
    "gatherer": {
        "task": "app.gatherer",
        "schedule": crontab(0, 0, day_of_week=2),
    },
}

db = SQLAlchemy(app)
port = os.getenv("PORT", "5000")
app.config["PORT"] = int(port)
app.config["HOST"] = "0.0.0.0"
app.config["beat_schedule"] = schedule
#app.config["imports"] = ("gatherer")
app.config["task_acks_late"] = False
ensure_upload_folder()
UPLOAD_FOLDER = "csv_upload"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://eric_s:1234@localhost/vc_db"

celery = make_celery(app)

@celery.task(name="app.save_csv_to_db")
def save_csv_to_db(contents):
    file = StringIO(contents)
    df = pd.read_csv(file)
    for index in df.index:
        # dt.datetime.now is bad, change this in the near future
        containment_set = Domains.query.filter(Domains.domain.contains(df.ix[index]["b'Domain"])).all()
        if len(containment_set) == 0:
            domain = Domains(df.ix[index]["b'Domain"], dt.datetime.now())
            db.session.add(domain)
            db.session.commit()

@celery.task(name="app.reset")
def reset():
    pushing_to_github("hello")

def parse_base_domain(domain):
	return ".".join(domain.split(".")[-2:])

@celery.task(name="app.gatherer")
def gatherer():
    """
    Grabs from dap, censys, eot2016, and parent domains of .gov
    """
    options = json.load(open("options.creds","r"))
    censys_list = censys_api.gather(".gov", options)
    censys_list = list(set(censys_list))
    censys_list = [elem for elem in censys_list if ".gov" in elem]

    eot2016 = requests.get("https://github.com/GSA/data/raw/gh-pages/end-of-term-archive-csv/eot-2016-seeds.csv")
    eot2016_string = eot2016.text
    eot2016_list = string_to_list(eot2016_string)

    dap = requests.get("https://analytics.usa.gov/data/live/sites-extended.csv")
    dap_string = dap.text
    dap_list = string_to_list(dap_string)
    dap_list = dap_list[1:]
    dap_list = string_to_list(dap_string)

    parents = requests.get("https://raw.githubusercontent.com/GSA/data/gh-pages/dotgov-domains/current-federal.csv")
    parents_string = parents.text
    parents_list = string_to_df_to_list(parents_string)

    master_data = {
        "eot2016":[],
        "dap":[],
        "Domain":[],
        "censys": [],
        "parents": [],
        "Base Domain": []

    }
    
    domain_list = [domain.domain for domain in Domains.query.all()]
    print("started for loop")
    for domain in domain_list:
        master_data["Domain"].append(domain)
        master_data["eot2016"].append(domain in eot2016_list)
        master_data["dap"].append(domain in dap_list)
        master_data["censys"].append(domain in censys_list)
        master_data["parents"].append(domain in parents)
        master_data["Base Domain"].append(parse_base_domain(domain))

    print("finished for loop")
    cols = ["Domain", "Base Domain", "censys", "dap", "eot2016", "parents"]
    df = pd.DataFrame(master_data)
    df = df[cols]
    s = StringIO()
    df.to_csv(s)
    csv_file_contents = s.getvalue()
    with open("domain-list.csv","w") as f:
    	f.write(csv_file_contents)
    print(csv_file_contents)
    pushing_to_github(csv_file_contents)
    #bucket_name = "dotgov_subdomains" 
    #bucket_name = "dotgov_shared_key"
    #upload_to_s3(csv_file_contents, bucket_name)
    return "success"



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
            contents = str(file.stream.read())
            contents = contents.replace("\\r","\r")
            contents = contents.replace("\\n","\n")
            save_csv_to_db.delay(contents)
            return render_template("index.html")
    return render_template("index.html")


@app.route("/gather", methods=["GET","POST"])
def gather():
    # fix this
    gatherer.delay()
    return "success"


@app.route("/reset", methods=["GET", "POST"])
def reset_csv():
    reset.delay()
    return "worked"


class Domains(db.Model):
    """
    This is where the list of current domains to scan is stored.
    We can see when this domain was added to the list
    
    Parameters:
    @domain - a domain to scan
    
    @timestamp - when the domain was added to the database
    """
    __tablename__ = "domains"
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String)
    timestamp = db.Column(db.DateTime)
    
    def __init__(self, domain, timestamp):
        self.domain = domain
        self.timestamp = timestamp


if __name__ == '__main__':
    app.run(debug=True)

