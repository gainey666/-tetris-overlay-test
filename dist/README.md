# Tetris Overlay

A real-time Tetris assistance overlay with ghost pieces, combo tracking, and performance monitoring.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Windows (primary), Linux/macOS (experimental)

### Installation
```bash
# Clone the repository
git clone https://github.com/gainey666/-tetris-overlay-test.git
cd -tetris-overlay-test

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Overlay
```bash
python run_overlay_core.py
```

### First-Time Setup
1. **Calibrate ROIs**: Press `Ctrl+Alt+C` to open the ROI calibrator
2. **Configure Settings**: Press `F1` to open the settings dialog
3. **View Statistics**: Press `Ctrl+Alt+S` to open the stats dashboard

## 🎮 Features

### Real-time Ghost Pieces
- Shows where pieces will land
- Accurate tetromino shapes
- Customizable colors and opacity
- Special move indicators (T-Spin, B2B, Combo)

### Performance Monitoring
- FPS display with color coding
- Frame time monitoring
- Performance warnings

### Statistics Tracking
- Match history
- Piece distribution
- Combo tracking
- Export to CSV/JSON

### Customizable Settings
- Ghost piece appearance
- Hotkey configuration
- Visual flags (combo, B2B)
- ROI calibration

## ⌨️ Default Hotkeys

| Key | Function |
|-----|----------|
| `F9` | Toggle overlay visibility |
| `F1` | Open settings dialog |
| `Ctrl+Alt+S` | Open statistics dashboard |
| `Ctrl+Alt+C` | Open ROI calibrator |
| `F2` | Toggle debug logging |
| `Esc` | Quit application |

## 📊 Statistics

The overlay tracks:
- Matches played
- Pieces placed
- Combos achieved
- T-Spins performed
- Performance metrics

Access the statistics dashboard with `Ctrl+Alt+S` to view detailed analytics and export data.

## 🔧 Configuration

### Settings File
Settings are automatically saved to `settings.json` using TinyDB.

### ROI Calibration
1. Press `Ctrl+Alt+C` to open calibrator
2. Draw rectangles around:
   - Left game board
   - Right game board (if dual player)
   - Next piece queues
3. Save configuration

### Ghost Piece Customization
- **Color**: Use the color picker in settings
- **Opacity**: Adjust transparency slider
- **Live Preview**: See changes in real-time

## 🐛 Troubleshooting

### Overlay Not Showing
1. Ensure Tetris window is active
2. Check ROI calibration (`Ctrl+Alt+C`)
3. Verify overlay visibility (`F9`)

### Performance Issues
1. Check FPS display (top-right corner)
2. Reduce capture frequency in settings
3. Close unnecessary applications

### Settings Not Saving
1. Check file permissions
2. Verify `settings.json` exists
3. Use "Reset to Defaults" in settings

## 🧪 Testing

Run the test suite:
```bash
pytest tests/ -v
```

## 📁 Project Structure

```
├── run_overlay_core.py     # Main entry point
├── overlay_renderer.py     # Ghost piece rendering
├── ui/                     # Qt interfaces
│   ├── settings.py         # Settings data model
│   ├── settings_dialog.py  # Settings GUI
│   └── stats_dashboard.py  # Statistics GUI
├── stats/                  # Statistics system
│   ├── db.py              # Database schema
│   └── collector.py       # Data collection
└── tests/                  # Test suite
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Pygame for overlay rendering
- PySide6 for Qt interfaces
- TinyDB for settings persistence
- SQLModel for statistics storage
