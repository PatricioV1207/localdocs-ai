from app import _clear_answer_state, _clear_document_state


def test_clear_answer_state_hides_stale_answer_and_results_without_erasing_history():
    history = [object()]
    state = {
        "qa_history": history,
        "last_answer": object(),
        "last_results": [object()],
    }

    _clear_answer_state(state)

    assert state["last_answer"] is None
    assert state["last_results"] == []
    assert state["qa_history"] is history


def test_clear_document_state_removes_all_stale_document_outputs():
    state = {
        "chunks": [object()],
        "document_names": ["old.pdf"],
        "index": object(),
        "qa_history": [object()],
        "last_answer": object(),
        "summaries": [object()],
        "flashcards": [object()],
        "study_questions": [object()],
        "last_results": [object()],
    }

    _clear_document_state(state)

    assert state == {
        "chunks": [],
        "document_names": [],
        "index": None,
        "qa_history": [],
        "last_answer": None,
        "summaries": [],
        "flashcards": [],
        "study_questions": [],
        "last_results": [],
    }
