# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from db_client import insert_review, get_reviews, close_db, clear_reviews_on_exit
from analyzer import ABSAService
from datetime import datetime
from aspect_merge import merge_aspects
from aggregator import aggregate_aspect_scores
from youtube_transcript_api import YouTubeTranscriptApi
from collector import fetch_and_store_comments
from config import MAX_COMMENTS
from review_synthesizer import synthesize_review

import re
import atexit

app = Flask(__name__)
CORS(app)

absa = ABSAService()


# responsible for collecting youtube reviews and inserting into database
@app.route("/collect/youtube", methods=["POST"])
def collect_youtube_comments():

    data = request.json or {}
    url = data.get("url")
    max_results = int(data.get("max_results", MAX_COMMENTS))

    if not url:
        return jsonify({"error": "YouTube URL is required"}), 400

    try:
        video_id, count = fetch_and_store_comments(url, max_results=max_results)

        return jsonify({
            "status": "ok",
            "message": f"Fetched and stored {count} comments.",
            "video_id": video_id,
            "count": count
        }), 200

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"error": str(e)}), 500


# responsible for running analysis and returning generated data to frontend as a response
@app.route("/course/<course_id>/analysis", methods=["GET"])
def course_analysis(course_id):
    print(">>> course_id received:", course_id)
    reviews = get_reviews("reviews", {"course_id": course_id}, limit=100)
    print(">>> reviews fetched:", len(reviews))
    if reviews:
        print(">>> sample review:", reviews[0])
    else:
        print(">>> NO reviews found")

    raw_texts = [r.get("text") for r in reviews]
    if not reviews:
        print(">>> NO reviews found")
        return jsonify({
            "course_id": course_id,
            "raw_count": 0,
            "detailed": [],
            "aspect_list": []
        }), 200
    
    batched_results = absa.analyze_batch(raw_texts)

    # Destructure (flatten) the nested lists
    all_analysis = []
    for batch in batched_results:
        all_analysis.extend(batch)

    print(f">>> Flattened {len(all_analysis)} total aspect entries")

    # Merge same aspects across reviews
    aspect_list = merge_aspects(all_analysis)

    # Get categorised review
    review_object = synthesize_review(aspect_list)

    # Calculate all aggregates
    aggregate_object = aggregate_aspect_scores(all_analysis)

    # Respond cleanly
    return jsonify({
        "course_id": course_id,
        "raw_count": len(raw_texts),
        "aggregate": {
            "aggregate_score": aggregate_object.get("aggregate_score", 0.0),
            "scaled_score": aggregate_object.get("scaled_score", 0.0),
            "adjusted_score": aggregate_object.get("adjusted_score", 0.0),
            "overall_sentiment": aggregate_object.get("overall_sentiment", "neutral"),
        },
        "review": {
            "summary": review_object.get("summary", "No summary generated."),
            "categories": review_object.get("categories", {}),
        },
        "aspect_list": aspect_list,
    }), 200


if __name__ == "__main__":
    atexit.register(clear_reviews_on_exit)
    try:
        app.run(debug=True, use_reloader=False, host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped manually.")
    finally:
        close_db()