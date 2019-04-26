from flask.cli import with_appcontext

import click


def init_cli(app):
    app.cli.add_command(create_db, 'create_db')


@click.command()
@with_appcontext
def create_db():
    """
    Creates the database
    """
    from .models import db

    db.create_all()

    print('Created database')
