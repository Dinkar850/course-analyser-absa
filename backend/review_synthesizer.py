# review_synthesizer.py
from collections import defaultdict
from typing import List, Dict, Any

ASPECT_KEYWORDS = {
    "instructor": [
        "instructor", "teacher", "lecturer", "tutor", "professor", "mentor",
        "instructors", "teachers", "lecturers", "tutors", "professors", "mentors",
        "teach", "teaches", "taught", "teaching", "lecture", "lectures", "lectured", "lecturing",
        "guide", "guides", "guided", "guiding",
        "man", "guy", "sir", "ma'am", "lady", "mam", "madam" "followers", "fan", "fans", "explain", "explained", "explanation", "explaining", "guide", "guides", "guided", "guiding", "lecturing", "lectured", "channel", "channels", "advice"
    ],

    "content": [
        "content", "slide", "slides", "material", "materials", "topic", "topics",
        "lesson", "lessons", "chapter", "chapters", "course", "courses", "lecture", "lectures"
        "project", "projects", "practical", "practicals", "tutorial", "tutorials",
        "formula", "formulas", "formulae",
        "python", "java", "c++", "javascript", "language", "framework", "library", "libraries", "captions", "caption", "code", "coding", "programming", "learn", "learning", "program", "programs", "learned", "learns", "playlist", "concept", "concepts", "subtitle", "subtitles","subject", "software", "softwares", "Functions", "Objects", "old"
    ],

    "pace": [
        "pace", "pacing", "speed", "timing", "duration", "flow",
        "fast", "faster", "quick", "quicker", "slow", "slower", "laggy", "dragging",
        "boring", "bored", "rush", "rushed", "hurried", "too fast", "too slow",
        "slowly", "quickly", "follow", "follows", "following", "time", "timing", "timed"
    ],

    "pricing": [
        "price", "pricing", "cost", "fees", "subscription", "membership",
        "free", "cheap", "affordable", "expensive", "costly", "paid", "unpaid",
        "money", "worth", "value", "purchase", "buy", "payment", "donation", "premium", "ads", "ad", "member", "members", "members only"
    ],

    "sound_quality": [
        "sound", "audio", "voice", "microphone", "mic", "clarity", "noise", "noisy",
        "echo", "distortion", "volume", "loud", "quiet", "muffled", "clear", "unclear",
        "background noise", "buzz", "hiss", "speaker", "words", "word", "clarity",
    ],

    "video_quality": [
        "video", "videos", "quality", "graphics", "blur", "blurry", "resolution", "resolutions"
        "visual", "visuals", "camera", "focus", "hd", "1080p", "720p", "recording",
        "footage", "frame", "brightness", "contrast", "unclear", "subtitle", "subtitles", "background", "backgrounds", "dark", "light", "bright"
    ],
}

# aspect to category mapper

def map_aspect_category(aspect: str) -> str:
    if not aspect:
        return "misc"

    aspect = aspect.lower().strip()
    for category, keywords in ASPECT_KEYWORDS.items():
        for kw in keywords:
            if kw in aspect:
                return category
    return "misc"


# aggregate aspect scores

def synthesize_category_scores(aspect_list: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
   
    category_scores = defaultdict(lambda: {"score_sum": 0.0, "count": 0})

    for item in aspect_list:
        aspect = item.get("aspect")
        sentiment = item.get("sentiment", "").lower()
        confidence = float(item.get("confidence", 0.0))

        if not aspect:
            continue

        category = map_aspect_category(aspect)
        if category == "misc":
            continue 

        if "pos" in sentiment or "positive" in sentiment:
            signed_score = confidence
        elif "neg" in sentiment or "negative" in sentiment:
            signed_score = -confidence
        else:
            signed_score = 0.0  # neutral

        category_scores[category]["score_sum"] += signed_score
        category_scores[category]["count"] += 1

    results = {}
    for cat, vals in category_scores.items():
        count = vals["count"]
        avg_score = vals["score_sum"] / count if count > 0 else 0.0
        results[cat] = {"score": round(avg_score, 3), "count": count}

    return results


# humanized review generator

def generate_humanized_review(category_scores: Dict[str, Dict[str, float]]) -> str:

    grouped_phrases = defaultdict(list)

    for category, data in category_scores.items():
        score = data["score"]
        count = data["count"]

        if count == 0:
            continue

        if score >= 0.9:
            grouped_phrases["excellent"].append(category)
        elif 0.65 <= score < 0.9:
            grouped_phrases["good"].append(category)
        elif 0.1 <= score < 0.65:
            grouped_phrases["decent"].append(category)
        elif -0.1 < score < 0.1:
            grouped_phrases["mixed"].append(category)
        elif -0.45 < score <= -0.1:
            grouped_phrases["below"].append(category)
        elif -0.75 < score <= -0.45:
            grouped_phrases["poor"].append(category)
        else:
            grouped_phrases["terrible"].append(category)

    def join_aspects(lst):
        if len(lst) == 1:
            return lst[0].replace("_", " ")
        elif len(lst) == 2:
            return f"{lst[0].replace('_',' ')} and {lst[1].replace('_',' ')}"
        else:
            return ", ".join(a.replace("_", " ") for a in lst[:-1]) + f", and {lst[-1].replace('_', ' ')}"

    parts = []
    if grouped_phrases["excellent"]:
        parts.append(f"{join_aspects(grouped_phrases['excellent']).capitalize()} were excellent and highly praised.")
    if grouped_phrases["good"]:
        parts.append(f"{join_aspects(grouped_phrases['good']).capitalize()} were good and appreciated.")
    if grouped_phrases["decent"]:
        parts.append(f"{join_aspects(grouped_phrases['decent']).capitalize()} were decent but could have been better.")
    if grouped_phrases["mixed"]:
        parts.append(f"{join_aspects(grouped_phrases['mixed']).capitalize()} received mixed opinions.")
    if grouped_phrases["below"]:
        parts.append(f"{join_aspects(grouped_phrases['below']).capitalize()} were below expectations.")
    if grouped_phrases["poor"]:
        parts.append(f"{join_aspects(grouped_phrases['poor']).capitalize()} were poor and disappointed many.")
    if grouped_phrases["terrible"]:
        parts.append(f"{join_aspects(grouped_phrases['terrible']).capitalize()} were terrible and widely criticized.")

    if not parts:
        return "Not enough feedback to generate a meaningful review."

    return " ".join(parts)

# main function to call
def synthesize_review(aspect_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    category_scores = synthesize_category_scores(aspect_list)
    review_text = generate_humanized_review(category_scores)

    return {
        "summary": review_text,
        "categories": category_scores
    }


if __name__ == "__main__":
    sample_aspects = [
        {"aspect": "teacher", "sentiment": "positive", "confidence": 0.92},
        {"aspect": "content", "sentiment": "positive", "confidence": 0.85},
        {"aspect": "pace", "sentiment": "negative", "confidence": 0.45},
        {"aspect": "voice", "sentiment": "negative", "confidence": 0.78},
        {"aspect": "video", "sentiment": "positive", "confidence": 0.7},
        {"aspect": "project", "sentiment": "positive", "confidence": 0.9},
    ]

    result = synthesize_review(sample_aspects)
    print("SUMMARY:")
    print(result["summary"])
    print("\nCATEGORY SCORES:")
    print(result["categories"])
