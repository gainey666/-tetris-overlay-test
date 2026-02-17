"""Qt Statistics Dashboard with charts and export functionality."""

import sys
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QComboBox, QDateEdit,
    QFileDialog, QMessageBox, QTabWidget, QGroupBox, QSpinBox,
    QTextEdit, QSplitter
)
from PySide6.QtCore import Qt, QDate, QTimer, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QPainter, QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import mplcursors

from stats.service import stats_service, MatchStats
from stats.db import get_session, Match, Event, init_db
from sqlmodel import select
from collections import Counter

class MatchTableModel(QAbstractTableModel):
    """Table model for displaying matches."""
    def __init__(self):
        super().__init__()
        self._data = []
        self._load()

    def _load(self):
        """Load matches from database."""
        with get_session() as s:
            self._data = s.exec(select(Match)).all()

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return 6   # columns: ID, start, end, score, lines, agent

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        row = self._data[index.row()]
        col = index.column()
        if col == 0: 
            return row.id[:8]   # short uuid
        if col == 1: 
            return f"{row.start_ts:.2f}"
        if col == 2: 
            return f"{(row.end_ts or 0):.2f}"
        if col == 3: 
            return row.total_score
        if col == 4: 
            return row.total_lines
        if col == 5: 
            return row.agent

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return ["ID", "Start", "End", "Score", "Lines", "Agent"][section]
        return str(section)

    def refresh(self):
        """Refresh the data from database."""
        self.beginResetModel()
        self._load()
        self.endResetModel()


class StatsDashboard(QMainWindow):
    """Enhanced Statistics Dashboard with charts, filtering, and export."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tetris Overlay - Statistics Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        
        # Data
        self.matches: List[MatchStats] = []
        self.filtered_matches: List[MatchStats] = []

        # ---------- Export buttons ----------
        btn_layout = QHBoxLayout()
        self.export_csv_btn = QPushButton("Export CSV")
        self.export_json_btn = QPushButton("Export JSON")
        self.refresh_btn = QPushButton("Refresh")
        btn_layout.addStretch()
        btn_layout.addWidget(self.export_csv_btn)
        btn_layout.addWidget(self.export_json_btn)
        btn_layout.addWidget(self.refresh_btn)
        right.addLayout(btn_layout)

        layout.addLayout(right, 3)

        # ---------- Signals ----------
        self.table.selectionModel().currentChanged.connect(self._load_detail)
        self.export_csv_btn.clicked.connect(self._export_csv)
        self.export_json_btn.clicked.connect(self._export_json)
        self.refresh_btn.clicked.connect(self._refresh)

    def _load_detail(self, current, previous):
        """Load detailed charts for selected match."""
        if not current.isValid():
            return
        
        match_id = self.model._data[current.row()].id
        with get_session() as s:
            events = s.exec(select(Event).where(Event.match_id == match_id)).all()

        if not events:
            return

        # Clear previous plots
        self.ax_score.clear()
        self.ax_combo.clear()
        self.ax_piece.clear()

        # Score over time (cumulative lines)
        frames = [e.frame for e in events]
        lines = [e.lines_cleared for e in events]
        self.ax_score.plot(frames, lines, label="Lines per frame", color='blue')
        self.ax_score.set_xlabel("Frame")
        self.ax_score.set_ylabel("Lines cleared")
        self.ax_score.legend()
        self.ax_score.grid(True, alpha=0.3)
        self.canvas_score.draw()

        # Combo streak
        combos = [e.combo for e in events]
        self.ax_combo.bar(frames, combos, width=1, color="green", alpha=0.7)
        self.ax_combo.set_xlabel("Frame")
        self.ax_combo.set_ylabel("Combo")
        self.ax_combo.grid(True, alpha=0.3)
        self.canvas_combo.draw()

        # Piece distribution
        piece_counts = Counter(e.piece for e in events)
        pieces, counts = zip(*piece_counts.items())
        self.ax_piece.pie(counts, labels=pieces, autopct="%1.1f%%", startangle=90)
        self.ax_piece.set_title("Piece Distribution")
        self.canvas_piece.draw()

    def _export_csv(self):
        """Export selected match to CSV."""
        if not self.table.selectionModel().hasSelection():
            QMessageBox.warning(self, "No match selected", "Select a match first.")
            return
        
        idx = self.table.selectionModel().currentIndex()
        match_id = self.model._data[idx.row()].id
        
        with get_session() as s:
            events = s.exec(select(Event).where(Event.match_id == match_id)).all()
        
        if not events:
            QMessageBox.information(self, "Empty", "No events to export.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", f"{match_id}.csv", "CSV Files (*.csv)")
        if not path:
            return
        
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["frame","ts","piece","orientation","lines_cleared",
                             "combo","b2b","tspin","latency_ms"])
            for e in events:
                writer.writerow([e.frame, e.ts, e.piece, e.orientation,
                                 e.lines_cleared, e.combo,
                                 int(e.b2b), int(e.tspin), e.latency_ms])
        QMessageBox.information(self, "Exported", f"Saved to {path}")

    def _export_json(self):
        """Export selected match to JSON."""
        if not self.table.selectionModel().hasSelection():
            QMessageBox.warning(self, "No match selected", "Select a match first.")
            return
        
        idx = self.table.selectionModel().currentIndex()
        match_id = self.model._data[idx.row()].id
        
        with get_session() as s:
            events = s.exec(select(Event).where(Event.match_id == match_id)).all()
        
        if not events:
            QMessageBox.information(self, "Empty", "No events to export.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Save JSON", f"{match_id}.json", "JSON Files (*.json)")
        if not path:
            return
        
        data = [
            {
                "frame": e.frame,
                "ts": e.ts,
                "piece": e.piece,
                "orientation": e.orientation,
                "lines_cleared": e.lines_cleared,
                "combo": e.combo,
                "b2b": e.b2b,
                "tspin": e.tspin,
                "latency_ms": e.latency_ms
            }
            for e in events
        ]
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        QMessageBox.information(self, "Exported", f"Saved to {path}")

    def _refresh(self):
        """Refresh the match table."""
        self.model.refresh()


if __name__ == "__main__":
    # Initialize database
    init_db()
    
    app = QApplication(sys.argv)
    dashboard = StatsDashboard()
    dashboard.show()
    sys.exit(app.exec())
