@echo off
setlocal
chcp 65001 >nul
title QUAN SUPER IQAMDAU BUILD
pushd "%~dp0"

echo ========================================
echo       QUAN SUPER IQAMDAU - BUILD v2.0
echo ========================================
echo.

if not exist "quan_super_iqamdau.py" (
  echo [ҚАТЕ]: quan_super_iqamdau.py файлы бұл бумадан табылмады.
  echo BAT файлы мен PY файлын бір папкада сақтаңыз.
  pause
  popd
  exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
  echo [ҚАТЕ]: Python табылмады. Python орнатып, "Add Python to PATH" қосуды ұмытпаңыз.
  pause
  popd
  exit /b 1
)

echo [1/4] PyInstaller тексерілуде және жаңартылуда...
python -m pip install --upgrade pyinstaller
if errorlevel 1 (
  echo [ҚАТЕ]: PyInstaller орнату/жаңарту сәтсіз аяқталды.
  pause
  popd
  exit /b 1
)

echo [2/4] Ескі құрастыру қалдықтары тазартылуда...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist QuanSuperIqamdau.spec del /q QuanSuperIqamdau.spec

echo [3/4] EXE файлы құрастырылуда (PyInstaller)...
if exist icon.ico (
  python -m PyInstaller --noconfirm --clean --onefile --windowed --icon=icon.ico --name QuanSuperIqamdau quan_super_iqamdau.py
) else (
  python -m PyInstaller --noconfirm --clean --onefile --windowed --name QuanSuperIqamdau quan_super_iqamdau.py
)

if errorlevel 1 (
  echo [ҚАТЕ]: Құрастыру сәтсіз аяқталды. Жоғарыдағы қате мәтінін қараңыз.
  pause
  popd
  exit /b 1
)

echo [4/4] Уақытша файлдар тазартылуда...
if exist QuanSuperIqamdau.spec del /q QuanSuperIqamdau.spec

echo.
echo ========================================
echo       ҚҰРАСТЫРУ СӘТТІ АЯҚТАЛДЫ!
echo ========================================
echo EXE орналасқан жері: "%CD%\dist\QuanSuperIqamdau.exe"
echo.
pause
popd
endlocal