"""Configuration loading for LocalDocs AI."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import tomllib

DEFAULT_CONFIG_PATH = Path("localdocs_config.toml")


@dataclass(frozen=True)
class ChunkingConfig:
    strategy: str = "word"
    chunk_size: int = 220
    chunk_overlap: int = 40


@dataclass(frozen=True)
class SearchConfig:
    top_k: int = 4
    minimum_score: float = 0.05


@dataclass(frozen=True)
class ExportsConfig:
    export_dir: str = "exports"


@dataclass(frozen=True)
class LLMConfig:
    use_openai_if_available: bool = True


@dataclass(frozen=True)
class StudyConfig:
    max_flashcards: int = 20
    max_questions: int = 20


@dataclass(frozen=True)
class ObsidianConfig:
    vault_dir: str = "exports/obsidian_vault"


@dataclass(frozen=True)
class AnkiConfig:
    flashcards_file: str = "exports/flashcards.tsv"


@dataclass(frozen=True)
class LocalDocsConfig:
    chunking: ChunkingConfig = field(default_factory=ChunkingConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    exports: ExportsConfig = field(default_factory=ExportsConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    study: StudyConfig = field(default_factory=StudyConfig)
    obsidian: ObsidianConfig = field(default_factory=ObsidianConfig)
    anki: AnkiConfig = field(default_factory=AnkiConfig)
    warnings: list[str] = field(default_factory=list)


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> LocalDocsConfig:
    """Load localdocs_config.toml, falling back to defaults on missing or invalid values."""

    config_path = Path(path)
    if not config_path.exists():
        return LocalDocsConfig()

    try:
        raw_config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return LocalDocsConfig(warnings=[f"Could not read {config_path}: {exc}. Using default settings."])

    warnings: list[str] = []
    chunking_section = _section(raw_config, "chunking", warnings)
    search_section = _section(raw_config, "search", warnings)
    exports_section = _section(raw_config, "exports", warnings)
    llm_section = _section(raw_config, "llm", warnings)
    study_section = _section(raw_config, "study", warnings)
    obsidian_section = _section(raw_config, "obsidian", warnings)
    anki_section = _section(raw_config, "anki", warnings)

    strategy = _choice(chunking_section, "strategy", "word", {"word", "paragraph", "heading"}, warnings)
    chunk_size = _positive_int(chunking_section, "chunk_size", 220, warnings)
    chunk_overlap = _non_negative_int(chunking_section, "chunk_overlap", 40, warnings)
    if chunk_overlap >= chunk_size:
        warnings.append("chunking.chunk_overlap must be smaller than chunking.chunk_size. Using default overlap.")
        chunk_overlap = 40
        if chunk_overlap >= chunk_size:
            chunk_size = 220

    top_k = _positive_int(search_section, "top_k", 4, warnings)
    minimum_score = _score(search_section, "minimum_score", 0.05, warnings)
    export_dir = _string(exports_section, "export_dir", "exports", warnings)
    use_openai = _bool(llm_section, "use_openai_if_available", True, warnings)
    max_flashcards = _positive_int(study_section, "max_flashcards", 20, warnings)
    max_questions = _positive_int(study_section, "max_questions", 20, warnings)
    vault_dir = _string(obsidian_section, "vault_dir", "exports/obsidian_vault", warnings)
    flashcards_file = _string(anki_section, "flashcards_file", "exports/flashcards.tsv", warnings)

    return LocalDocsConfig(
        chunking=ChunkingConfig(strategy=strategy, chunk_size=chunk_size, chunk_overlap=chunk_overlap),
        search=SearchConfig(top_k=top_k, minimum_score=minimum_score),
        exports=ExportsConfig(export_dir=export_dir),
        llm=LLMConfig(use_openai_if_available=use_openai),
        study=StudyConfig(max_flashcards=max_flashcards, max_questions=max_questions),
        obsidian=ObsidianConfig(vault_dir=vault_dir),
        anki=AnkiConfig(flashcards_file=flashcards_file),
        warnings=warnings,
    )


def _section(config: dict[str, Any], name: str, warnings: list[str]) -> dict[str, Any]:
    value = config.get(name, {})
    if isinstance(value, dict):
        return value
    warnings.append(f"{name} must be a table. Using defaults for that section.")
    return {}


def _positive_int(section: dict[str, Any], key: str, default: int, warnings: list[str]) -> int:
    value = section.get(key, default)
    if isinstance(value, int) and not isinstance(value, bool) and value > 0:
        return value
    warnings.append(f"{key} must be a positive integer. Using {default}.")
    return default


def _non_negative_int(section: dict[str, Any], key: str, default: int, warnings: list[str]) -> int:
    value = section.get(key, default)
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    warnings.append(f"{key} must be a non-negative integer. Using {default}.")
    return default


def _score(section: dict[str, Any], key: str, default: float, warnings: list[str]) -> float:
    value = section.get(key, default)
    if isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 1:
        return float(value)
    warnings.append(f"{key} must be a number from 0 to 1. Using {default}.")
    return default


def _choice(
    section: dict[str, Any],
    key: str,
    default: str,
    choices: set[str],
    warnings: list[str],
) -> str:
    value = section.get(key, default)
    if isinstance(value, str) and value in choices:
        return value
    warnings.append(f"{key} must be one of {', '.join(sorted(choices))}. Using {default}.")
    return default


def _string(section: dict[str, Any], key: str, default: str, warnings: list[str]) -> str:
    value = section.get(key, default)
    if isinstance(value, str) and value.strip():
        return value
    warnings.append(f"{key} must be a non-empty string. Using {default}.")
    return default


def _bool(section: dict[str, Any], key: str, default: bool, warnings: list[str]) -> bool:
    value = section.get(key, default)
    if isinstance(value, bool):
        return value
    warnings.append(f"{key} must be true or false. Using {default}.")
    return default
