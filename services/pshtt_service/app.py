import pshtt
from flask import Flask, request
import json

app = Flask(__name__)


@app.route("services/pshtt", methods=["GET","POST"])
def pshtt():
    return "this is just a test"
    # data = json.loads(request.data)
    # options = data["options"]
    # domain = data["domain"]
    # return pshtt.scan(domain, options)
    
if __name__ == '__main__':
    app.run()
