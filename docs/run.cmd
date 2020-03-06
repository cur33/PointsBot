@echo off

REM wsl run.sh
REM start "" chrome.exe TODO.html

REM pandoc.exe -s -f gfm -t html TODO.md -o TODO.html --metadata pagetitle="TODO.html"
REM  .\TODO.html

call :makedoc DONE
call :makedoc IDEAS
call :makedoc TODO
call :makedoc TESTS
goto :eof

:makedoc
pandoc.exe -s -f gfm -t html %1.md -o %1.html --metadata pagetitle="%1.html"
goto :eof
