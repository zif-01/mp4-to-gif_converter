@echo off
setlocal enabledelayedexpansion

:: Определяем путь к папке скрипта
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo Установка Discord GIF Converter
echo Папка проекта: %CD%
echo.

:: Проверяем requirements.txt
if not exist "requirements.txt" (
    echo Создаю requirements.txt...
    echo numpy==1.24.3 > requirements.txt
    echo pillow==10.2.0 >> requirements.txt
    echo imageio==2.31.6 >> requirements.txt
    echo imageio-ffmpeg==0.4.9 >> requirements.txt
    echo tkinterdnd2==0.3.0 >> requirements.txt
)

echo [1/6] Создание виртуального окружения...
if exist "venv" (
    echo Папка venv уже существует
    echo Удалить и создать заново? (Y/N)
    set /p choice=
    if /i "!choice!"=="Y" (
        rmdir /s /q venv 2>nul
        python -m venv venv
        echo Создано новое окружение
    ) else (
        echo Используется существующее окружение
    )
) else (
    python -m venv venv
    echo Виртуальное окружение создано
)

echo.
echo [2/6] Активация окружения...
call venv\Scripts\activate.bat

echo.
echo [3/6] Установка зависимостей из requirements.txt...
echo.
type requirements.txt
echo.

:: Обновляем pip
python -m pip install --upgrade pip

:: Устанавливаем пакеты по одному с обработкой ошибок
set "PACKAGES_FILE=requirements.txt"
set "FAILED_PACKAGES="
set "SUCCESS_PACKAGES="

for /f "usebackq tokens=*" %%p in ("%PACKAGES_FILE%") do (
    echo.
    echo Устанавливаю: %%p
    python -m pip install %%p --no-warn-script-location
    
    if !errorlevel! equ 0 (
        echo ✅ Успешно: %%p
        set "SUCCESS_PACKAGES=!SUCCESS_PACKAGES! %%p"
    ) else (
        echo ❌ Ошибка при установке: %%p
        set "FAILED_PACKAGES=!FAILED_PACKAGES! %%p"
        
        :: Пробуем альтернативный способ для проблемных пакетов
        if "%%p"=="tkinterdnd2" (
            echo Пробую альтернативный источник для tkinterdnd2...
            python -m pip install tkinterdnd2 --no-deps --index-url https://pypi.org/simple/
            
            if !errorlevel! equ 0 (
                echo ✅ tkinterdnd2 установлен через альтернативный источник
                set "FAILED_PACKAGES=!FAILED_PACKAGES: tkinterdnd2=!"
                set "SUCCESS_PACKAGES=!SUCCESS_PACKAGES! tkinterdnd2"
            ) else (
                echo Пробую установить без зависимостей...
                python -m pip install tkinterdnd2 --no-deps
            )
        )
    )
)

echo.
echo [4/6] Установка дополнительных пакетов для совместимости...
:: Устанавливаем setuptools для tkinterdnd2
python -m pip install setuptools --upgrade
python -m pip install wheel

:: Пробуем еще раз установить неудавшиеся пакеты
if not "!FAILED_PACKAGES!"=="" (
    echo.
    echo Повторная попытка установки неудавшихся пакетов: !FAILED_PACKAGES!
    for %%p in (!FAILED_PACKAGES!) do (
        python -m pip install %%p --no-warn-script-location --force-reinstall
    )
)

echo.
echo [5/6] Создание ярлыков запуска...

:: Основной запускающий файл
echo @echo off > launch.bat
echo echo Discord GIF Converter >> launch.bat
echo echo ===================== >> launch.bat
echo cd /d "%%~dp0" >> launch.bat
echo call venv\Scripts\activate.bat >> launch.bat
echo python main.py >> launch.bat
echo if errorlevel 1 pause >> launch.bat

:: Быстрая конвертация
echo @echo off > convert.bat
echo echo Быстрая конвертация >> convert.bat
echo echo =================== >> convert.bat
echo cd /d "%%~dp0" >> convert.bat
echo call venv\Scripts\activate.bat >> convert.bat
echo python quick_convert.py %%* >> convert.bat
echo if errorlevel 1 pause >> convert.bat

echo.
echo [6/6] Проверка установки...

:: Создаем проверочный скрипт
echo import sys > check_install.py
echo import subprocess >> check_install.py
echo. >> check_install.py
echo print("=" * 50) >> check_install.py
echo print("Проверка установки Discord GIF Converter") >> check_install.py
echo print("=" * 50) >> check_install.py
echo. >> check_install.py

:: Проверяем каждый пакет
echo packages_to_check = ["numpy", "PIL", "imageio", "tkinterdnd2"] >> check_install.py
echo results = {} >> check_install.py
echo. >> check_install.py
echo for package in packages_to_check: >> check_install.py
echo     try: >> check_install.py
echo         if package == "PIL": >> check_install.py
echo             import PIL >> check_install.py
echo             version = PIL.__version__ >> check_install.py
echo         elif package == "tkinterdnd2": >> check_install.py
echo             import tkinterdnd2 >> check_install.py
echo             version = "0.3.0"  # У tkinterdnd2 может не быть __version__ >> check_install.py
echo         else: >> check_install.py
echo             exec(f"import {package}") >> check_install.py
echo             exec(f"version = {package}.__version__") >> check_install.py
echo         results[package] = ("✅", version) >> check_install.py
echo     except ImportError as e: >> check_install.py
echo         results[package] = ("❌", f"Не установлен: {e}") >> check_install.py
echo. >> check_install.py

echo print("\nРезультаты установки:") >> check_install.py
echo for package, (status, info) in results.items(): >> check_install.py
echo     print(f"{status} {package}: {info}") >> check_install.py
echo. >> check_install.py

:: Проверка FFmpeg
echo print("\nПроверка FFmpeg:") >> check_install.py
echo try: >> check_install.py
echo     result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True) >> check_install.py
echo     if result.returncode == 0: >> check_install.py
echo         print("✅ FFmpeg найден в системе") >> check_install.py
echo     else: >> check_install.py
echo         print("⚠️ FFmpeg не отвечает правильно") >> check_install.py
echo except FileNotFoundError: >> check_install.py
echo     print("❌ FFmpeg не найден! Установите FFmpeg из https://ffmpeg.org") >> check_install.py
echo. >> check_install.py

echo print("=" * 50) >> check_install.py
echo if all(status == "✅" for status, _ in results.values()): >> check_install.py
echo     print("✅ Все зависимости установлены успешно!") >> check_install.py
echo else: >> check_install.py
echo     print("⚠️ Некоторые зависимости не установлены") >> check_install.py
echo     print("   Попробуйте установить их вручную:") >> check_install.py
echo     print("   pip install неустановленный_пакет") >> check_install.py
echo print("=" * 50) >> check_install.py

python check_install.py
del check_install.py

echo.
echo ========================================
echo ИНСТРУКЦИЯ ПО УСТАНОВКЕ tkinterdnd2
echo ========================================
echo Если tkinterdnd2 не установился автоматически:
echo.
echo 1. Установите вручную:
echo    venv\Scripts\activate
echo    pip install tkinterdnd2
echo.
echo 2. Или используйте альтернативу:
echo    pip install tkinter-dnd
echo.
echo 3. Если не работает, можно отключить drag&drop:
echo    - Отредактируйте gui_converter.py
echo    - Удалите импорт tkinterdnd2
echo    - Удалите все вызовы drop функций
echo ========================================
echo.
echo Файлы для запуска:
echo - launch.bat   - Графический интерфейс
echo - convert.bat  - Быстрая конвертация
echo.
echo Папка проекта: %CD%
echo.
pause