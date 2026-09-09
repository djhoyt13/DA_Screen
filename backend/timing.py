"""Parse optional client timing payloads for quiz telemetry."""
from datetime import datetime, timezone


def parse_iso_datetime(value):
    """Parse an ISO-8601 timestamp into a naive UTC datetime, or None."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def extract_timing(payload):
    """Normalize timing fields from a submit payload.

    Expected shape::

        {
          "opened_at": "...",
          "acknowledged_at": "...",
          "submitted_at": "...",
          "answers": { "<question_key>": "..." }
        }

    Missing/invalid values become None. Never raises.
    """
    timing = payload.get("timing") if isinstance(payload, dict) else None
    if not isinstance(timing, dict):
        timing = {}

    answer_times = {}
    raw_answers = timing.get("answers")
    if isinstance(raw_answers, dict):
        for key, value in raw_answers.items():
            parsed = parse_iso_datetime(value)
            if parsed is not None:
                answer_times[str(key)] = parsed

    return {
        "opened_at": parse_iso_datetime(timing.get("opened_at")),
        "acknowledged_at": parse_iso_datetime(timing.get("acknowledged_at")),
        "submitted_at": parse_iso_datetime(timing.get("submitted_at")),
        "answer_timestamps": answer_times,
    }
