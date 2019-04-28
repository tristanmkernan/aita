from flask import render_template

from .models import DataCacheModel
from .tasks import tasks


def init_views(app):
    @app.route('/')
    def index():
        cache = DataCacheModel.query.first()

        yta_count = cache.yta_count
        nta_count = cache.nta_count
        esh_count = cache.esh_count

        total = cache.total

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
