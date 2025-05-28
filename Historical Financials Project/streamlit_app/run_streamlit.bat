@echo off
REM -------------------------------
REM 1. Jump into this script’s folder
cd /d "%~dp0"
REM -------------------------------
REM 2. Activate your venv (if you named it "venv")
call ..\venv\Scripts\activate.bat
REM -------------------------------
REM 3. Run Streamlit via Python
py -m streamlit run app.py
REM -------------------------------
pause
