from flask import Flask


def create_app():
    app = Flask(__name__)

    # load the instance config
    # app.config.from_envvar("AITAWS_SETTINGS", silent=False)

    # from .models import init_app as init_models

    # init_models(app)

    from .views import init_views
    init_views(app)

    return app
