from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os
from celery import Celery
from celery.schedules import crontab
import cfenv
import datetime as dt
import pandas as pd
from io import StringIO
import requests
import json
import os
import boto
from boto.s3.key import Key
from flask import render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import censys_api
from github import Github
from github import InputGitTreeElement

env = cfenv.AppEnv()


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


def ensure_upload_folder():
    if not os.path.exists("csv_upload"):
        os.mkdir("csv_upload")


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
# the below line is for local development only
#app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://eric_s:1234@localhost/vc_db"
redis_url = get_redis_url()
app.config.update(
    CELERY_BROKER_URL=redis_url,
    result_backend=redis_url
)


db = SQLAlchemy(app)
port = os.getenv("PORT", "5000")
app.config["PORT"] = int(port)
app.config["HOST"] = "0.0.0.0"


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
        
    def __str__(self):
        return "< domain: {}>".format(repr(self.domain))


class USWDS(db.Model):
    """
    Information relating to scans for the us web design standards.
    There will be multiple entries for the same domain, the only certain difference
    will be the timestamp, which will be unique to each date a scan occurred.
    ## The following 4 lines are not related to documentation, but are good thoughts
    ## think about where to put this
    I think it will be interesting to see the results of scans over time.
    This way we can have a more informed security posture over time.
    Additionally, this allows us to monitor whether things are
    improving or getting worse.

    Parameters:
    @domain - the domain that was scanned
    
    @uswds - a boolean - 
    The result of a scan. 
    If True the web design standards are present on the homepage
    
    @https - a boolean - 
    The result of a scan. 
    If True the website's homepage responds to https requests
    
    @timestamp - a datetime object -
    When the scan took place
    """
    __tablename__ = 'uswds'
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String)
    uswds = db.Column(db.Boolean)
    https = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime)

    def __init__(self, domain, uswds, https, timestamp):
        self.domain = domain
        self.uswds = uswds
        self.https = https
        self.timestamp = timestamp

    def __str__(self):
        return "< domain: {}".format(repr(self.domain))

schedule = {
    "gatherer": {
        "task": "app.gatherer",
        "schedule": crontab(0, 0, day_of_week=2),
    },
    #"dummy": {
    #	"task": "app.dummy",
    #	"schedule": crontab(minute="*/1")
    #}
}

ensure_upload_folder()
UPLOAD_FOLDER = "csv_upload"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["beat_schedule"] = schedule
#app.config["imports"] = ("gatherer")
app.config["task_acks_late"] = False

celery = make_celery(app)


@celery.task(name="app.dummy")
def dummy():
    return "it worked!"


@celery.task(name="app.uswds")
def uswds():
    """
    Runs the us web design standards checker against the uploaded list of domains.
    """
    results = {}
    for domain in Domains.query.all():
        payload = {"domain":domain.domain}
        headers = {"Content-Type":"application/json"}
        result = requests.get(
            "https://domain-scan-python-services.app.cloud.gov/services/web-design-standards",
            params=payload,
        headers=headers)
        result = json.loads(result.text)
        uswds = USWDS(domain.domain, result["uswds"], result["https"], dt.datetime.now())
        db.session.add(uswds)
        db.session.commit()
        results[domain.domain] = result
    return results #maybe?


def string_to_list(string):
    return string.split("\n")


def string_to_df_to_list(string):
    data = StringIO(string)
    df = pd.read_csv(data, sep=",")
    return list(df["Domain Name"])


def upload_to_s3(csv_file_contents, bucket_name):
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
        "eot":[],
        "dap":[],
        "domains":[],
        "censys": []
    }
    print("started for loop")
    for domain in parents_list:
        master_data["domains"].append(domain)
        master_data["eot"].append(domain in eot2016_list)
        master_data["dap"].append(domain in dap_list)
        master_data["censys"].append(domain in censys_list)
    print("finished for loop")
    col = ["domains", ]
    df = pd.DataFrame(master_data)
    s = StringIO()
    df.to_csv(s)
    csv_file_contents = s.getvalue()
    with open("domain-list.csv","w") as f:
    	f.write(csv_file_contents)
    pushing_to_github(csv_file_contents)
    #bucket_name = "dotgov_subdomains" 
    #bucket_name = "dotgov_shared_key"
    #upload_to_s3(csv_file_contents, bucket_name)
    return s.getvalue()


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


@app.route("/dummy", methods=["GET","POST"])
def dum():
    dummy.delay()
    return "success"


if __name__ == '__main__':
    app.run(debug=True)

