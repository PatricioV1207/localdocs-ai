from app import _clear_answer_state


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
