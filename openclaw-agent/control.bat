@echo off
chcp 65001 >nul
REM OpenClaw Agent Control Script for Windows

set AGENT_DIR=%~dp0
set PYTHON=%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe

if not exist %PYTHON% (
    echo Python non trouve. Installe Python 3.11+
    exit /b 1
)

echo ========================================
echo OpenClaw Agent Controller
echo ========================================
echo.

if "%~1"=="" goto :menu

goto :%1 2>nul || goto :menu

:menu
echo Commandes disponibles:
echo   start    - Demarre l'agent
echo   stop     - Arrete l'agent
echo   status   - Verifie le statut
echo   init     - Initialise la configuration
echo   n8n      - Gestion n8n
echo   logs     - Affiche les logs
echo.
set /p CMD="Que veux-tu faire ? "
goto :%CMD% 2>nul || (echo Commande inconnue && goto :menu)

:start
echo Demarrage de l'agent...
start /b %PYTHON% "%AGENT_DIR%\agent.py" start > "%AGENT_DIR%\agent.log" 2>&1
echo Agent demarre en arriere-plan.
echo Logs: %AGENT_DIR%\agent.log
goto :end

:stop
echo Arret de l'agent...
taskkill /f /im python.exe 2>nul
echo Agent arrete.
goto :end

:status
echo Verification du statut...
tasklist | findstr python.exe >nul && echo Agent: ACTIF || echo Agent: INACTIF
echo.
docker ps --format "table {{.Names}}\t{{.Status}}" 2>nul | findstr n8n >nul && echo n8n: OK || echo n8n: ARRETE
goto :end

:init
echo Initialisation...
%PYTHON% "%AGENT_DIR%\agent.py" init
echo Configuration creee.
goto :end

:n8n
cls
echo ========================================
echo Gestion n8n
echo ========================================
echo.
echo 1. Demarrer n8n
echo 2. Arreter n8n
echo 3. Redemarrer n8n
echo 4. Voir les logs n8n
echo 5. Retour
echo.
set /p choice="Choix: "
if "%choice%"=="1" goto :n8n_start
if "%choice%"=="2" goto :n8n_stop
if "%choice%"=="3" goto :n8n_restart
if "%choice%"=="4" goto :n8n_logs
if "%choice%"=="5" goto :menu

:n8n_start
docker run -d --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n 2>nul || docker start n8n
echo n8n demarre sur http://localhost:5678
pause
goto :n8n

:n8n_stop
docker stop n8n
echo n8n arrete.
pause
goto :n8n

:n8n_restart
docker restart n8n
echo n8n redemarre.
pause
goto :n8n

:n8n_logs
docker logs n8n -f --tail 50
goto :n8n

:logs
type "%AGENT_DIR%\agent.log" | more
goto :end

:end
echo.
pause
