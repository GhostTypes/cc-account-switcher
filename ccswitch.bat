@echo off
REM Wrapper script for Claude Code Account Switcher
REM This allows you to run ccswitch from anywhere after adding to PATH

set EXEC_PATH=%~dp0dist\ccswitch.exe

REM Pass all arguments to the executable
"%EXEC_PATH%" %*