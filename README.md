# Discord GIF Converter

Конвертер видео в GIF на базе FFmpeg. Включает графический интерфейс, CLI и
интерактивный режим быстрой конвертации.

## Возможности

- Три профиля качества и настройка FPS/ширины через CLI.
- Обрезка по времени; длительность одного GIF ограничивается 10 секундами.
- Пакетная конвертация из командной строки.
- GUI с выбором нескольких файлов, логом и прогрессом.
- Drag & drop в GUI при установленном `tkinterdnd2`.

Конвертер предупреждает, если результат превышает 10 MiB. Размер зависит от
содержимого видео, поэтому соответствие лимиту не гарантируется.

## Установка

Нужен Python 3.8 или новее. Создайте виртуальное окружение и установите
зависимости:

### Windows

```bat
setup.bat
launch.bat
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

Tkinter должен быть доступен в установленном Python. На некоторых Linux
дистрибутивах его нужно установить отдельным системным пакетом.

Проект использует системный `ffmpeg`, если он есть в `PATH`, иначе — FFmpeg из
пакета `imageio-ffmpeg`. Для сведений о видео используется `ffprobe`, если он
доступен; если его нет, конвертация всё равно ограничивает клип 10 секундами.

Drag & drop — необязательная возможность. Установите её отдельно:

```bash
python -m pip install tkinterdnd2
```

## Использование

### GUI

```bash
python main.py --gui
```

Или `python main.py` для меню запуска.

### CLI

```bash
# Конвертировать файл
python discord_gif_converter.py video.mp4

# Выбрать GIF и параметры
python discord_gif_converter.py video.mp4 -o output.gif -f 10 -w 400 -l 2

# Обрезать от 5 до 15 секунды (не более 10 секунд)
python discord_gif_converter.py video.mp4 -s 5 -e 15

# Пакетная конвертация MP4 из папки
python discord_gif_converter.py ./videos/ -b
```

CLI также доступен через `python main.py --cli ...`. Справка:
`python discord_gif_converter.py --help`.

### Быстрая интерактивная конвертация

```bash
python quick_convert.py
```

## Параметры CLI

| Параметр | Описание |
|---|---|
| `-o, --output` | Путь к выходному GIF |
| `-f, --fps` | FPS (положительное целое число) |
| `-w, --width` | Ширина GIF в пикселях |
| `-s, --start` | Начало фрагмента в секундах |
| `-e, --end` | Конец фрагмента в секундах |
| `-l, --level` | Профиль: `0` — качество, `1` — баланс, `2` — компактность |
| `-b, --batch` | Конвертировать файлы из указанной папки |

Доступные входные форматы зависят от сборки FFmpeg. GUI предлагает выбирать
MP4-файлы.

## Файлы проекта

- `main.py` — меню запуска GUI/CLI.
- `discord_gif_converter.py` — конвертер и CLI.
- `gui_converter.py` — графический интерфейс.
- `quick_convert.py` — интерактивная конвертация.
- `requirements.txt` — Python-зависимости.
- `setup.bat` — настройка окружения Windows.

## Тесты

```bash
python -m unittest discover -s tests
```

## Лицензия

Файл лицензии в репозитории отсутствует. Добавьте `LICENSE` с выбранной
лицензией перед распространением проекта.
