@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\pythonw.exe" (
  start "Office Twin" ".venv\Scripts\pythonw.exe" -m office_twin
) else (
  python -m office_twin
)
