import pytest

from app.core.exceptions import ValidationError
from app.rag.output_parsers import parse_flashcards


def test_parse_flashcards_ok():
    raw = '[{"front":"Term","back":"Definition","hint":"a clue"}]'
    cards = parse_flashcards(raw)
    assert len(cards) == 1
    assert cards[0].front == "Term"
    assert cards[0].back == "Definition"
    assert cards[0].hint == "a clue"


def test_parse_flashcards_skips_incomplete():
    raw = '[{"front":"only front"},{"front":"f","back":"b"}]'
    cards = parse_flashcards(raw)
    assert len(cards) == 1
    assert cards[0].back == "b"


def test_parse_flashcards_no_json_raises():
    with pytest.raises(ValidationError):
        parse_flashcards("nothing here")


def test_parse_flashcards_empty_raises():
    with pytest.raises(ValidationError):
        parse_flashcards("[]")
