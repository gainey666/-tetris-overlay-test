"""Orchestrator should load a plan and call each registered agent."""

from unittest.mock import MagicMock, patch

import pytest

from src.orchestrator.orchestrator import AGENT_REGISTRY, main as orchestrate


@pytest.mark.skip(reason="Keyboard hook blocks CI")
def test_plan_execution(tmp_path):
    plan_content = """
    steps:
      - name: dummy_one
        params: {}
      - name: dummy_two
        params:
          foo: bar
    """
    plan_file = tmp_path / "plan.yaml"
    plan_file.write_text(plan_content)

    mock_one = MagicMock()
    mock_two = MagicMock()

    # Temporarily replace the registry entries
    with patch.dict(
        AGENT_REGISTRY, {"dummy_one": mock_one, "dummy_two": mock_two}, clear=True
    ):
        orchestrate(plan_path=str(plan_file))

    mock_one.handle.assert_called_once_with({})
    mock_two.handle.assert_called_once_with({"foo": "bar"})
