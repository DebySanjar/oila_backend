@echo off
echo ========================================
echo   Oila Backend Server
echo ========================================
echo.
echo Server ishga tushmoqda...
echo Emulator uchun: http://10.0.2.2:8000
echo Browser uchun: http://127.0.0.1:8000
echo.
python manage.py runserver 0.0.0.0:8000
