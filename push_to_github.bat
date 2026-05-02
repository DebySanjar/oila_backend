@echo off
echo ========================================
echo   GitHub ga yuklash
echo ========================================
echo.
echo Git init...
git init
echo.
echo Files qo'shish...
git add .
echo.
echo Commit...
git commit -m "Initial commit - Oila Backend"
echo.
echo DIQQAT: GitHub repository URL ni kiriting
echo Masalan: https://github.com/yourusername/oila_backend.git
echo.
set /p REPO_URL="Repository URL: "
echo.
echo Remote qo'shish...
git remote add origin %REPO_URL%
echo.
echo Push qilish...
git branch -M main
git push -u origin main
echo.
echo ========================================
echo   TAYYOR! GitHub ga yuklandi!
echo ========================================
pause
