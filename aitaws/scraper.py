from collections import Counter
from datetime import datetime
from praw import Reddit
from praw.models import MoreComments
from sqlalchemy import func

from .models import db, PostModel, DataCacheModel, TopPostCacheModel


# https://praw.readthedocs.io/en/latest/index.html
# https://praw.readthedocs.io/en/latest/tutorials/comments.html


def scrape(client_id, client_secret, user_agent, num_posts):
    reddit = Reddit(client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent)

    data = []

    for submission in reddit.subreddit('AmItheAsshole').hot(limit=num_posts):

        # ignore meta, update, etc. posts
        title = submission.title.lower()
        if not (title.startswith('aita') or title.startswith('wibta')):
            continue

        counts = Counter()

        for comment in submission.comments:
            if isinstance(comment, MoreComments):
                continue

            body = comment.body.lower()

            for judgment in ('yta', 'nta', 'esh'):
                if body.startswith(judgment):
                    counts[judgment] += comment.score

        # do not load zero-vote or low-vote posts
        if sum(counts.values()) > 50:
            data.append((submission.id, submission.title, submission.created, submission.score, counts))

    # persist the data:
    # update record if it exists, otherwise create it
    for post_id, title, created, score, counts in data:
        post = PostModel.query.filter_by(post_id=post_id).first()

        if post is None:
            post = PostModel(post_id=post_id)
            db.session.add(post)

        post.title = title
        post.created = datetime.fromtimestamp(created)
        post.score = score
        post.yta = counts['yta']
        post.nta = counts['nta']
        post.esh = counts['esh']

    db.session.commit()

    # compute the tallies of yta, nta, esh, und, total

    # a post is considered YTA if its YTA votes are greater than the sum of its NTA and ESH votes
    # in other words, a post must have 50% or more YTA votes to be marked YTA
    # and likewise for every category
    yta_query = PostModel.query.filter(PostModel.yta > 0.67 * (PostModel.yta + PostModel.nta + PostModel.esh))
    nta_query = PostModel.query.filter(PostModel.nta > 0.67 * (PostModel.yta + PostModel.nta + PostModel.esh))
    esh_query = PostModel.query.filter(PostModel.esh > 0.67 * (PostModel.yta + PostModel.nta + PostModel.esh))

    yta_count = yta_query.count()
    nta_count = nta_query.count()
    esh_count = esh_query.count()

    total = PostModel.query.count()

    # undecided (und) posts are those without a clear majority winner
    und_count = total - yta_count - nta_count - esh_count

    # calculate the weighted scores

    yta_count_weighted = yta_query \
        .with_entities(func.sum(PostModel.yta).label('count_weighted')) \
        .first() \
        .count_weighted

    nta_count_weighted = nta_query \
        .with_entities(func.sum(PostModel.nta).label('count_weighted')) \
        .first() \
        .count_weighted

    esh_count_weighted = esh_query \
        .with_entities(func.sum(PostModel.esh).label('count_weighted')) \
        .first() \
        .count_weighted

    total_weighted = PostModel.query \
        .with_entities(func.sum(PostModel.nta + PostModel.yta + PostModel.esh).label('count_weighted')) \
        .first() \
        .count_weighted

    und_count_weighted = total_weighted - (yta_count_weighted + nta_count_weighted + esh_count_weighted)

    # update or create the existing counts cache record
    cache = DataCacheModel.query.first()

    if cache is None:
        cache = DataCacheModel()
        db.session.add(cache)

    cache.yta_count = yta_count
    cache.nta_count = nta_count
    cache.esh_count = esh_count
    cache.und_count = und_count
    cache.total = total

    cache.yta_count_weighted = yta_count_weighted
    cache.nta_count_weighted = nta_count_weighted
    cache.esh_count_weighted = esh_count_weighted
    cache.und_count_weighted = und_count_weighted
    cache.total_weighted = total_weighted

    db.session.commit()

    # update the top posts: delete all current top posts, then insert new ones
    TopPostCacheModel.query.delete()
    db.session.commit()

    yta_top = yta_query.order_by(PostModel.yta.desc()).limit(10).all()
    nta_top = nta_query.order_by(PostModel.nta.desc()).limit(10).all()
    esh_top = esh_query.order_by(PostModel.esh.desc()).limit(10).all()

    for post in yta_top:
        db.session.add(TopPostCacheModel(post=post, category='yta'))

    for post in nta_top:
        db.session.add(TopPostCacheModel(post=post, category='nta'))

    for post in esh_top:
        db.session.add(TopPostCacheModel(post=post, category='esh'))

    db.session.commit()
