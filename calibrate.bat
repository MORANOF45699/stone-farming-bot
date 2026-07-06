@echo off
chcp 65001 >nul
title Stone Bot - Calibrate (จับพิกัด/template)
cd /d "%~dp0"

REM ===== ต้องรันด้วยสิทธิ์ Administrator =====
net session >nul 2>&1
if not %errorlevel%==0 (
    echo กำลังขอสิทธิ์ Administrator...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

py --version >nul 2>&1
if %errorlevel%==0 (set PY=py) else (set PY=python)

echo =======================================================
echo    Calibrate - จับพิกัดและ template ของจอคุณ
echo    เปิดเกมค้างไว้ แล้วทำตามที่โปรแกรมบอก
echo    (สลับหน้าต่างไปเกม แล้วกดปุ่มตัวเลข 1-7, กด 0 เพื่อจบ)
echo =======================================================
echo.

%PY% calibrate.py

echo.
pause
