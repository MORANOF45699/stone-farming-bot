@echo off
chcp 65001 >nul
title Stone Farming Bot
cd /d "%~dp0"

REM ===== ต้องรันด้วยสิทธิ์ Administrator (ไม่งั้นส่งปุ่มเข้าเกมไม่ได้) =====
net session >nul 2>&1
if not %errorlevel%==0 (
    echo กำลังขอสิทธิ์ Administrator...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

REM หา Python
py --version >nul 2>&1
if %errorlevel%==0 (set PY=py) else (set PY=python)

%PY% stone_main.py

echo.
echo (บอทปิดแล้ว) กดปุ่มใดก็ได้เพื่อปิดหน้าต่าง
pause >nul
