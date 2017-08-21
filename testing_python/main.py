import requests

def my_handler(event, context):
    return {
        "message": requests.get(event["url"]).text
    }
