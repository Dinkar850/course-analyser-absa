from collections import defaultdict

def merge_aspects(aspect_list):
    # Step 1: group every aspect
    grouped = defaultdict(list)

    for it in aspect_list:
        aspect = it["aspect"]
        sentiment = it["sentiment"]
        confidence = it["confidence"] or 0.0

        # convert sentiment to signed number
        if sentiment == "positive":
            signed = +confidence
        elif sentiment == "negative":
            signed = -confidence
        else:
            signed = 0.0

        grouped[aspect].append(signed)

    # Step 2: compute merged result
    merged = []

    for aspect, signed_scores in grouped.items():

        avg = sum(signed_scores) / len(signed_scores)   # average signed

        # determine final sentiment
        if avg > 0:
            final_sentiment = "positive"
        elif avg < 0:
            final_sentiment = "negative"
        else:
            final_sentiment = "neutral"

        merged.append({
            "aspect": aspect,
            "sentiment": final_sentiment,
            "confidence": round(abs(avg), 4) # final confidence is magnitude
        })

    return merged
