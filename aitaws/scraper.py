from collections import Counter
from praw import Reddit
from praw.models import MoreComments

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

        # do not load zero-vote or low-vote posts
        if sum(counts.values()) > 50:
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

    # compute the tallies of yta, nta, esh, und, total

    # a post is considered YTA if its YTA votes are greater than the sum of its NTA and ESH votes
    # in other words, a post must have 50% or more YTA votes to be marked YTA
    # and likewise for every category
    yta_count = PostModel.query.filter(PostModel.yta >= (PostModel.nta + PostModel.esh)).count()
    nta_count = PostModel.query.filter(PostModel.nta >= (PostModel.yta + PostModel.esh)).count()
    esh_count = PostModel.query.filter(PostModel.esh >= (PostModel.yta + PostModel.nta)).count()

    total = PostModel.query.count()

    # undecided (und) posts are those without a clear majority winner
    und_count = total - yta_count - nta_count - esh_count

    # either update the existing cache record or create one
    cache = DataCacheModel.query.first()

    if cache is None:
        cache = DataCacheModel()
        db.session.add(cache)

    cache.yta_count = yta_count
    cache.nta_count = nta_count
    cache.esh_count = esh_count
    cache.und_count = und_count
    cache.total = total

    db.session.commit()
