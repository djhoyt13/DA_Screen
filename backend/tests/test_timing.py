"""Timing payload parsing tests."""
from datetime import datetime

from backend.timing import extract_timing, parse_iso_datetime


def test_parse_iso_datetime_zulu_and_offset():
    assert parse_iso_datetime("2026-09-09T16:00:00Z") == datetime(2026, 9, 9, 16, 0, 0)
    assert parse_iso_datetime("2026-09-09T12:00:00-04:00") == datetime(2026, 9, 9, 16, 0, 0)
    assert parse_iso_datetime("") is None
    assert parse_iso_datetime("not-a-date") is None


def test_extract_timing_normalizes_payload():
    timing = extract_timing(
        {
            "timing": {
                "opened_at": "2026-09-09T16:00:00Z",
                "acknowledged_at": "2026-09-09T16:01:00Z",
                "submitted_at": "2026-09-09T16:20:00Z",
                "answers": {
                    "answer_Unpacking": "2026-09-09T16:05:00Z",
                    "answer_Loops": "bad",
                },
            }
        }
    )
    assert timing["opened_at"] == datetime(2026, 9, 9, 16, 0, 0)
    assert timing["acknowledged_at"] == datetime(2026, 9, 9, 16, 1, 0)
    assert timing["submitted_at"] == datetime(2026, 9, 9, 16, 20, 0)
    assert timing["answer_timestamps"]["answer_Unpacking"] == datetime(2026, 9, 9, 16, 5, 0)
    assert "answer_Loops" not in timing["answer_timestamps"]


def test_extract_timing_missing_is_empty():
    timing = extract_timing({})
    assert timing["opened_at"] is None
    assert timing["answer_timestamps"] == {}
