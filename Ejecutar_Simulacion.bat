@echo off
REM ============================================================
REM  EvoLLM — Lanzador de Interfaz Grafica
REM  Doble clic para iniciar. Cierra esta ventana para detener.
REM ============================================================
cd /d "%~dp0"
set PYTHONPATH=%~dp0src

echo Verificando dependencias...
python -c "import streamlit" 2>nul
IF ERRORLEVEL 1 (
    echo Instalando Streamlit y Plotly (solo la primera vez)...
    pip install streamlit plotly
    IF ERRORLEVEL 1 (
        echo ERROR: No se pudo instalar Streamlit.
        echo Asegurate de tener Python y pip instalados correctamente.
        pause
        exit /b 1
    )
)

echo.
echo  =============================================
echo   EvoLLM -- Simulador del Dilema del Prisionero
echo  =============================================
echo.
echo  Abriendo la interfaz en tu navegador...
echo  URL: http://localhost:8501
echo.
echo  Para DETENER la aplicacion, cierra esta ventana
echo  o presiona Ctrl+C aqui.
echo  =============================================
echo.

streamlit run "%~dp0gui.py" --server.headless false --browser.gatherUsageStats false

pause
