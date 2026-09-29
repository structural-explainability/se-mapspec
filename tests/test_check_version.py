"""Version consistency and missing-tag behavior."""

from pathlib import Path

from se_mapspec import check_version


def test_version_match(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "CITATION.cff").write_text('version: "0.1.0"\n', encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        '[tool.hatch.version]\nfallback-version = "0.1.0"\n', encoding="utf-8"
    )
    assert check_version.run() == 0
    monkeypatch.setattr(check_version, "get_git_tag", lambda: "v0.1.0")
    assert check_version.run(require_tag=True) == 0


def test_version_mismatch_and_missing_tag(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "CITATION.cff").write_text('version: "0.1.0"\n', encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        '[tool.hatch.version]\nfallback-version = "0.1.1"\n', encoding="utf-8"
    )
    assert check_version.run() == 1

    def missing_tag() -> str:
        raise RuntimeError("no tag")

    monkeypatch.setattr(check_version, "get_git_tag", missing_tag)
    assert check_version.run(require_tag=True) == 1


def test_missing_files_reports_error(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    assert check_version.run() == 1
