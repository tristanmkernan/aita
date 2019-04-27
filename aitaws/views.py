from flask import render_template
from sqlalchemy import and_

from .models import PostModel
from .tasks import tasks


def init_views(app):
    @app.route('/')
    def index():
        yta = PostModel.query.filter(and_(PostModel.yta > PostModel.nta, PostModel.yta > PostModel.esh)).count()
        nta = PostModel.query.filter(and_(PostModel.nta > PostModel.yta, PostModel.nta > PostModel.esh)).count()
        esh = PostModel.query.filter(and_(PostModel.esh > PostModel.yta, PostModel.esh > PostModel.nta)).count()

        total = yta + nta + esh

        if total > 0:
            yta = int(100 * yta / total)
            nta = int(100 * nta / total)
            esh = int(100 * esh / total)

        return render_template('index.html', yta=yta, nta=nta, esh=esh)

    @app.route('/scrape')
    def scrape():
        if app.config['DEVELOPMENT']:
            tasks['scrape'].delay()
        return 'OK', 200

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
