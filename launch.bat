@echo off 
echo Discord GIF Converter 
echo ===================== 
cd /d "%~dp0" 
call venv\Scripts\activate.bat 
python main.py 
if errorlevel 1 pause 
