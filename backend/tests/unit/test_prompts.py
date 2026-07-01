from app.rag.prompt_templates import (
    build_comparison_prompt,
    build_flashcards_prompt,
    build_quiz_prompt,
    build_rag_prompt,
    build_summary_prompt,
)


def test_rag_prompt_includes_context_and_question():
    prompt = build_rag_prompt("What is X?", ["alpha", "beta"])
    assert "Source 1" in prompt
    assert "Source 2" in prompt
    assert "What is X?" in prompt
    assert "Conversation so far" not in prompt


def test_rag_prompt_with_history():
    prompt = build_rag_prompt(
        "Follow up?",
        ["ctx"],
        history=[("user", "hi"), ("assistant", "hello")],
    )
    assert "Conversation so far" in prompt
    assert "User: hi" in prompt
    assert "Assistant: hello" in prompt


def test_summary_prompt_variants():
    assert "SHORT" in build_summary_prompt("short", "text")
    assert "DETAILED" in build_summary_prompt("detailed", "text")
    assert "EXECUTIVE" in build_summary_prompt("executive", "text")


def test_comparison_prompt_sections():
    prompt = build_comparison_prompt("A", "ta", "B", "tb")
    assert "Similarities" in prompt
    assert "Differences" in prompt
    assert "Conclusion" in prompt


def test_quiz_prompt_types():
    assert "multiple-choice" in build_quiz_prompt("mcq", 5, "t")
    assert "true/false" in build_quiz_prompt("true_false", 5, "t")
    assert "short-answer" in build_quiz_prompt("short", 5, "t")
    assert "JSON" in build_quiz_prompt("mcq", 5, "t")


def test_flashcards_prompt():
    prompt = build_flashcards_prompt(10, "t")
    assert "flashcards" in prompt
    assert "front" in prompt and "back" in prompt
