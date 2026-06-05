from localdocs.config import load_config


def test_load_config_uses_defaults_when_missing(tmp_path):
    config = load_config(tmp_path / "missing.toml")

    assert config.chunking.chunk_size == 220
    assert config.chunking.chunk_overlap == 40
    assert config.search.top_k == 4
    assert config.search.minimum_score == 0.05
    assert config.exports.export_dir == "exports"
    assert config.llm.use_openai_if_available is True
    assert config.warnings == []


def test_load_config_reads_valid_values(tmp_path):
    path = tmp_path / "localdocs_config.toml"
    path.write_text(
        """
[chunking]
chunk_size = 120
chunk_overlap = 20

[search]
top_k = 6
minimum_score = 0.1

[exports]
export_dir = "tmp_exports"

[llm]
use_openai_if_available = false
""",
        encoding="utf-8",
    )

    config = load_config(path)

    assert config.chunking.chunk_size == 120
    assert config.chunking.chunk_overlap == 20
    assert config.search.top_k == 6
    assert config.search.minimum_score == 0.1
    assert config.exports.export_dir == "tmp_exports"
    assert config.llm.use_openai_if_available is False
    assert config.warnings == []


def test_load_config_warns_and_uses_defaults_for_invalid_values(tmp_path):
    path = tmp_path / "localdocs_config.toml"
    path.write_text(
        """
[chunking]
chunk_size = "large"
chunk_overlap = -1

[search]
top_k = 0
minimum_score = 2

[exports]
export_dir = ""

[llm]
use_openai_if_available = "yes"
""",
        encoding="utf-8",
    )

    config = load_config(path)

    assert config.chunking.chunk_size == 220
    assert config.chunking.chunk_overlap == 40
    assert config.search.top_k == 4
    assert config.search.minimum_score == 0.05
    assert config.exports.export_dir == "exports"
    assert config.llm.use_openai_if_available is True
    assert len(config.warnings) >= 6


def test_load_config_warns_and_uses_defaults_for_invalid_toml(tmp_path):
    path = tmp_path / "localdocs_config.toml"
    path.write_text("[chunking\nchunk_size = 120", encoding="utf-8")

    config = load_config(path)

    assert config.chunking.chunk_size == 220
    assert config.search.top_k == 4
    assert config.warnings
    assert "Could not read" in config.warnings[0]
