import math
from collections import defaultdict

def aggregate_aspect_scores(analyzed_items):
    """
    Weighted aggregate sentiment that accounts for both confidence
    and number of comments (trust grows with sqrt of comment count).
    """
    if not analyzed_items:
        return {
            "aggregate_score": 0.0,
            "scaled_score": 0.0,
            "adjusted_score": 0.0,
            "overall_sentiment": "neutral",
            "total_comments": 0
        }

    total_score = 0.0
    count = 0

    for it in analyzed_items:
        sentiment = it.get('sentiment', '').lower()
        confidence = float(it.get('confidence', 0.0))

        if 'pos' in sentiment:
            total_score += confidence
            count += 1
        elif 'neg' in sentiment:
            total_score -= confidence
            count += 1
        elif 'neu' in sentiment:
            count += 1

    if count == 0:
        return {
            "aggregate_score": 0.0,
            "scaled_score": 0.0,
            "adjusted_score": 0.0,
            "overall_sentiment": "neutral",
            "total_comments": 0
        }

    # Normalize to [-1, 1]
    aggregate_score = total_score / count

    # Scale to [0, 10]
    scaled_score = ((aggregate_score + 1) / 2) * 10
    scaled_score = round(scaled_score, 2)

    # Damping based on number of comments
    damping_factor = min(1.0, math.sqrt(count) / 10)
    adjusted_score = round(scaled_score * damping_factor, 2)

    # Overall label
    if aggregate_score > 0.2:
        overall = "positive"
    elif aggregate_score < -0.2:
        overall = "negative"
    else:
        overall = "neutral"

    return {
        "aggregate_score": round(aggregate_score, 4),
        "scaled_score": scaled_score,
        "adjusted_score": adjusted_score,
        "overall_sentiment": overall,
        "total_comments": count,
        "damping_factor": round(damping_factor, 3)
    }
