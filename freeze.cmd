@echo off

set dest=".\dist\"

REM The below is an alternative to using a custom hook for praw
REM FOR /F "tokens=* USEBACKQ" %%F IN (`pipenv --venv`) DO (
    REM SET pipenvdir=%%F
REM )
REM --add-data "%pipenvdir%\Lib\site-packages\praw\praw.ini;site-packages\praw\praw.ini" ^

REM using the --noconfirm option sometimes causes issues when rebuilding
REM (ie when it tries to delete the previous dist directory)
pyinstaller ^
    --onefile ^
    --additional-hooks-dir .\pyinstaller-hooks\ ^
    PointsBot.py

copy ".\README.md" %dest%
copy ".\LICENSE.md" %dest%
copy ".\CHANGELOG.md" %dest%

mkdir .\releases\
powershell Compress-Archive -Force .\dist\* .\releases\PointsBot_Windows_x64.zip
