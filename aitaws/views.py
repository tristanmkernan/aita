from flask import render_template
from operator import attrgetter

from .models import DataCacheModel, TopPostCacheModel
from .tasks import tasks


def init_views(app):
    @app.route('/')
    def index():
        cache = DataCacheModel.query.first()

        yta_percent = round(100 * cache.yta_count / cache.total, 2)
        nta_percent = round(100 * cache.nta_count / cache.total, 2)
        esh_percent = round(100 * cache.esh_count / cache.total, 2)
        und_percent = round(100 * cache.und_count / cache.total, 2)

        yta_percent_weighted = round(100 * cache.yta_count_weighted / cache.total_weighted, 2)
        nta_percent_weighted = round(100 * cache.nta_count_weighted / cache.total_weighted, 2)
        esh_percent_weighted = round(100 * cache.esh_count_weighted / cache.total_weighted, 2)
        und_percent_weighted = round(100 * cache.und_count_weighted / cache.total_weighted, 2)

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
                'base': {
                    'percent': yta_percent,
                    'count': cache.yta_count,
                },
                'weighted': {
                    'percent': yta_percent_weighted,
                    'count': cache.yta_count_weighted
                },
                'top': top_yta_posts
            },
            'nta': {
                'base': {
                    'percent': nta_percent,
                    'count': cache.nta_count,
                },
                'weighted': {
                    'percent': nta_percent_weighted,
                    'count': cache.nta_count_weighted
                },
                'top': top_nta_posts
            },
            'esh': {
                'base': {
                    'percent': esh_percent,
                    'count': cache.esh_count,
                },
                'weighted': {
                    'percent': esh_percent_weighted,
                    'count': cache.esh_count_weighted
                },
                'top': top_esh_posts
            },
            'und': {
                'base': {
                    'percent': und_percent,
                    'count': cache.und_count,
                },
                'weighted': {
                    'percent': und_percent_weighted,
                    'count': cache.und_count_weighted
                },
            },
            'total': {
                'base': cache.total,
                'weighted': cache.total_weighted
            }
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
