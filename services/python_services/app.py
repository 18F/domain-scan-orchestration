#import pshtt
from flask import Flask, request
import json
import subprocess

app = Flask(__name__)


def scan(command, env=None, allowed_return_codes=[]):
    try:
        response = subprocess.check_output(command, shell=False, env=env)
        return str(response, encoding='UTF-8')
    except subprocess.CalledProcessError as exc:
        if exc.returncode in allowed_return_codes:
            return str(exc.stdout, encoding='UTF-8')
        else:
            logging.warn("Error running %s." % (str(command)))
            return None


@app.route("/", methods=["GET","POST"])
def index():
    return "whatever"


@app.route("/services", methods=["GET", "POST"])
def services():
    domain = request.args.get("domain")
    return domain

@app.route("/services/pshtt", methods=["GET","POST"])
def pshtt():
    domain = request.args.get("domain")
    timeout=30
    user_agent = "github.com/18f/domain-scan-orchestration, pshtt.py"
    # we don't need a preload cache, because we are switching to database
    raw = scan([
            "pshtt",
            domain,
            '--json',
            '--user-agent', '\"%s\"' % user_agent,
            '--timeout', str(timeout)
        ])
    return raw
    # data = json.loads(request.data)
    # options = data["options"]
    # domain = data["domain"]
    # return pshtt.scan(domain, options)
    
if __name__ == '__main__':
    app.run()
