@echo off
cd /d "%~dp0"

echo YNB On Muhasebe Mobil - Desktop Test
echo ------------------------------------

py -3.11 -m venv .venv
call .venv\Scripts\activate

python -m pip install --upgrade pip setuptools wheel
python -m pip install kivy==2.3.1 filetype

python main.py

pause
