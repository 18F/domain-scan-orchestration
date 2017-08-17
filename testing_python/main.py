def my_handler(event, context):
    return {
        "message": event["hostname"]
    }
