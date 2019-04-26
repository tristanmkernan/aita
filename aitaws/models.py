from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class PostModel(db.Model):
    post_id = db.Column(db.String, primary_key=True)
    yta = db.Column(db.Integer, default=0)
    nta = db.Column(db.Integer, default=0)
    esh = db.Column(db.Integer, default=0)


def init_db(app):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
