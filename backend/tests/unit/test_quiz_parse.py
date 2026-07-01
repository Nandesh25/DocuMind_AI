import pytest

from app.core.exceptions import ValidationError
from app.services.quiz_service import QuizService

svc = QuizService(document_repo=None, workspace_service=None, llm_client=None)


def test_parse_mcq_extracts_from_noisy_output():
    raw = (
        'Sure! Here is your quiz:\n'
        '[{"question":"Q1","options":["a","b","c","d"],'
        '"answer":"a","explanation":"because"}]\nHope it helps.'
    )
    questions = svc._parse(raw, "mcq")
    assert len(questions) == 1
    assert questions[0].options == ["a", "b", "c", "d"]
    assert questions[0].answer == "a"
    assert questions[0].explanation == "because"


def test_parse_true_false_forces_options():
    raw = '[{"question":"Q","answer":"True","explanation":"x"}]'
    questions = svc._parse(raw, "true_false")
    assert questions[0].options == ["True", "False"]


def test_parse_skips_incomplete_items():
    raw = '[{"question":"only q"},{"question":"good","answer":"a"}]'
    questions = svc._parse(raw, "short")
    assert len(questions) == 1
    assert questions[0].question == "good"


def test_parse_no_json_raises():
    with pytest.raises(ValidationError):
        svc._parse("no json here", "mcq")


def test_parse_invalid_json_raises():
    with pytest.raises(ValidationError):
        svc._parse('[{"question": bad}]', "mcq")


def test_parse_empty_list_raises():
    with pytest.raises(ValidationError):
        svc._parse("[]", "mcq")
