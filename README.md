# 🎮 Discord GIF Converter

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-orange)

**Конвертер MP4 в GIF с графическим интерфейсом, оптимизированный для Discord**

Преобразуйте ваши видео в GIF-файлы, которые идеально подходят для Discord с автоматической оптимизацией размера и качества.

## ✨ Возможности

- 🎨 **Современный графический интерфейс** с поддержкой drag & drop
- ⚡ **Автоматическая оптимизация** под ограничения Discord (10 МБ, 10 секунд)
- 📊 **3 уровня оптимизации** (качество/баланс/размер)
- 🎞️ **Обрезка видео** по времени
- 📁 **Пакетная обработка** нескольких файлов
- 📝 **Детальный лог** конвертации с прогресс-баром
- 🚀 **3 режима работы**: GUI, командная строка, быстрая конвертация

## 🚀 Быстрый старт

### 📥 Установка

#### Для Windows (рекомендуется)
1. **Скачайте архив** с проектом и распакуйте
2. **Запустите установку** двойным кликом на `setup.bat`
3. **Запустите программу** через `launch.bat`

#### Для Linux/macOS
```bash
# Клонируйте репозиторий
git clone https://github.com/ваш_username/discord-gif-converter.git
cd discord-gif-converter

# Дайте права на выполнение и запустите установку
chmod +x install.sh
./install.sh

# Запустите программу
python main.py
🔧 Установка FFmpeg (обязательно)
Программа использует FFmpeg для конвертации видео. Установите его:

Windows
Скачайте с ffmpeg.org

Распакуйте в C:\ffmpeg

Добавьте C:\ffmpeg\bin в системную переменную PATH

Перезагрузите компьютер

Linux (Ubuntu/Debian)
bash
sudo apt update
sudo apt install ffmpeg
macOS
bash
brew install ffmpeg
Проверка установки FFmpeg
bash
ffmpeg -version
🖥️ Использование
Графический интерфейс (рекомендуется)
bash
python main.py
или просто запустите launch.bat (Windows)

Командная строка
bash
# Базовое использование
python discord_gif_converter.py video.mp4

# С настройками
python discord_gif_converter.py video.mp4 -o output.gif -f 10 -w 400 -l 2

# Обрезка видео (с 5 по 15 секунду)
python discord_gif_converter.py video.mp4 -s 5 -e 15

# Пакетная конвертация всех MP4 в папке
python discord_gif_converter.py ./videos/ -b
Быстрая конвертация
bash
python quick_convert.py
⚙️ Параметры командной строки
Параметр	Описание	Пример	По умолчанию
-o, --output	Выходной файл	-o meme.gif	автоимя
-f, --fps	Кадров в секунду	-f 10	8
-w, --width	Ширина в пикселях	-w 400	400
-s, --start	Начало обрезки (секунды)	-s 5	0
-e, --end	Конец обрезки (секунды)	-e 15	до конца
-l, --level	Уровень оптимизации (0-2)	-l 2	2
-b, --batch	Пакетная конвертация	-b	выкл
🎯 Уровни оптимизации
Уровень	Название	Цвета	FPS	Ширина	Для чего
0	Качество	256	15	640px	Максимальное качество
1	Баланс	128	10	480px	Баланс качества/размера
2	Размер	64	8	400px	Для Discord (рекомендуется)
📁 Структура проекта
text
discord-gif-converter/
├── 📄 main.py                 # Главный запускающий файл
├── 📄 discord_gif_converter.py # Основной конвертер (CLI)
├── 📄 gui_converter.py        # Графический интерфейс
├── 📄 quick_convert.py        # Быстрая конвертация
├── 📄 requirements.txt        # Зависимости Python
├── 📄 setup.bat              # Установщик для Windows
├── 📄 install.sh             # Установщик для Linux/macOS
├── 📄 README.md              # Эта документация
├── 📄 LICENSE                # Лицензия MIT
├── 📄 .gitignore             # Игнорируемые файлы
└── 📁 screenshots/           # Скриншоты программы
🐛 Устранение неполадок
❌ "FFmpeg не найден"
Убедитесь, что FFmpeg установлен: ffmpeg -version

Проверьте наличие в PATH: where ffmpeg (Windows) или which ffmpeg (Linux/macOS)

Перезагрузите компьютер после добавления в PATH

❌ "NumPy ошибка"
bash
pip uninstall numpy -y
pip install numpy==1.24.3
❌ "tkinterdnd2 не устанавливается"
bash
# Способ 1: Стандартная установка
pip install tkinterdnd2

# Способ 2: Без drag&drop (ограниченный функционал)
# Отредактируйте gui_converter.py, закомментировав импорт tkinterdnd2
❌ "AttributeError: _ARRAY_API not found"
bash
# Проблема несовместимости NumPy 2.x
pip install numpy==1.24.3
❌ Программа зависает при конвертации
Убедитесь, что FFmpeg работает: ffmpeg -version

Проверьте права на запись в папку вывода

Попробуйте уменьшить разрешение или FPS

🔧 Технические детали
Зависимости
Python 3.8+ - основной язык

FFmpeg - конвертация видео (обязательно)

Pillow - обработка изображений

NumPy 1.24.3 - работа с массивами

ImageIO - чтение/запись медиа

Tkinter - графический интерфейс

tkinterdnd2 - поддержка drag & drop

Поддерживаемые форматы
Входные: MP4, AVI, MOV, MKV, WMV

Выходные: GIF (оптимизированный для Discord)

Ограничения Discord
✅ Максимальный размер: 10 МБ

✅ Максимальная длительность: 10 секунд

✅ Рекомендуемый FPS: 8-10

✅ Рекомендуемая ширина: 400-480px

🤝 Вклад в развитие
Хотите улучшить проект? Отлично!

Форкните репозиторий

Создайте ветку для вашей функции:

bash
git checkout -b feature/amazing-feature
Зафиксируйте изменения:

bash
git commit -m 'Добавил крутую функцию'
Запушьте ветку:

bash
git push origin feature/amazing-feature
Создайте Pull Request

📄 Лицензия
Этот проект распространяется под лицензией MIT. Подробнее в файле LICENSE.

text
MIT License

Copyright (c) 2024 [Ваше Имя]

Разрешается свободное использование, копирование, изменение, объединение, публикация, 
распространение, сублицензирование и/или продажа копий программного обеспечения.
👨‍💻 Автор
ZXF - GitHub | Email polianskyzif1132@gmail.com

🙏 Благодарности
FFmpeg - мощный инструмент для работы с мультимедиа

Сообществу Python за отличные библиотеки

Discord за вдохновение для создания этого инструмента

📞 Поддержка
Нашли баг или есть предложение?

Создайте Issue в репозитории

Опишите проблему подробно

Приложите скриншоты если нужно

Укажите версии Python и FFmpeg

<div align="center">
⭐ Если проект вам понравился, поставьте звезду на GitHub!
Happy GIF making! 🎉

</div> ```
