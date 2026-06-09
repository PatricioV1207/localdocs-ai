import pytest

from localdocs.document_types import detect_document_type, detect_section_role
from localdocs.flashcards import generate_flashcards
from localdocs.models import DocumentChunk
from localdocs.study import generate_study_questions


def _chunk(text: str, file_name: str = "document.md") -> DocumentChunk:
    return DocumentChunk(
        text=text,
        file_name=file_name,
        file_path=file_name,
        file_type="markdown",
        chunk_index=1,
    )


@pytest.mark.parametrize(
    ("document_type", "text"),
    [
        (
            "academic_practice",
            "# Learning Objectives\nStudents will compare evaporation and condensation. "
            "Exercise: explain how the processes differ.",
        ),
        (
            "technical_manual",
            "# Installation Procedure\nBefore installation, close the supply valve. "
            "Step 1: attach the filter housing.",
        ),
        (
            "research_paper",
            "# Spaced Review Results\nMethods used two participant groups. "
            "Results showed that spaced review increased recall.",
        ),
        (
            "legal_business",
            "# Service Agreement\nThe supplier shall retain audit records. "
            "The agreement has an effective date of July 1.",
        ),
        (
            "generic",
            "# Community Garden\nThe community garden combines shared plots and weekly meetings.",
        ),
    ],
)
def test_detect_document_type_for_general_domains(document_type, text):
    assert detect_document_type([_chunk(text)]).document_type == document_type


@pytest.mark.parametrize(
    ("role", "text"),
    [
        ("definition", "A watershed is defined as the land draining to one outlet."),
        ("objective", "# Learning Objective\nStudents will compare two energy sources."),
        ("procedure", "# Procedure\nStep 1: connect the cable before starting."),
        ("result", "# Results\nThe study found that recall increased after spaced review."),
        ("obligation", "The supplier shall retain the records for five years."),
        ("question", "# Questions\nExplain why the two outcomes differ?"),
        ("example", "# Worked Example\nFor instance, use a smaller sample."),
        ("overview", "# Introduction\nThis section gives an overview of the project."),
    ],
)
def test_detect_section_role_from_reusable_structure(role, text):
    assert detect_section_role(text) == role


def test_generators_use_document_structure_for_templates():
    chunks = [
        _chunk(
            "# Learning Objectives\nStudents will compare evaporation and condensation.",
            "practice.md",
        ),
        _chunk(
            "# Installation Procedure\nBefore installation, close the water supply.",
            "manual.md",
        ),
        _chunk(
            "# Spaced Review Results\nResults showed that spaced review increased recall.",
            "paper.md",
        ),
        _chunk(
            "# Service Agreement\nThe supplier shall retain audit records.",
            "agreement.md",
        ),
    ]

    questions = generate_study_questions(chunks, max_questions=10)
    cards = generate_flashcards(chunks, max_cards=10)
    question_text = " ".join(item.question for item in questions)
    card_text = " ".join(item.question for item in cards)

    assert "What should a learner understand about" in question_text
    assert "How should" in question_text
    assert "What did the document find about" in question_text
    assert "What obligation applies to" in question_text
    assert "What should be understood about" in card_text
    assert "What procedure is specified for" in card_text
    assert "What result is reported about" in card_text
    assert "What requirement applies to" in card_text
