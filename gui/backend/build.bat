@echo off
REM build.bat - Empaquetar como .exe

echo.
echo === Building BrokenLinkCrawler ===
echo.

REM Verifica que PyInstaller esté instalado
..\..\.venv\Scripts\pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    ..\..\.venv\Scripts\pip install pyinstaller
)

REM Ejecuta PyInstaller con el spec
echo Building executable...
..\..\.venv\Scripts\pyinstaller build.spec --distpath dist

if errorlevel 0 (
    echo.
    echo ✅ Build successful!
    echo 📁 Executable: dist\BrokenLinkCrawler\BrokenLinkCrawler.exe
    echo.
) else (
    echo ❌ Build failed
    exit /b 1
)

pause