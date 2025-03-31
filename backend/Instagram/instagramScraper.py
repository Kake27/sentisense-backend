from instaloader import Instaloader, Post
import time
import random
import os
from dotenv import load_dotenv

load_dotenv()

FILENAME = os.getenv("INSTAGRAM_COOKIE_FILE_1")

class Instgram:
    def __init__(self):
        self.L = Instaloader()
        self.L.load_session_from_file(FILENAME)
        print("login success")
    
    def get_comments(self, url):
        shortcode = url.split("/p/")[-1].split("/")[0]
        post = Post.from_shortcode(self.L.context, shortcode)

        comments = post.get_comments()
        comment_count = post.comments
        print(f"Found {comment_count} comments")

        all_comments = []

        for comment in comments:
            # print(comment.text)
            all_comments.append(comment.text.replace(",",""))

            print(f"got {len(all_comments)} comments so far...")

            if((len(all_comments))%15 == 0):
                print(f"Sleeping for some time...") 
                time.sleep(random.uniform(7, 15))

            wait_time = random.uniform(0.5,2)
            print(f"Waiting for {wait_time} seconds...")
            time.sleep(wait_time)

        print(f"got {len(all_comments)} comments")
        return all_comments


url = "https://www.instagram.com/p/DFtT1dQTRvL/"

if __name__ == "__main__":
    instagram = Instgram()
    comments = instagram.get_comments(url=url)
    for comment in comments:
        print(comment)



