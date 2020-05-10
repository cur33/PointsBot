@echo off

REM FOR /F "tokens=* USEBACKQ" %%F IN (`pipenv --venv`) DO (
    REM SET pipenvdir=%%F
REM )

REM --add-data "%pipenvdir%\Lib\site-packages\praw\praw.ini;site-packages\praw\praw.ini" ^

REM --noconfirm ^
pyinstaller ^
    --onedir ^
    --additional-hooks-dir .\pyinstaller-hooks\ ^
    PointsBot.py
