from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os
from celery import Celery
from .env import env
from celery.schedules import crontab
import cfenv

def make_celery(app):
    celery = Celery(app.name, backend=app.config['result_backend'],
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

env = cfenv.AppEnv()
db = SQLAlchemy(app)
port = os.getenv("PORT", "5000")
app.config["PORT"] = int(port)
app.config["HOST"] = "0.0.0.0"

schedule = {
    "uswds": {
        # structure: file.function
        "task": "tasks.uswds",
        "schedule": crontab(day_of_week=2),
    }
}

ensure_upload_folder()
UPLOAD_FOLDER = "csv_upload"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["beat_schedule"] = schedule
app.config["imports"] = ("tasks.uswds")
app.config["task_acks_late"] = False

celery_obj = make_celery(app)

from app import views, models
