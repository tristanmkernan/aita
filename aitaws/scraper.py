from collections import Counter
from praw import Reddit
from praw.models import MoreComments
from sqlalchemy import and_

from .models import db, PostModel, DataCacheModel


# https://praw.readthedocs.io/en/latest/index.html
# https://praw.readthedocs.io/en/latest/tutorials/comments.html


def scrape(client_id, client_secret, user_agent, num_posts):
    reddit = Reddit(client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent)

    data = []

    for submission in reddit.subreddit('AmItheAsshole').hot(limit=num_posts):
        counts = Counter()

        for comment in submission.comments:
            if isinstance(comment, MoreComments):
                continue

            body = comment.body.lower()

            for judgment in ('yta', 'nta', 'esh'):
                if body.startswith(judgment):
                    counts[judgment] += comment.score

        # do not load zero-vote posts
        if sum(counts.values()) > 0:
            data.append((submission.id, counts))

    # persist the data:
    # update record if it exists, otherwise create it
    for post_id, counts in data:
        post = PostModel.query.filter_by(post_id=post_id).first()

        if post is None:
            post = PostModel(post_id=post_id)
            db.session.add(post)

        post.yta = counts['yta']
        post.nta = counts['nta']
        post.esh = counts['esh']

    db.session.commit()

    # compute the tallies of yta, nta, esh as percentages of total and cache in db

    yta_count = PostModel.query.filter(and_(PostModel.yta > PostModel.nta, PostModel.yta > PostModel.esh)).count()
    nta_count = PostModel.query.filter(and_(PostModel.nta > PostModel.yta, PostModel.nta > PostModel.esh)).count()
    esh_count = PostModel.query.filter(and_(PostModel.esh > PostModel.yta, PostModel.esh > PostModel.nta)).count()

    total = yta_count + nta_count + esh_count

    # either update the existing cache record or create one
    cache = DataCacheModel.query.first()

    if cache is None:
        cache = DataCacheModel()
        db.session.add(cache)

    cache.yta_count = yta_count
    cache.nta_count = nta_count
    cache.esh_count = esh_count
    cache.total = total

    db.session.commit()
