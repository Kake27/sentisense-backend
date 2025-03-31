import praw
import os
import time
from random import randint
from dotenv import load_dotenv

load_dotenv()

class Reddit:
    def __init__(self):
        client_id=os.getenv("CLIENT_ID_REDDIT")
        client_secret=os.getenv("CLIENT_SECRET_REDDIT")
        username=os.getenv("USERNAME_REDDIT")
        password=os.getenv("PASSWORD_REDDIT")
        print(client_id)

        self.reddit = praw.Reddit(
            user_agent = True,
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password
        )

    def get_comments(self, url):
        post = self.reddit.submission(url=url)
        comments = post.comments
        comments.replace_more(limit=None)

        total_comments = comments.list()
        all_comments = []

        for comment in total_comments:
            all_comments.append(comment.body.replace(",", ""))

            if len(all_comments) % 10 == 0:
                print(f"Obtained {len(all_comments)} comments so far.")

            if len(all_comments) % 50 == 0:
                time.sleep(randint(2, 5))

        return all_comments


if __name__ == "__main__":
    url = "https://www.reddit.com/r/Btechtards/comments/1j01odr/gen_z_men_are_just_as_fucked_up_as_the_older_men/"
    reddit = Reddit()
    comments = reddit.get_comments(url=url)
    for comment in comments:
        print(comment)


