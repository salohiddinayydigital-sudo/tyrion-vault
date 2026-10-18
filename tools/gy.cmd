@echo off
setlocal EnableExtensions
chcp 65001 >nul

rem ============================================================================
rem  gy.cmd — Tyrion bilim grafi (Graphify wrapper, portativ v4.0)
rem  Har qanday papkadan ishlaydi (%~dp0.. orqali ildizni avtomatik topadi).
rem
rem  Ishlatish:
rem    tools\gy.cmd query "learning phase qoidalari" --budget 1200
rem    tools\gy.cmd god-nodes --top 10
rem    tools\gy.cmd explain "Kreativ va avtonom sikl"
rem    tools\gy.cmd status
rem    tools\gy.cmd build
rem ============================================================================

for %%I in ("%~dp0..") do set "GY_ROOT=%%~fI"
set "GY_GRAPH=%GY_ROOT%\graphify-out\graph.json"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

if "%~1"=="" goto :usage
if /I "%~1"=="help" goto :usage
if /I "%~1"=="--help" goto :usage
if /I "%~1"=="-h" goto :usage
if /I "%~1"=="status" goto :status
if /I "%~1"=="build" goto :build

if not exist "%GY_GRAPH%" (
    py -3 "%GY_ROOT%\tools\brain-graph.py" build --report
)

py -3 "%GY_ROOT%\tools\brain-search.py" search "%~2" --top 5
exit /b %ERRORLEVEL%

:build
py -3 "%GY_ROOT%\tools\brain-graph.py" build --report
exit /b %ERRORLEVEL%

:status
py -3 "%GY_ROOT%\tools\brain-graph.py" stats
exit /b %ERRORLEVEL%

:usage
echo Foydalanish:
echo   tools\gy.cmd build
echo   tools\gy.cmd status
echo   tools\gy.cmd query "<savol>"
exit /b 0
