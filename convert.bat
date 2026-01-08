@echo off 
echo Быстрая конвертация 
echo =================== 
cd /d "%~dp0" 
call venv\Scripts\activate.bat 
python quick_convert.py %* 
if errorlevel 1 pause 
