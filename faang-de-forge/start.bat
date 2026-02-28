@echo off
title DE Forge — FAANG Prep Platform
echo.
echo  ===================================================
echo   DE Forge — FAANG Data Engineering Prep Platform
echo  ===================================================
echo.
echo  Starting local server...
echo  Open your browser at: http://localhost:8000
echo.
echo  Press Ctrl+C to stop the server.
echo  ===================================================
echo.
start "" "http://localhost:8000"
python -m http.server 8000
