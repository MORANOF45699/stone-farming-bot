@echo off
chcp 65001 >nul
title Stone Bot - ติดตั้ง
cd /d "%~dp0"

echo =======================================================
echo    ติดตั้ง Stone Farming Bot
echo =======================================================
echo.

REM เช็คว่ามี Python ไหม
py --version >nul 2>&1
if %errorlevel%==0 (
    set PY=py
) else (
    python --version >nul 2>&1
    if %errorlevel%==0 (
        set PY=python
    ) else (
        echo [ผิดพลาด] ไม่พบ Python ในเครื่อง
        echo กรุณาติดตั้ง Python ก่อนที่ https://www.python.org/downloads/
        echo ตอนติดตั้งอย่าลืมติ๊ก "Add Python to PATH"
        echo.
        pause
        exit /b 1
    )
)

echo [1/2] พบ Python แล้ว กำลังอัปเดต pip...
%PY% -m pip install --upgrade pip

echo.
echo [2/2] กำลังติดตั้ง library ที่บอทใช้...
%PY% -m pip install -r requirements.txt

echo.
echo =======================================================
echo    ติดตั้งเสร็จแล้ว!
echo    ครั้งแรก: ดับเบิลคลิก calibrate.bat เพื่อจับพิกัด
echo    รันบอท:  ดับเบิลคลิก run.bat
echo =======================================================
echo.
pause
