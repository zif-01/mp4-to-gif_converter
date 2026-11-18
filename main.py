#!/usr/bin/env python3
"""
Главный файл для запуска Discord GIF Converter
Выбор между GUI и CLI режимом
"""

import sys
import argparse

def main():
    argv = sys.argv[1:]
    
    # Если нет аргументов, показываем меню выбора
    if not argv:
        print("=" * 50)
        print("Discord GIF Converter")
        print("=" * 50)
        print("Выберите режим:")
        print("1. Графический интерфейс (GUI)")
        print("2. Командная строка (CLI)")
        print("3. Быстрая конвертация")
        print("\nИли используйте аргументы:")
        print("  python main.py --gui           # Запуск GUI")
        print("  python main.py --cli video.mp4 # Запуск CLI")
        print("  python main.py --cli --help    # Помощь по CLI")
        
        choice = input("\nВаш выбор (1-3): ").strip()
        
        if choice == '1':
            from gui_converter import main as gui_main
            gui_main()
        elif choice == '2':
            from discord_gif_converter import main as cli_main
            cli_main(['--help'])
        elif choice == '3':
            from quick_convert import quick_convert
            quick_convert()
        else:
            print("Неверный выбор")
    
    elif argv == ['--gui']:
        from gui_converter import main as gui_main
        gui_main()
    elif argv[0] in ('-h', '--help'):
        parser = argparse.ArgumentParser(description='Discord GIF Converter')
        parser.add_argument('--gui', action='store_true', help='Запустить графический интерфейс')
        parser.add_argument('--cli', action='store_true', help='Запустить командный интерфейс')
        parser.print_help()
    else:
        if argv[0] == '--cli':
            argv = argv[1:]
        from discord_gif_converter import main as cli_main
        cli_main(argv)


if __name__ == "__main__":
    main()