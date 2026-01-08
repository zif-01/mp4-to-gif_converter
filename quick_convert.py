#!/usr/bin/env python3
"""
Простой скрипт для быстрой конвертации MP4 в GIF для Discord
"""

import os
import sys
from discord_gif_converter import DiscordGIFConverter

def quick_convert():
    """Интерактивная конвертация"""
    print("🚀 Быстрая конвертация MP4 в GIF для Discord")
    print("=" * 40)
    
    try:
        # Ввод файла
        while True:
            input_file = input("\nВведите путь к MP4 файлу (или 'exit' для выхода): ").strip()
            
            if input_file.lower() == 'exit':
                return
            
            if not input_file:
                print("❌ Пожалуйста, введите путь к файлу")
                continue
            
            if not os.path.exists(input_file):
                print("❌ Файл не найден!")
                continue
            
            if not input_file.lower().endswith('.mp4'):
                print("❌ Файл должен быть в формате MP4")
                continue
            
            break
        
        # Выбор уровня оптимизации
        print("\n📊 Уровень оптимизации:")
        print("1. Максимальное качество (больший размер)")
        print("2. Сбалансировано")
        print("3. Минимальный размер (рекомендуется для Discord)")
        
        while True:
            choice = input("\nВаш выбор (1-3, по умолчанию 3): ").strip()
            if choice == '':
                choice = '3'
            
            level_map = {'1': 0, '2': 1, '3': 2}
            if choice in level_map:
                level = level_map[choice]
                break
            else:
                print("❌ Пожалуйста, выберите 1, 2 или 3")
        
        # Конвертация
        print(f"\n⚙️  Конвертация с уровнем оптимизации {['Качество', 'Баланс', 'Размер'][level]}...")
        
        converter = DiscordGIFConverter(optimize_level=level)
        
        # Автоматическое имя файла
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"discord_gif_{timestamp}.gif"
        
        success, result = converter.convert_mp4_to_gif(
            input_file,
            output_file
        )
        
        if success:
            print(f"\n✅ Успешно! Файл сохранен: {result}")
            
            # Показать информацию о файле
            if os.path.exists(result):
                size_mb = os.path.getsize(result) / 1024 / 1024
                print(f"📏 Размер: {size_mb:.2f} MB")
                
                if size_mb > 10:
                    print("⚠️  Внимание: Размер превышает лимит Discord (10MB)")
                    print("   Попробуйте уровень оптимизации 3 для уменьшения размера")
                else:
                    print("✓ Размер подходит для Discord")
                
                print(f"\n📁 Файл сохранен в: {os.path.abspath(result)}")
                
                # Открыть папку с файлом
                open_folder = input("\nОткрыть папку с файлом? (y/n): ").lower()
                if open_folder == 'y':
                    folder = os.path.dirname(os.path.abspath(result))
                    if sys.platform == "win32":
                        os.startfile(folder)
                    elif sys.platform == "darwin":
                        os.system(f'open "{folder}"')
                    else:
                        os.system(f'xdg-open "{folder}"')
            else:
                print("⚠️  Файл не найден после конвертации")
        else:
            print(f"\n❌ Ошибка: {result}")
            
            # Проверка наличия FFmpeg
            print("\n🔍 Проверка наличия FFmpeg...")
            try:
                import subprocess
                result = subprocess.run(['ffmpeg', '-version'], 
                                      capture_output=True, 
                                      text=True)
                if result.returncode != 0:
                    print("❌ FFmpeg не найден!")
                    print("\n📥 Установите FFmpeg:")
                    print("Windows: https://ffmpeg.org/download.html")
                    print("Linux: sudo apt install ffmpeg")
                    print("MacOS: brew install ffmpeg")
            except:
                print("❌ FFmpeg не установлен!")
    
    except KeyboardInterrupt:
        print("\n\n👋 Завершено пользователем")
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")

if __name__ == "__main__":
    quick_convert()