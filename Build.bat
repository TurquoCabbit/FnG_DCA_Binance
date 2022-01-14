pyinstaller -F main.py
copy /Y dist\main.exe output\main.exe
rem copy /Y dist\main.exe ..\main.exe
call Clean.bat
git add --all
git status
pause