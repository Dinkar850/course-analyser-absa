import re
import requests
from datetime import datetime
from db_client import insert_review
from config import YOUTUBE_API_KEY


def extract_video_id(url: str):
    """Extracts videoId from a YouTube URL."""
    match = re.search(r"(?:v=|youtu\.be/|embed/)([^&?/]+)", url)
    return match.group(1) if match else None


def fetch_top_comments(video_url: str, api_key: str, max_results: int = 50):
    """Fetches top (most relevant) YouTube comments as plain text strings."""
    video_id = extract_video_id(video_url)
    if not video_id:
        raise ValueError("Invalid YouTube URL provided.")

    url = "https://www.googleapis.com/youtube/v3/commentThreads"
    params = {
        "part": "snippet",
        "videoId": video_id,
        "maxResults": max_results,
        "order": "relevance",      # 'relevance' = top comments
        "textFormat": "plainText",
        "key": api_key
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch comments: {response.text}")

    data = response.json()
    comments = [
        item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        for item in data.get("items", [])
    ]
    return comments, video_id


def fetch_and_store_comments(video_url: str, max_results: int = 50):
    """
    Fetches YouTube comments and stores them in MongoDB using videoId as course_id.
    """
    comments, video_id = fetch_top_comments(video_url, YOUTUBE_API_KEY, max_results)

    print(f"Fetched {len(comments)} comments for video {video_id}, inserting into DB...")
    for text in comments:
        doc = {
            "source": "youtube",
            "course_id": video_id,  # using the videoId as course_id
            "text": text,
            "created_at": datetime.utcnow()
        }
        insert_review("reviews", doc)

    print(f"Inserted {len(comments)} comments for video {video_id}.")
    return video_id, len(comments)


if __name__ == "__main__":
    test_url = "https://youtu.be/qwAFL1597eM?si=f6X1qAQw3t_caEjT"
    video_id, count = fetch_and_store_comments(test_url, max_results=50)
    print(f"Done: {count} comments inserted for video {video_id}")
