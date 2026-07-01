"""Pure parsers for LLM JSON output (quiz / flashcards).

Kept free of heavy dependencies (no SQLAlchemy / LangChain) so the parsing
logic — the most error-prone part of the AI features — is easily unit-tested.
"""

import json
import re

from app.core.exceptions import ValidationError
from app.schemas.flashcard_schema import Flashcard
from app.schemas.quiz_schema import QuizQuestion

_JSON_ARRAY = re.compile(r"\[.*\]", re.DOTALL)


def _extract_array(raw: str, kind: str) -> list:
    match = _JSON_ARRAY.search(raw)
    if not match:
        raise ValidationError(
            f"The model did not return valid {kind}. Please try again."
        )
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise ValidationError(
            f"The generated {kind} could not be parsed. Please try again."
        ) from exc
    return data if isinstance(data, list) else []


def parse_quiz(raw: str, quiz_type: str) -> list[QuizQuestion]:
    items = _extract_array(raw, "quiz")
    questions: list[QuizQuestion] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        question = item.get("question")
        answer = item.get("answer")
        if not question or answer is None:
            continue

        options = item.get("options")
        if quiz_type == "true_false":
            options = ["True", "False"]
        elif not isinstance(options, list):
            options = None
        else:
            options = [str(o) for o in options]

        questions.append(
            QuizQuestion(
                question=str(question),
                options=options,
                answer=str(answer),
                explanation=(
                    str(item["explanation"]) if item.get("explanation") else None
                ),
            )
        )

    if not questions:
        raise ValidationError(
            "No quiz questions could be generated. Please try again."
        )
    return questions


def parse_flashcards(raw: str) -> list[Flashcard]:
    items = _extract_array(raw, "flashcards")
    cards: list[Flashcard] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        front = item.get("front")
        back = item.get("back")
        if not front or not back:
            continue
        cards.append(
            Flashcard(
                front=str(front),
                back=str(back),
                hint=str(item["hint"]) if item.get("hint") else None,
            )
        )

    if not cards:
        raise ValidationError(
            "No flashcards could be generated. Please try again."
        )
    return cards
