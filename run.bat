@echo off
rem Add native dll folder to PATH
set "BIN=%~dp0vcpkg\installed\x64-windows\bin"
set "PATH=%BIN%;%PATH%"

rem Launch Python (assumes virtualenv in .venv)
call .venv\Scripts\activate.bat
python -m src.main -p orchestration_plan.yaml
