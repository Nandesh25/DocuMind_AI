RAG_SYSTEM_PROMPT = (
    "You are DocuMind AI, an assistant that answers questions strictly using the "
    "provided document context. If the answer is not contained in the context, say "
    "you do not have enough information. Always be concise and cite facts from the "
    "context."
)


def build_rag_prompt(
    question: str,
    context_blocks: list[str],
    history: list[tuple[str, str]] | None = None,
) -> str:
    context = "\n\n".join(
        f"[Source {i + 1}]\n{block}" for i, block in enumerate(context_blocks)
    )

    conversation = ""
    if history:
        turns = []
        for role, content in history:
            speaker = "User" if role == "user" else "Assistant"
            turns.append(f"{speaker}: {content}")
        conversation = "Conversation so far:\n" + "\n".join(turns) + "\n\n"

    return (
        f"{RAG_SYSTEM_PROMPT}\n\n"
        f"Context:\n{context}\n\n"
        f"{conversation}"
        f"Question: {question}\n\n"
        f"Answer:"
    )


def build_summary_prompt(summary_type: str, text: str) -> str:
    instructions = {
        "short": (
            "Write a SHORT summary in 2-3 sentences that captures the essence of "
            "the document."
        ),
        "detailed": (
            "Write a DETAILED summary in several paragraphs. Cover the major "
            "sections, key arguments, findings, and supporting details so a "
            "reader understands the document without reading it in full."
        ),
        "executive": (
            "Write an EXECUTIVE summary for decision-makers. Lead with the key "
            "takeaways, then cover decisions, risks, outcomes, and recommended "
            "actions. Be concise and business-oriented."
        ),
    }
    instruction = instructions.get(summary_type, instructions["short"])
    return (
        f"You are summarizing a document. {instruction}\n\n"
        f"Document:\n{text}\n\nSummary:"
    )


def build_comparison_prompt(
    title_a: str, text_a: str, title_b: str, text_b: str
) -> str:
    return (
        "You are comparing two documents. Produce a clear, structured comparison "
        "with exactly three sections titled 'Similarities', 'Differences', and "
        "'Conclusion'. Base your analysis only on the content provided.\n\n"
        f"=== Document A — {title_a} ===\n{text_a}\n\n"
        f"=== Document B — {title_b} ===\n{text_b}\n\n"
        "Comparison:"
    )


def build_quiz_prompt(quiz_type: str, num_questions: int, text: str) -> str:
    specs = {
        "mcq": (
            f"Generate {num_questions} multiple-choice questions. Each JSON object "
            'must have "question" (string), "options" (array of exactly 4 distinct '
            'strings), "answer" (the exact text of the correct option), and '
            '"explanation" (string).'
        ),
        "true_false": (
            f"Generate {num_questions} true/false questions. Each JSON object must "
            'have "question" (string), "answer" (either "True" or "False"), and '
            '"explanation" (string). Do not include an "options" field.'
        ),
        "short": (
            f"Generate {num_questions} short-answer questions. Each JSON object must "
            'have "question" (string) and "answer" (a concise model answer string).'
        ),
    }
    spec = specs.get(quiz_type, specs["mcq"])
    return (
        "You are a quiz generator. Based ONLY on the document below, "
        f"{spec}\n"
        "Respond with ONLY a valid JSON array of question objects — no markdown "
        "fences, no commentary before or after.\n\n"
        f"Document:\n{text}\n\nJSON:"
    )


def build_flashcards_prompt(num_cards: int, text: str) -> str:
    return (
        "You are creating study flashcards. Based ONLY on the document below, "
        f'generate {num_cards} flashcards. Each JSON object must have "front" '
        '(a concise question, term, or concept) and "back" (the answer or '
        'explanation). Optionally include "hint" (a short hint).\n'
        "Respond with ONLY a valid JSON array of flashcard objects — no markdown "
        "fences, no commentary before or after.\n\n"
        f"Document:\n{text}\n\nJSON:"
    )