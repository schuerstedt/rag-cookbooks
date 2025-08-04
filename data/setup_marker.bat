@echo off
REM Setup script for Marker with Python 3.11

echo 🚀 Setting up Marker PDF Converter...

REM Check if conda is available
where conda >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Conda found - creating Python 3.11 environment
    conda create -n marker python=3.11 -y
    call conda activate marker
    pip install marker-pdf
    echo ✅ Marker installed in conda environment 'marker'
    echo 💡 To use: conda activate marker && marker_single your_file.pdf
) else (
    echo ❌ Conda not found
    echo 💡 Please install Miniconda or Anaconda first
    echo 📥 Download from: https://docs.conda.io/en/latest/miniconda.html
)

pause
