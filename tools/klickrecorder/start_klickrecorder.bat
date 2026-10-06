@echo off
rem Klickrecorder starten (braucht uv: https://docs.astral.sh/uv/)
cd /d "%~dp0"
where uv >nul 2>nul || (
  echo uv fehlt. Einmalig installieren mit:
  echo   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  pause
  exit /b 1
)
set /p NAME=Name der Aufnahme (z.B. P1_Material):
uv run klickrecorder.py %NAME%
pause
