# analyzer.py
from typing import List, Dict, Any, Optional
import threading

# Use the ATEPC manager for aspect extraction + polarity classification
from pyabsa import ATEPCCheckpointManager

_sentiment_map = {
    "positive": "positive",
    "negative": "negative",
    "neutral":  "neutral",
    "pos": "positive",
    "neg": "negative",
    "neu": "neutral"
}


class ABSAService:
    _classifier = None
    _lock = threading.Lock()

    def __init__(self, checkpoint: str = "multilingual"):
        self.checkpoint = checkpoint

    def _load_model(self):
        if ABSAService._classifier is not None:
            return

        with ABSAService._lock:
            if ABSAService._classifier is not None:
                return
            ABSAService._classifier = ATEPCCheckpointManager.get_aspect_extractor(
                self.checkpoint
            )

    def _normalize_sentiment(self, s: Any) -> str:
        if not s:
            return "neutral"
        if isinstance(s, str):
            return _sentiment_map.get(s.lower(), s.lower())
        return str(s).lower()

    def _parse_atepc_result(self, raw_result: Any, source_text: Optional[str] = None) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []

        if raw_result is None:
            return items

        # Case: list → flatten
        if isinstance(raw_result, list):
            for elem in raw_result:
                items.extend(self._parse_atepc_result(elem, source_text))
            return items

        # Case: string → treat as sentiment only
        if isinstance(raw_result, str):
            items.append({
                "aspect": None,
                "sentiment": self._normalize_sentiment(raw_result),
                "polarity": self._normalize_sentiment(raw_result),
                "confidence": None,
                "_source_text": source_text
            })
            return items

        # ============================
        # Case: dict (ATEPC normal)
        # ============================
        if isinstance(raw_result, dict):
            aspects = (
                raw_result.get("aspect")
                or raw_result.get("aspect_term")
                or raw_result.get("extracted_aspect")
                or []
            )
            sentiments = (
                raw_result.get("sentiment")
                or raw_result.get("polarity")
                or raw_result.get("sentiment_pred")
                or []
            )

            # NEW: get confidence
            confidences = (
                raw_result.get("confidence")
                or raw_result.get("sentiment_confidence")
                or []
            )

            # Normalize formats
            if isinstance(aspects, str):
                aspects = [aspects]
            if isinstance(sentiments, str):
                sentiments = [sentiments]
            if isinstance(confidences, (int, float)):
                confidences = [confidences]

            # Zip aspects + sentiments (+ optional confidence)
            if isinstance(aspects, list) and isinstance(sentiments, list) and len(aspects) == len(sentiments):
                for i, (a, s) in enumerate(zip(aspects, sentiments)):
                    conf = confidences[i] if i < len(confidences) else None

                    items.append({
                        "aspect": a.lower() if a else None,
                        "sentiment": self._normalize_sentiment(s),
                        "polarity": self._normalize_sentiment(s),
                        "confidence": conf,        # <-- ADDED
                        "_source_text": source_text
                    })
                return items

            # Only aspects known
            if isinstance(aspects, list) and len(aspects) > 0:
                for a in aspects:
                    items.append({
                        "aspect": a.lower() if a else None,
                        "sentiment": "neutral",
                        "polarity": "neutral",
                        "confidence": None,
                        "_source_text": source_text
                    })
                return items

            # Only sentiment known
            if isinstance(sentiments, list) and len(sentiments) > 0:
                for s in sentiments:
                    items.append({
                        "aspect": None,
                        "sentiment": self._normalize_sentiment(s),
                        "polarity": self._normalize_sentiment(s),
                        "confidence": None,
                        "_source_text": source_text
                    })
                return items

        # fallback
        return items

    def analyze_text(self, text: str) -> List[Dict[str, Any]]:
        if not text:
            return []

        self._load_model()

        try:
            raw = ABSAService._classifier.extract_aspect(
                inference_source=[text],
                pred_sentiment=True,
                save_result=False
            )
        except Exception as e:
            raise RuntimeError(f"ATEPC extract_aspect failed: {e}")

        parsed = self._parse_atepc_result(raw, source_text=text)
        return parsed

    def analyze_batch(self, texts: List[str]) -> List[List[Dict[str, Any]]]:
        results = []
        for t in texts:
            results.append(self.analyze_text(t))
        return results


if __name__ == "__main__":
    svc = ABSAService()
    print(svc.analyze_text("I LOOOVE their eggplant pizza , as well as their pastas !"))
