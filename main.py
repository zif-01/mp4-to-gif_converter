#!/usr/bin/env python3
"""
Главный файл для запуска Discord GIF Converter
Выбор между GUI и CLI режимом
"""

import sys
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='Discord GIF Converter')
    parser.add_argument('--gui', action='store_true', help='Запустить графический интерфейс')
    parser.add_argument('--cli', action='store_true', help='Запустить командный интерфейс')
    parser.add_argument('input', nargs='?', help='Входной файл (для CLI режима)')
    parser.add_argument('-o', '--output', help='Выходной файл (для CLI режима)')
    
    # Если нет аргументов, показываем меню выбора
    if len(sys.argv) == 1:
        print("=" * 50)
        print("Discord GIF Converter")
        print("=" * 50)
        print("Выберите режим:")
        print("1. Графический интерфейс (GUI)")
        print("2. Командная строка (CLI)")
        print("3. Быстрая конвертация")
        print("\nИли используйте аргументы:")
        print("  python main.py --gui           # Запуск GUI")
        print("  python main.py video.mp4       # Быстрая конвертация")
        print("  python main.py --cli --help    # Помощь по CLI")
        
        choice = input("\nВаш выбор (1-3): ").strip()
        
        if choice == '1':
            from gui_converter import main as gui_main
            gui_main()
        elif choice == '2':
            # Запуск CLI с подсказкой
            os.system(f'python discord_gif_converter.py --help')
        elif choice == '3':
            from quick_convert import quick_convert
            quick_convert()
        else:
            print("Неверный выбор")
    
    # Обработка аргументов командной строки
    else:
        args = parser.parse_args()
        
        if args.gui:
            from gui_converter import main as gui_main
            gui_main()
        elif args.input or args.cli:
            from discord_gif_converter import main as cli_main
            cli_main()
        else:
            parser.print_help()


if __name__ == "__main__":
    main()