import subprocess
import json
import os


class Youtube:
    def __init__(self):
        pass

    def get_comments(self, video_url):
        subprocess.run([
            "yt-dlp",
            "--write-comments",
            "--skip-download",
            "-o", "%(id)s",
            video_url
        ])

        video_id = video_url.split("v=")[-1]
        json_filename = f"{video_id}.info.json"

        if os.path.exists(json_filename):
            with open(json_filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "comments" in data:
                comments = []
                for comment in data["comments"]:
                    comments.append(comment["text"].replace(",",""))

                
                os.remove(json_filename)
                return comments

            else:
                print("No comments found.")
                return None

        else:
            print("JSON file not found. yt-dlp might not have extracted comments.")


if __name__ == "__main__":
    youtube = Youtube()
    video_url = "https://www.youtube.com/watch?v=HV82kA8AH0Q"
    commets = youtube.get_comments(video_url)