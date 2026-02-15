# Cleanup Script - Run after Day 5

echo "Cleaning temporary files..."

# Remove temporary generated files
if exist "tools\board_sample.png" del "tools\board_sample.png"
if exist "src\models\tetris_perfect.onnx" del "src\models\tetris_perfect.onnx"

# Remove Python cache
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
for /r . %%f in (*.pyc) do @del "%%f"

echo "Cleanup complete!"
echo "Backup created at: tetris_again_backup_20250214"
echo "Project ready for next development phase."
