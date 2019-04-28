from flask import render_template
from sqlalchemy import and_

from .models import PostModel
from .tasks import tasks


def init_views(app):
    @app.route('/')
    def index():
        yta_count = PostModel.query.filter(and_(PostModel.yta > PostModel.nta, PostModel.yta > PostModel.esh)).count()
        nta_count = PostModel.query.filter(and_(PostModel.nta > PostModel.yta, PostModel.nta > PostModel.esh)).count()
        esh_count = PostModel.query.filter(and_(PostModel.esh > PostModel.yta, PostModel.esh > PostModel.nta)).count()

        total = yta_count + nta_count + esh_count

        yta_percent = 0
        nta_percent = 0
        esh_percent = 0

        if total > 0:
            yta_percent = int(100 * yta_count / total)
            nta_percent = int(100 * nta_count / total)
            esh_percent = int(100 * esh_count / total)

        data = {
            'yta': {
                'percent': yta_percent,
                'count': yta_count
            },
            'nta': {
                'percent': nta_percent,
                'count': nta_count
            },
            'esh': {
                'percent': esh_percent,
                'count': esh_count
            },
            'total': total
        }

        return render_template('index.html', devmode=app.config['DEVELOPMENT'], **data)

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
