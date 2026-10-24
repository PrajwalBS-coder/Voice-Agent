from pathlib import Path

from skills.create_document import run


def test_creates_offline_document_for_arbitrary_topic(tmp_path: Path):
    result = run({
        "topic": "photosynthesis and plant energy",
        "documents_dir": str(tmp_path),
    })

    output_path = tmp_path / "photosynthesis-and-plant-energy.md"
    assert output_path.exists()
    assert "# Photosynthesis And Plant Energy" in output_path.read_text(encoding="utf-8")
    assert "photosynthesis and plant energy" in result


def test_empty_topic_requests_clarification(tmp_path: Path):
    assert run({"topic": "", "documents_dir": str(tmp_path)}) == "What topic should I write the document about?"