@echo off
REM Martin Setup Script for Windows
REM This script sets up the development environment using uv (preferred) or venv

echo Setting up Martin development environment...

REM Check if uv is available
where uv >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo Using uv for dependency management...
    
    REM Create virtual environment with uv
    uv venv
    
    REM Activate virtual environment
    call .venv\Scripts\activate.bat
    
    REM Install dependencies with uv
    uv pip install -e ".[dev]"
    
    echo ✅ Environment setup complete with uv!
    echo To activate the environment, run:
    echo   .venv\Scripts\activate.bat
    
) else (
    REM Check if python is available
    where python >nul 2>nul
    if %ERRORLEVEL% == 0 (
        echo uv not found, using venv...
        
        REM Create virtual environment with venv
        python -m venv .venv
        
        REM Activate virtual environment
        call .venv\Scripts\activate.bat
        
        REM Upgrade pip
        pip install --upgrade pip
        
        REM Install dependencies
        pip install -e ".[dev]"
        
        echo ✅ Environment setup complete with venv!
        echo To activate the environment, run:
        echo   .venv\Scripts\activate.bat
        
    ) else (
        echo ❌ Neither uv nor python found. Please install Python 3.8+ or uv.
        exit /b 1
    )
)

echo.
echo Next steps:
echo 1. Copy .env.example to .env and add your OpenAI API key
echo 2. Run: martin "https://arxiv.org/pdf/1706.03762.pdf"