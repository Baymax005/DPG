@echo off
echo Testing DPG Authentication...
cd /d "c:\Users\muham\OneDrive\Desktop\OTHER LANGS\DPG"
call venv\Scripts\activate.bat
timeout /t 2 /nobreak > nul
python test_register.py
pause
