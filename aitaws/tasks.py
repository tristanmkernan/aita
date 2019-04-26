from celery import Celery

from . import create_app
from .scraper import scrape


# http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html
# http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html
# http://flask.pocoo.org/docs/1.0/patterns/celery/

def init_tasks(app=None):
    app = app or create_app()

    stalk = Celery(app.import_name,
                   broker=app.config['CELERY_BROKER_URL'])

    stalk.conf.update(app.config)

    class ContextTask(stalk.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    stalk.Task = ContextTask

    @stalk.task
    def my_scraper():
        return scrape(app.config['PRAW_CLIENT_ID'],
                      app.config['PRAW_CLIENT_SECRET'],
                      app.config['PRAW_USER_AGENT'])

    stalk.conf.beat_schedule = {
        'scraper': {
            'task': 'aitaws.tasks.my_scraper',
            'schedule': 60.0 * 60.0
        }
    }

    return stalk
