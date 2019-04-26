from flask import Flask


def create_app():
    app = Flask(__name__)

    # load the instance config
    app.config.from_envvar("AITAWS_SETTINGS", silent=False)

    from .models import init_db
    init_db(app)

    from .views import init_views
    init_views(app)

    from .tasks import init_tasks
    init_tasks(app)

    from .cli import init_cli
    init_cli(app)

    return app
