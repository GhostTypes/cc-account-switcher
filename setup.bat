@echo off
REM Setup script for Claude Code Account Switcher on Windows

set EXEC_NAME=ccswitch.exe
set USER_PROFILE=%USERPROFILE%
set INSTALL_DIR=%USER_PROFILE%\claude-switcher

REM Create the installation directory if it doesn't exist
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy the executable to the installation directory
copy "dist\%EXEC_NAME%" "%INSTALL_DIR%\%EXEC_NAME%"

echo Setup completed!
echo The executable is located at: %INSTALL_DIR%\%EXEC_NAME%
echo.
echo To use ccswitch from any command prompt, add this directory to your PATH:
echo.
echo Method 1 - Command line (temporary for current session):
echo   set PATH=%%PATH%%;%INSTALL_DIR%
echo.
echo Method 2 - Permanently via System Properties:
echo   1. Press Windows + R, type 'sysdm.cpl', press Enter
echo   2. Click on 'Environment Variables' button
echo   3. Under 'System Variables', find and select 'Path', click 'Edit'
echo   4. Click 'New' and add: %INSTALL_DIR%
echo   5. Click 'OK' on all dialogs to save
echo.
echo After adding to PATH, you can run 'ccswitch' from any command prompt.
echo.
echo To use without adding to PATH, run: "%INSTALL_DIR%\%EXEC_NAME%" [options]

pause