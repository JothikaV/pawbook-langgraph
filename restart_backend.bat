@echo off
REM Kill all Python processes
echo Killing existing Python processes...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak

REM Start backend
echo Starting PawBook backend...
cd python_backend
python run.py
