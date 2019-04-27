from collections import Counter
from praw import Reddit
from praw.models import MoreComments

from .models import db, PostModel


# https://praw.readthedocs.io/en/latest/index.html
# https://praw.readthedocs.io/en/latest/tutorials/comments.html


def scrape(client_id, client_secret, user_agent):
    reddit = Reddit(client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent)

    data = []

    for submission in reddit.subreddit('AmItheAsshole').hot(limit=50):
        counts = Counter()

        for comment in submission.comments:
            if isinstance(comment, MoreComments):
                continue

            body = comment.body.lower()

            for judgment in ('yta', 'nta', 'esh'):
                if body.startswith(judgment):
                    counts[judgment] += 1

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
