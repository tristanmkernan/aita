from collections import Counter

from praw import Reddit
from praw.models import MoreComments


# https://praw.readthedocs.io/en/latest/index.html
# https://praw.readthedocs.io/en/latest/tutorials/comments.html


def scrape(client_id, client_secret, user_agent):
    reddit = Reddit(client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent)

    data = []

    for submission in reddit.subreddit('AmItheAsshole').hot(limit=5):
        counts = Counter()

        for comment in submission.comments:
            if isinstance(comment, MoreComments):
                continue

            body = comment.body.lower()

            for judgment in ('yta', 'nta', 'esh'):
                if body.startswith(judgment):
                    counts[judgment] += 1

        data.append({'post_id': submission.id, **counts})

    # TODO upsert the data
    print(data)
