@echo off
REM Script pour redémarrer le backend FastAPI

echo Arret des processus Python en cours...
taskkill /F /IM python.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul

echo Demarrage du backend FastAPI...
start "Backend FastAPI" python main.py

timeout /t 3 /nobreak >nul
echo.
echo Backend redémarre sur http://localhost:8000
echo.
