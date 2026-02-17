# Tetris Overlay

A production-ready, real-time Tetris assistance overlay with ghost pieces, combo tracking, performance monitoring, and comprehensive statistics.

## 🎯 Features

### 🎮 Core Overlay
- **30 FPS Real-time Rendering** - Smooth ghost piece display
- **Accurate Tetromino Shapes** - All 7 pieces with proper rotations
- **Visual Effects** - Configurable ghost opacity, outline modes, animations
- **Special Move Indicators** - T-Spin, B2B, and combo visual badges
- **Performance Monitoring** - FPS counter and frame time display

### 🖥️ Professional GUI
- **Settings Dialog** - Tabbed interface with live preview
- **Statistics Dashboard** - Rich charts, filtering, and export functionality
- **Hotkey Management** - Dynamic hotkey registration and editing
- **Visual Flags** - Toggle combo, B2B, FPS indicators

### 📊 Statistics & Analytics
- **Frame-by-Frame Tracking** - Complete match recording
- **SQLite Database** - Persistent statistics storage
- **Rich Dashboard** - Score trends, piece distribution, performance metrics
- **Export Functionality** - CSV/JSON export with filtering
- **Match History** - Sortable table with detailed metrics

### 🛠️ Developer Tools
- **Comprehensive Testing** - Unit, integration, UI, and performance tests
- **CI/CD Pipeline** - Automated testing, building, and releases
- **Cross-Platform Support** - Windows, macOS, Linux
- **Docker Support** - Containerized deployment
- **Plugin Architecture** - Extensible prediction agents

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ (3.13 recommended)
- Windows (primary), Linux/macOS (experimental)
- 4GB RAM minimum
- DirectX/OpenGL support

### Installation

#### Option 1: Download Executable (Recommended)
1. Visit [Releases](https://github.com/gainey666/-tetris-overlay-test/releases)
2. Download the appropriate executable for your platform
3. Run the installer and launch the application

#### Option 2: Python Package
```bash
pip install tetris-overlay
tetris-overlay
```

#### Option 3: Development Setup
```bash
# Clone the repository
git clone https://github.com/gainey666/-tetris-overlay-test.git
cd -tetris-overlay-test

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the overlay
python run_overlay_core.py
```

## 📡 Optional – Tracer (live function-call view)

The overlay ships with a lightweight tracer that shows a live table of every
function decorated with `@trace_calls`. It is **optional** – if the tracer package
is not installed, the decorators automatically fall back to no-ops and the
overlay continues to run normally.

### Install the tracer (optional)

```bash
# From the repository root
pip install -e ./tracer
```

### Run the tracer UI

```bash
python -m tracer.server
```

Leave the UI running in a separate terminal, then start any overlay entry point
(`python run_overlay_core.py`, `python run_simple_working_overlay.py`, etc.). You’ll
see entries such as:

```
S run_simple_working_overlay : main
S run_overlay_core           : _frame_worker
F piece_detector             : get_current_piece
```

If you skip the optional install, `@trace_calls` simply does nothing, so there
is no runtime overhead.

### Docker Installation
```bash
docker pull gainey666/tetris-overlay:latest
docker run -it --rm gainey666/tetris-overlay:latest
```

## 🎮 Usage

### First-Time Setup
1. **Launch the Application** - Start `tetris-overlay.exe` or run `python run_overlay_core.py`
2. **Calibrate ROIs** - Press `F6` to open the ROI calibrator
3. **Configure Settings** - Press `F8` to open the settings dialog
4. **Start Playing** - The overlay will automatically detect your Tetris game

### Default Hotkeys
| Hotkey | Action |
|--------|--------|
| `F9` | Toggle overlay visibility |
| `F8` | Open settings dialog |
| `F7` | Open statistics dashboard |
| `F6` | Calibrate ROIs |
| `F5` | Toggle debug logging |
| `Esc` | Quit application |

### Settings Configuration

#### General Tab
- **ROI Configuration** - Set game window regions
- **Prediction Agent** - Choose AI algorithm (Dellacherie/Bertilsson)

#### Ghost Tab
- **Color Picker** - Choose ghost piece color
- **Opacity Slider** - Adjust transparency (0-100%)
- **Visual Effects** - Outline mode, fade animations

#### Hotkeys Tab
- **Dynamic Editing** - Click to change any hotkey
- **Reset to Defaults** - Restore default hotkey bindings

#### Visual Flags Tab
- **Combo Indicator** - Show/hide combo counter
- **B2B Indicator** - Show/hide back-to-back indicator
- **FPS Counter** - Show/hide performance display
- **Debug Mode** - Enable detailed logging

#### Advanced Tab
- **Target FPS** - Set frame rate (10-60 FPS)
- **Frame Timeout** - Adjust processing timeout
- **Validation Status** - Check configuration errors

### Statistics Dashboard

#### Match History
- **Sortable Table** - Sort by any column
- **Match Details** - Duration, frames, pieces, combos
- **Performance Metrics** - Average FPS, B2B count

#### Analytics Charts
- **Score Progression** - Track score over time
- **Combo Distribution** - Histogram of max combos
- **Piece Distribution** - Frequency of each tetromino
- **Performance Trends** - FPS and frame time analysis

#### Export Features
- **Date Range Filtering** - Export specific time periods
- **Format Options** - JSON or CSV export
- **Preview Function** - Review data before export

## 🔧 Advanced Configuration

### Configuration Files
- `settings.json` - User preferences and ROI data
- `calibration.json` - Screen calibration settings
- `feature_toggles.json` - Feature enable/disable flags
- `stats.db` - SQLite statistics database

### Environment Variables
```bash
TETRIS_OVERLAY_LOG_LEVEL=INFO
TETRIS_OVERLAY_CONFIG_DIR=/path/to/config
TETRIS_OVERLAY_DATA_DIR=/path/to/data
```

### Custom Prediction Agents
Create a new agent by implementing the `BaseAgent` interface:

```python
from prediction_agents.base import BaseAgent

class CustomAgent(BaseAgent):
    def predict(self, board, piece, next_queue):
        # Your prediction logic here
        return best_position, best_rotation
```

## 🧪 Testing

### Running Tests
```bash
# Unit tests
pytest tests/test_tetromino_shapes.py -v

# Integration tests
pytest tests/test_integration.py -v

# Performance benchmark
python tests/benchmark_frame_time.py --frames 500 --fps 30

# UI tests (requires display)
xvfb-run -a pytest tests/test_ui.py -v
```

### Coverage Report
```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

## 📦 Building from Source

### Prerequisites
- Python 3.11+
- PyInstaller
- Platform-specific build tools

### Build Executable
```bash
# Install build dependencies
pip install pyinstaller

# Build for current platform
pyinstaller --onefile --windowed --name tetris-overlay run_overlay_core.py

# Cross-platform builds (Docker)
docker build -t tetris-overlay-builder .
docker run --rm -v $(pwd):/output tetris-overlay-builder
```

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run linting
ruff check .
black --check .
mypy .

# Run full test suite
pytest
```

## 🐛 Troubleshooting

### Common Issues

#### Overlay Not Visible
1. Check if overlay is toggled on (F9)
2. Verify ROI calibration (F6)
3. Ensure game window is detected
4. Check display scaling settings

#### Poor Performance
1. Lower target FPS in settings
2. Disable visual effects
3. Close other applications
4. Update graphics drivers

#### Statistics Not Recording
1. Check if match is active
2. Verify database permissions
3. Reset statistics database
4. Check for error messages

#### Hotkeys Not Working
1. Check for conflicting applications
2. Reset to default hotkeys
3. Run as administrator
4. Check keyboard settings

### Debug Mode
Enable debug mode for detailed logging:
1. Open settings (F8)
2. Go to Visual Flags tab
3. Enable "Debug Mode"
4. Check logs in console

### Log Files
- Windows: `%APPDATA%/tetris-overlay/logs/`
- Linux: `~/.local/share/tetris-overlay/logs/`
- macOS: `~/Library/Logs/tetris-overlay/`

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Style
- Use `black` for formatting
- Follow PEP 8 guidelines
- Add type hints
- Include docstrings
- Write comprehensive tests

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Tetris Guideline** - Official Tetris standards
- **Pygame Community** - Graphics and input handling
- **PySide6** - Qt GUI framework
- **SQLModel** - Database ORM
- **Matplotlib** - Chart visualization

## 📞 Support

- **Documentation**: [Wiki](https://github.com/gainey666/-tetris-overlay-test/wiki)
- **Issues**: [GitHub Issues](https://github.com/gainey666/-tetris-overlay-test/issues)
- **Discussions**: [GitHub Discussions](https://github.com/gainey666/-tetris-overlay-test/discussions)
- **Email**: support@tetris-overlay.com

## 🗺️ Roadmap

### Version 2.1 (In Progress)
- [ ] Multi-screen support
- [ ] Advanced calibration UI
- [ ] Plugin marketplace
- [ ] Web dashboard

### Version 2.2 (Planned)
- [ ] AI training pipeline
- [ ] OBS integration
- [ ] Mobile companion app
- [ ] Cloud sync

### Version 3.0 (Future)
- [ ] Multi-player support
- [ ] Real-time collaboration
- [ ] Advanced analytics
- [ ] Professional esports features

---

**🎮 Happy Tetris playing! May your combos be many and your clears be perfect!**

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
