from flask import render_template
from operator import attrgetter

from .models import DataCacheModel, TopPostCacheModel
from .tasks import tasks


def init_views(app):
    @app.route('/')
    def index():
        cache = DataCacheModel.query.first()

        yta_count = cache.yta_count
        nta_count = cache.nta_count
        esh_count = cache.esh_count
        und_count = cache.und_count

        total = cache.total

        yta_percent = 0
        nta_percent = 0
        esh_percent = 0
        und_percent = 0

        if total > 0:
            yta_percent = round(100 * yta_count / total, 2)
            nta_percent = round(100 * nta_count / total, 2)
            esh_percent = round(100 * esh_count / total, 2)
            und_percent = round(100 * und_count / total, 2)

        top_posts = TopPostCacheModel.query.all()

        top_yta_posts = filter(lambda p: p.category == 'yta', top_posts)
        top_yta_posts = map(attrgetter('post'), top_yta_posts)
        top_yta_posts = sorted(top_yta_posts, key=attrgetter('yta'), reverse=True)

        top_nta_posts = filter(lambda p: p.category == 'nta', top_posts)
        top_nta_posts = map(attrgetter('post'), top_nta_posts)
        top_nta_posts = sorted(top_nta_posts, key=attrgetter('nta'), reverse=True)

        top_esh_posts = filter(lambda p: p.category == 'esh', top_posts)
        top_esh_posts = map(attrgetter('post'), top_esh_posts)
        top_esh_posts = sorted(top_esh_posts, key=attrgetter('esh'), reverse=True)

        data = {
            'yta': {
                'percent': yta_percent,
                'count': yta_count,
                'top': top_yta_posts
            },
            'nta': {
                'percent': nta_percent,
                'count': nta_count,
                'top': top_nta_posts
            },
            'esh': {
                'percent': esh_percent,
                'count': esh_count,
                'top': top_esh_posts
            },
            'und': {
                'percent': und_percent,
                'count': und_count
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
