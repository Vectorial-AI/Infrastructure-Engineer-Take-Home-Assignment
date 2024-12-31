@echo off

:: Clean and create package directory
if exist package rmdir /s /q package
mkdir package

:: Install dependencies
pip install --platform manylinux2014_x86_64 --implementation cp --python-version 3.12 --only-binary=:all: --target ./package -r requirements.txt

:: Copy Lambda function code
copy *.py package\

:: Create ZIP file (using 7-Zip if available, otherwise use PowerShell)
where 7z >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    7z a -tzip lambda_function.zip ./package/*
) else (
    powershell -command "Add-Type -Assembly 'System.IO.Compression.FileSystem'; [System.IO.Compression.ZipFile]::CreateFromDirectory('package', 'lambda_function.zip')"
)

:: Clean up
rmdir /s /q package 