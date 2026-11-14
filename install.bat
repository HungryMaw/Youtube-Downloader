@echo off
setlocal enabledelayedexpansion

:: 1. Setup Directories and Paths
set "DIR=%~dp0"
if "%DIR:~-1%"=="\" set "DIR=%DIR:~0,-1%"
set "VENV_DIR=%DIR%\.venv"
set "EXE_DEST=%USERPROFILE%\Desktop\Youtube Downloader.exe"
set "REQ_FILE=%DIR%\src\requirements.txt"

:: 2. Create Virtual Environment
if not exist "%VENV_DIR%" (
    echo Creating virtual environment
    python -m venv "%VENV_DIR%"
)

:: 3. Activate Virtual Environment
call "%VENV_DIR%\Scripts\activate.bat"
echo Virtual Environment is activated
echo.

:: 4. Install Packages
echo Downloading packages
set "PYTHON_BIN=%VENV_DIR%\Scripts\python.exe"

"%PYTHON_BIN%" -m pip install --upgrade pip

if exist "%REQ_FILE%" (
    echo Installing from requirements.txt
    "%PYTHON_BIN%" -m pip install -r "%REQ_FILE%"
) else (
    echo ERROR: %REQ_FILE% not found!
    pause
    exit /b 1
)
echo.

:: 5. Verify Packages
echo Verifying Python packages
set "MISSING_PKGS="

"%PYTHON_BIN%" -c "import customtkinter" >nul 2>&1 || set "MISSING_PKGS=!MISSING_PKGS! customtkinter"
"%PYTHON_BIN%" -c "import imageio_ffmpeg" >nul 2>&1 || set "MISSING_PKGS=!MISSING_PKGS! imageio_ffmpeg"
"%PYTHON_BIN%" -c "import PyQt5" >nul 2>&1 || set "MISSING_PKGS=!MISSING_PKGS! PyQt5"
"%PYTHON_BIN%" -c "import pyautogui" >nul 2>&1 || set "MISSING_PKGS=!MISSING_PKGS! pyautogui"
"%PYTHON_BIN%" -c "import yt_dlp" >nul 2>&1 || set "MISSING_PKGS=!MISSING_PKGS! yt_dlp"

if not "!MISSING_PKGS!"=="" (
    echo Error: The following Python packages failed to install:
    for %%p in (!MISSING_PKGS!) do echo   - %%p
    pause
    exit /b 1
)
echo All Python packages are successfully installed
echo.

:: 6. Compile to EXE using PyInstaller
echo Installing An Exe File
echo.

if exist "%EXE_DEST%" (
    echo An Executable file is already downloaded! path: %EXE_DEST%
    echo If you want to recompile, delete the Desktop EXE first.
    goto :done
)

echo Installing PyInstaller
"%PYTHON_BIN%" -m pip install pyinstaller

cd /d "%DIR%"
echo Compiling executable. This may take a few minutes.

"%PYTHON_BIN%" -m PyInstaller --noconsole --onefile --icon="%DIR%\src\icon.ico" --add-data "%DIR%\src\icon.png;." --add-data "%DIR%\src\icon.ico;." --collect-all customtkinter --collect-all pyautogui "%DIR%\src\downloader.py"

if !errorlevel! neq 0 (
    echo.
    echo ERROR: Compilation failed! Read the error above.
    pause
    exit /b 1
)

if exist "%DIR%\dist\downloader.exe" (
    move /Y "%DIR%\dist\downloader.exe" "%EXE_DEST%"
    echo %EXE_DEST% was Installed!
    rmdir /S /Q "%DIR%\build"
    rmdir /S /Q "%DIR%\dist"
    del /Q "%DIR%\downloader.spec"
) else (
    echo ERROR: Could not find the compiled .exe in the dist folder!
    pause
    exit /b 1
)

:done
echo.
echo The Youtube Downloader was installed, enjoy!
pause
exit /b 0