@echo off
echo =================================
echo Starting Emergency Card Frontend
echo =================================
echo.
echo Open your browser: http://localhost:3000
echo.
cd frontend
python -m http.server 3000
pause
