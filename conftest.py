import pathlib


def pytest_sessionstart(session):
    artifact_path = pathlib.Path("artifacts") / "test_results.txt"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text("OK", encoding="utf-8")
