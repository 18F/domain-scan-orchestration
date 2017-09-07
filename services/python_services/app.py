from flask import Flask, request
import json
from web_design_standards_check import uswds_checker
from smart_open import smart_open
import boto
from app import env
import StringIO
import io


app = Flask(__name__)


@app.route("/", methods=["GET","POST"])
def index():
    return "whatever"


@app.route("/services/web-design-standards", methods=["GET", "POST"])
def services():
    domain = request.args.get("domain")
    return json.dumps(uswds_checker(domain))


@app.route("/services/pshtt", methods=["GET","POST"])
def pshtt():
    result = subprocess.run(["pshtt_command", "whitehouse.gov"], stdout=subprocess.PIPE)
    return result.stdout.decode("utf-8")

@app.route("/services/command_test", methods=["GET","POST"])
def command_test():
    result = subprocess.run(["test_command"], stdout=subprocess.PIPE)
    return result.stdout


def get_s3_key(name):
    connection = boto.s3.connect_to_region(
        env.get_credential('region'),
        aws_access_key_id=env.get_credential('access_key_id'),
        aws_secret_access_key=env.get_credential('secret_access_key'),
    )
    bucket = connection.get_bucket(env.get_credential('bucket'))
    key = Key(bucket=bucket, name=name)
    return key

def make_bundle(resource):
    s3_key = get_s3_key(resource['name'])
    with smart_open(s3_key, "wb") as fp:
        query = query_with_labels(
            resource['query'],
            resource['schema']
        )
        copy_to(
            query,
            fp,
            db.session.connection().engine,
            format='csv',
            header=True
        )

# assume data is a dataframe
def to_s3(data):
    s = StringIO.StringIO()
    data.to_csv(s)
    resultant_csv = s.getvalue()
    connection = boto.s3.connect_to_region(
        env.get_credential('region'),
        aws_access_key_id=env.get_credential('access_key_id'),
        aws_secret_access_key=env.get_credential('secret_access_key'),
    )
    bucket = connection.get_bucket(env.get_credential('bucket'))
    key = boto.s3.key.Key(bucket, 'all-domains.csv')
    f = io.StringIO(resultant_csv)
    key.send_file(f)

    
@app.route("/services/gather", methods=["GET","POST"])
def gather():
    key = get_s3_key("dotgov_subdomains")
    return "pass"


if __name__ == '__main__':
    app.run()
