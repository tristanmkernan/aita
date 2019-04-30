from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class PostModel(db.Model):
    post_id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String)
    created = db.Column(db.DateTime)
    yta = db.Column(db.Integer, default=0)
    nta = db.Column(db.Integer, default=0)
    esh = db.Column(db.Integer, default=0)
    score = db.Column(db.Integer, default=0)


class ScrapeLogModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)


class DataCacheModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    yta_count = db.Column(db.Integer, default=0)
    nta_count = db.Column(db.Integer, default=0)
    esh_count = db.Column(db.Integer, default=0)
    und_count = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, default=0)


class TopPostCacheModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey(PostModel.post_id))
    post = db.relationship(PostModel, uselist=False)
    category = db.Column(db.String)


def init_db(app):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
