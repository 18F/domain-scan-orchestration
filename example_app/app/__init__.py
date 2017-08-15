from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os
from celery import Celery
from .env import env


def make_celery(app):
    celery = Celery(app.name, backend=app.config['CELERY_RESULT_BACKEND'],
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
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
redis_url = get_redis_url()
app.config.update(
    CELERY_BROKER_URL=redis_url,
    CELERY_RESULT_BACKEND=redis_url
)

db = SQLAlchemy(app)
port = os.getenv("PORT", "5000")
app.config["PORT"] = int(port)
app.config["HOST"] = "0.0.0.0"

celery = make_celery(app)

from app import views, models
