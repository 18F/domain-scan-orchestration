from flask import Flask
import os
from celery import Celery
from celery.schedules import crontab
import cfenv
import pandas as pd
from io import StringIO
import requests
import json
import boto
from boto.s3.key import Key
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
    #"dummy": {
    #	"task": "app.dummy",
    #	"schedule": crontab(minute="*/1")
    #}
}


port = os.getenv("PORT", "5000")
app.config["PORT"] = int(port)
app.config["HOST"] = "0.0.0.0"
app.config["beat_schedule"] = schedule
#app.config["imports"] = ("gatherer")
app.config["task_acks_late"] = False

celery = make_celery(app)


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
    repo = g.get_user().get_repo('domain-scan-orchestration')
    #org = [org for org in list(g.get_user().get_orgs()) if "18F" in org.url][0]
    #repo = org.get_repo('domain-scan-orchestration')
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


@app.route("/", methods=["GET","POST"])
def index():
    return "it worked!"


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

