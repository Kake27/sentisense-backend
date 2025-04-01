from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

from backend.Instagram.instagramScraper import Instagram
from backend.Reddit.redditScraper import Reddit
from backend.Youtube.youtubeScraper import Youtube

from backend.clustering.clustering import Clustering
from backend.GeminiIntegration.genai import Genai
from backend.testing import SentimentAnalysis
import pandas as pd
from dotenv import load_dotenv
import os
import json

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

load_dotenv()



status = {"processing": False, "comments_found": False, "file_created": False, "error": False}
prev_url = ""


def analyse(url):
    global status
    global prev_url

    prev_url = url
    status["processing"] = True

    if(os.path.exists("comments.csv")):
        os.remove("comments.csv")
        status["file_created"] = False

    try: 
        comments = []
        if "x.com" in url:
            print("Not supported")
            # scraper = Twitter()
            # id = url.split("/")[-1]
            # comments = asyncio.run(scraper.get_tweet(id=id, min_comments=200))
        elif "reddit.com" in url:
            scraper = Reddit()
            comments = scraper.get_comments(url=url)
        elif "instagram.com" in url:
            scraper = Instagram()
            comments = scraper.get_comments(url=url)
        elif "youtube.com" in url:
            scraper = Youtube()
            comments = scraper.get_comments(video_url=url)
        else:
            print("Invalid URL")
            status["error"] = "Invalid URL"
            return
        
        status["comments_found"] = True
        print("comments found")

        sentiments = []

        analyser = SentimentAnalysis()
        print("sentiment model loaded")

        for comment in comments:
            sentiment = analyser.predict_class([comment])
            sentiments.append([comment, sentiment])

        df = pd.DataFrame(sentiments, columns=["Comment", "Sentiment"])
        df.to_csv("comments.csv", index=False)

        print("Sentiment Analysis Completed.")
        status["file_created"] = True

    except Exception as e:
        print("An error occurred: " + str(e))
        status["error"] = True
        
    status["processing"] = False




@app.get("/")
async def root():
    return {"message": "server running"}

@app.get("/status")
async def get_status():
    global status
    return status


@app.get("/analyse")
async def get_analysis(url: str, background_tasks: BackgroundTasks):
    global status
    if status["processing"]:
        return {"message": "Process is already running"}
    elif url == prev_url and os.path.exists("comments.csv"):
        return {"file_created": True}
    
    background_tasks.add_task(analyse, url)
    return {"message": "Analysis Started"}


@app.get("/getcsv")
async def get_file():
    if os.path.exists("comments.csv"):
        return FileResponse("comments.csv", filename="output.csv", media_type="text/csv")
    return {"error": "file not found"}


@app.get("/graphs")
async def get_graph_data():
    if(os.path.exists("comments.csv")):
        df  = pd.read_csv("comments.csv")
        sentiment_count = df["Sentiment"].value_counts().to_dict()
        return sentiment_count
    return {"error": "file not found"}


@app.get("/clustering")
async def get_cluster():
    if(os.path.exists("comments.csv")):
        df = pd.read_csv("comments.csv")
        clustering = Clustering()
        return {"message": "testing clusters"}
        
        # clusters = clustering.create_cluster(df)
        
        return clusters
    
    return {"error": "File not found"}


@app.get("/solutions")
async def get_solutions():
    try:
        solution_data = ""
        if(os.path.exists("comments.csv")):
            df = pd.read_csv("comments.csv")
            clustering = Clustering()
            solution_data = clustering.create_cluster(df)

        data = json.loads(solution_data)
        formatted_output = ""

        for sentiment, clusters in data.items():
            formatted_output += f"\nSentiment: {sentiment.lower()}\n"
            for cluster, comments in clusters.items():
                formatted_output += f"Cluster {cluster}: {comments}\n"

        # print(formatted_output)

        genai = Genai()
        solutions = genai.get_solutions(
            prompt=
            """
             Analyze the following clusters of product reviews categorized by sentiment (neutral, negative, positive).

            For each sentiment (neutral, negative, positive), provide bullet points (maximum 10 words for each bullet) for:
            1. How to improve neutral sentiments.
            2. How to minimize negative sentiments.
            3. How to enhance positive sentiments.

            Data: """ + formatted_output + 
            """
            Return: Provide only the bullet points for improving neutral reviews, minimizing negative reviews, and enhancing positive reviews. 
            Always give the output in the format given here:
            {
                "Neutral": [
                    "Prompt engagement with questions about the content.",
                    "Add visually stimulating elements to capture attention.",
                    "Relate content to broader, interesting stories/movies.",
                    "Provide more facts/interesting info to increase engagement."
                ],
                "Negative": [
                    "Clearly explain the logic of events portrayed.",
                    "Be realistic about chances for promotion participation.",
                    "Ensure content is high quality and enjoyable.",
                    "Avoid plot holes or confusing aspects in content."
                ],
                "Positive": [
                    "Continue high animation/modeling quality.",
                    "Show the process in behind-the-scenes videos.",
                    "Expand the breadth of knowledge shared in videos.",
                    "Encourage viewers to express feelings."
                ]
            }
            """
        )
        print(solutions)
        return solutions
    except Exception as e:
        print("Error occurred while fetching solutions: "+ str(e))
        return {"error":e}






    

