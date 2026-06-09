from localdocs.flashcards import generate_flashcards
from localdocs.models import SearchResult
from localdocs.qa import answer_question
from localdocs.study import generate_study_questions


def test_golden_study_questions_use_only_technical_chunks(spanish_safety_chunks):
    questions = generate_study_questions(spanish_safety_chunks, max_questions=10)

    assert {question.citation.chunk_index for question in questions} == {3, 4, 5}
    assert all(question.question.startswith("¿") for question in questions)
    combined = " ".join(question.question.lower() for question in questions)
    assert "descarga segura del actuador" in combined
    assert "prevención de arranque inesperado" in combined
    assert "válvula 1v1" in combined
    assert any("válvula 1v1" in question.question.lower() for question in questions)
    assert "información legal" not in combined
    assert "ciente volumen" not in combined


def test_golden_flashcards_are_spanish_grounded_and_technical(spanish_safety_chunks):
    cards = generate_flashcards(spanish_safety_chunks, max_cards=10)

    assert {card.citation.chunk_index for card in cards} == {3, 4, 5}
    assert all(card.question.startswith("¿") for card in cards)
    assert all(not card.question.startswith("What is") for card in cards)
    valve_cards = [card for card in cards if "válvula 1v1" in card.question.lower()]
    assert len(valve_cards) == 1
    assert "descarga segura del actuador" in valve_cards[0].answer.lower()
    for card in cards:
        question_terms = set(card.question.lower().replace("¿", "").replace("?", "").split())
        answer_terms = set(card.answer.lower().split())
        assert question_terms & answer_terms
    combined = " ".join(f"{card.question} {card.answer}".lower() for card in cards)
    assert "información legal" not in combined
    assert "ciente volumen" not in combined


def test_golden_local_qa_synthesizes_three_technical_chunks(spanish_safety_chunks):
    scores = [0.96, 0.91, 0.89, 0.88, 0.87, 0.93]
    results = [
        SearchResult(chunk=chunk, score=score)
        for chunk, score in zip(spanish_safety_chunks, scores, strict=True)
    ]

    answer = answer_question(
        "¿Qué es descarga segura del actuador y prevención de arranque inesperado?",
        results,
        use_openai=False,
    )

    assert answer.enough_evidence is True
    assert answer.used_llm is False
    assert {citation.chunk_index for citation in answer.citations} == {3, 4, 5}
    assert {result.chunk_index for result in answer.context} == {3, 4, 5}
    assert "descarga segura del actuador" in answer.answer.lower()
    assert "prevención de arranque inesperado" in answer.answer.lower()
    assert "válvula 1v1" in answer.answer.lower()
    assert "Based on" not in answer.answer
    assert "\n-" not in answer.answer
    assert "información legal" not in answer.answer.lower()
    lower_answer = answer.answer.lower()
    assert lower_answer.index("descarga segura del actuador se define") < lower_answer.index(
        "prevención de arranque inesperado es"
    )
    assert lower_answer.index("prevención de arranque inesperado es") < lower_answer.index(
        "válvula 1v1"
    )
