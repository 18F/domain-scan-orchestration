from flask import Flask, request
import json
import subprocess
from web_design_standards_check import uswds_checker

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
    result = subprocess.run(["pshtt", "whitehouse.gov"], stdout=subprocess.PIPE)
    return result.stdout

@app.route("/services/command_test", methods=["GET","POST"])
def command_test():
    result = subprocess.run(["test_command"], stdout=subprocess.PIPE)
    return result.stdout

if __name__ == '__main__':
    app.run()
