@echo off

timeout 2 >nul
del "%~dp0ThanosCleaner.exe" >nul
move "C:\Temp\ThanosCleaner.exe" "%~dp0ThanosCleaner.exe" >nul
del /q "C:\Temp" >nul
start /d "%~dp0" ThanosCleaner.exe >nul