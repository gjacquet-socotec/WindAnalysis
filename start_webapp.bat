@echo off
REM Script pour lancer l'application web Wind Turbine Analytics
REM Backend (FastAPI) + Frontend (Vite)

echo ============================================================
echo Wind Turbine Analytics - Application Web
echo ============================================================
echo.

REM Lancer le backend FastAPI dans une nouvelle fenêtre
echo [1/2] Demarrage du backend FastAPI (http://localhost:8000)...
start "Backend FastAPI" cmd /k "python main.py"

REM Attendre que le backend soit prêt
timeout /t 5 /nobreak >nul

REM Lancer le frontend Vite dans une nouvelle fenêtre
echo [2/2] Demarrage du frontend Vite (http://localhost:5173)...
cd frontend
start "Frontend Vite" cmd /k "npm run dev"
cd ..

echo.
echo ============================================================
echo Application lancee !
echo ============================================================
echo.
echo - Backend API:  http://localhost:8000
echo - Documentation: http://localhost:8000/docs
echo - Frontend:     http://localhost:5173
echo.
echo Appuyez sur une touche pour ouvrir le navigateur...
pause >nul

REM Ouvrir le navigateur
start http://localhost:5173
