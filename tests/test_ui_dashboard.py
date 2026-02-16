"""Tests for Qt UI dashboard."""

import pytest
from PySide6.QtWidgets import QApplication
from ui.stats_dashboard import StatsDashboard, MatchTableModel


@pytest.fixture
def app():
    """Create QApplication for tests."""
    if not QApplication.instance():
        app = QApplication([])
    else:
        app = QApplication.instance()
    return app


def test_match_table_model():
    """Test match table model creation and basic functionality."""
    model = MatchTableModel()
    
    # Should have at least 0 rows initially
    assert model.rowCount() >= 0
    assert model.columnCount() == 6  # ID, Start, End, Score, Lines, Agent
    
    # Check headers
    headers = []
    for i in range(model.columnCount()):
        headers.append(model.headerData(i, 1))  # Qt.Horizontal = 1
    
    expected_headers = ["ID", "Start", "End", "Score", "Lines", "Agent"]
    assert headers == expected_headers


def test_stats_dashboard_creation(qtbot, app):
    """Test that stats dashboard can be created without crashing."""
    dashboard = StatsDashboard()
    qtbot.addWidget(dashboard)
    
    # Just make sure it shows without crashing
    dashboard.show()
    qtbot.waitExposed(dashboard)


def test_dashboard_refresh(qtbot, app):
    """Test dashboard refresh functionality."""
    dashboard = StatsDashboard()
    qtbot.addWidget(dashboard)
    
    # Test refresh doesn't crash
    dashboard._refresh()
    
    # Should still have a table model
    assert dashboard.model is not None
    assert dashboard.model.rowCount() >= 0
