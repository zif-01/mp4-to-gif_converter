import os
import sys
import argparse
from pathlib import Path
from typing import Optional, Tuple
import subprocess
import tempfile
import json

class DiscordGIFConverter:
    """Конвертер MP4 в GIF оптимизированный для Discord (без moviepy)"""
    
    # Discord limitations
    DISCORD_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    DISCORD_MAX_DURATION = 10  # секунд
    DISCORD_RECOMMENDED_WIDTH = 480
    
    def __init__(self, optimize_level: int = 2):
        """
        Args:
            optimize_level: 
                0 - минимальная оптимизация (лучшее качество)
                1 - средняя оптимизация
                2 - максимальная оптимизация (для Discord)
        """
        self.optimize_level = optimize_level
        self.presets = {
            0: {'fps': 15, 'width': 640, 'colors': 256, 'quality': 90},
            1: {'fps': 10, 'width': 480, 'colors': 128, 'quality': 80},
            2: {'fps': 8, 'width': 400, 'colors': 64, 'quality': 70}
        }
        
        # Проверка наличия ffmpeg
        self.ffmpeg_path = self._find_ffmpeg()
        
    def _get_preset(self):
        """Получить настройки для текущего уровня оптимизации"""
        return self.presets.get(self.optimize_level, self.presets[2])
    
    def _find_ffmpeg(self) -> str:
        """Найти путь к ffmpeg"""
        # Сначала проверяем PATH
        try:
            subprocess.run(['ffmpeg', '-version'], 
                          capture_output=True, 
                          check=True)
            return 'ffmpeg'
        except:
            # Проверяем imageio-ffmpeg
            try:
                import imageio_ffmpeg
                return imageio_ffmpeg.get_ffmpeg_exe()
            except:
                # Ищем в возможных местах
                possible_paths = [
                    os.path.join(os.path.dirname(sys.executable), 'ffmpeg.exe'),
                    os.path.join(os.path.dirname(sys.executable), 'Scripts', 'ffmpeg.exe'),
                    'C:\\ffmpeg\\bin\\ffmpeg.exe',
                    '/usr/local/bin/ffmpeg',
                    '/usr/bin/ffmpeg'
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        return path
                
                raise Exception("FFmpeg не найден. Установите ffmpeg и добавьте в PATH")
    
    def _check_file_size(self, filepath: str, max_size: int = None) -> bool:
        """Проверить размер файла"""
        if max_size is None:
            max_size = self.DISCORD_MAX_SIZE
        
        size = os.path.getsize(filepath)
        mb_size = size / 1024 / 1024
        print(f"Размер файла: {mb_size:.2f} MB")
        
        if size > max_size:
            print(f"⚠️  Предупреждение: Размер GIF ({mb_size:.2f} MB) превышает {max_size/1024/1024} MB")
            return False
        return True
    
    def _get_video_info(self, video_path: str) -> dict:
        """Получить информацию о видео с помощью ffprobe"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            info = json.loads(result.stdout)
            
            # Ищем видео поток
            video_stream = None
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                    break
            
            duration = float(info.get('format', {}).get('duration', 0))
            width = int(video_stream.get('width', 0)) if video_stream else 0
            height = int(video_stream.get('height', 0)) if video_stream else 0
            fps_str = video_stream.get('r_frame_rate', '0/1') if video_stream else '0/1'
            
            # Вычисляем FPS
            if '/' in fps_str:
                num, den = fps_str.split('/')
                fps = float(num) / float(den) if float(den) != 0 else 0
            else:
                fps = float(fps_str)
            
            return {
                'duration': duration,
                'width': width,
                'height': height,
                'fps': fps,
                'total_frames': int(duration * fps) if fps > 0 else 0
            }
            
        except Exception as e:
            print(f"Ошибка получения информации о видео: {e}")
            return {'duration': 0, 'width': 0, 'height': 0, 'fps': 0, 'total_frames': 0}
    
    def convert_mp4_to_gif(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        custom_fps: Optional[int] = None,
        custom_width: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Основная функция конвертации с использованием ffmpeg
        
        Args:
            input_path: путь к MP4 файлу
            output_path: путь для сохранения GIF (если None, генерируется автоматически)
            start_time: начальное время в секундах
            end_time: конечное время в секундах
            custom_fps: кастомный FPS
            custom_width: кастомная ширина
            
        Returns:
            Tuple[успех, путь к файлу]
        """
        try:
            # Генерация имени выходного файла
            if output_path is None:
                input_stem = Path(input_path).stem
                output_path = f"{input_stem}_discord.gif"
            
            # Получение информации о видео
            print(f"📹 Анализ видео: {input_path}")
            video_info = self._get_video_info(input_path)
            duration = video_info['duration']
            
            # Обрезка для Discord
            if duration > self.DISCORD_MAX_DURATION:
                if end_time is None or end_time > self.DISCORD_MAX_DURATION:
                    end_time = min(end_time or duration, self.DISCORD_MAX_DURATION)
                    print(f"Видео обрезано до {end_time} секунд (лимит Discord)")
            
            # Обрезка по времени
            if start_time is not None and end_time is not None:
                if end_time - start_time > self.DISCORD_MAX_DURATION:
                    end_time = start_time + self.DISCORD_MAX_DURATION
                    print(f"Клип обрезан до {self.DISCORD_MAX_DURATION} секунд")
            
            # Получение настроек
            preset = self._get_preset()
            fps = custom_fps or preset['fps']
            width = custom_width or preset['width']
            
            print(f"⚙️  Настройки конвертации:")
            print(f"   • Длительность: {duration:.1f} сек")
            print(f"   • Исходный FPS: {video_info['fps']:.1f}")
            print(f"   • Целевой FPS: {fps}")
            print(f"   • Ширина: {width}px")
            
            # Построение команды ffmpeg
            cmd = [self.ffmpeg_path, '-y']
            
            # Добавляем временные ограничения
            if start_time is not None:
                cmd.extend(['-ss', str(start_time)])
            
            if end_time is not None and start_time is not None:
                cmd.extend(['-t', str(end_time - start_time)])
            elif end_time is not None:
                cmd.extend(['-t', str(end_time)])
            
            # Основные параметры
            cmd.extend([
                '-i', input_path,
                '-vf', f'fps={fps},scale={width}:-1:flags=lanczos',
                '-gifflags', '+transdiff',
                '-y'  # Перезаписать без подтверждения
            ])
            
            # Параметры палитры для лучшего качества
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                palette_path = tmp.name
            
            # Генерация палитры
            palette_cmd = [
                self.ffmpeg_path, '-y',
                '-i', input_path
            ]
            
            if start_time is not None:
                palette_cmd.extend(['-ss', str(start_time)])
            
            if end_time is not None and start_time is not None:
                palette_cmd.extend(['-t', str(end_time - start_time)])
            
            palette_cmd.extend([
                '-vf', f'fps={fps},scale={width}:-1:flags=lanczos,palettegen',
                palette_path
            ])
            
            print("🎨 Генерация палитры цветов...")
            result = subprocess.run(palette_cmd, 
                                  capture_output=True, 
                                  text=True,
                                  creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
            
            if result.returncode != 0:
                print(f"Ошибка генерации палитры: {result.stderr}")
                # Пробуем без палитры
                cmd.append(output_path)
            else:
                # Использование палитры
                cmd.extend([
                    '-i', palette_path,
                    '-filter_complex', f'[0:v]fps={fps},scale={width}:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=sierra2_4a',
                    output_path
                ])
            
            print("🔄 Конвертация MP4 → GIF...")
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True,
                                  creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
            
            # Удаление временного файла палитры
            if os.path.exists(palette_path):
                os.remove(palette_path)
            
            if result.returncode != 0:
                print(f"❌ Ошибка конвертации: {result.stderr}")
                
                # Пробуем простую конвертацию без палитры
                print("🔄 Попытка простой конвертации...")
                simple_cmd = [
                    self.ffmpeg_path, '-y',
                    '-i', input_path,
                    '-vf', f'fps={fps},scale={width}:-1',
                    output_path
                ]
                
                result = subprocess.run(simple_cmd, 
                                      capture_output=True, 
                                      text=True,
                                      creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
                
                if result.returncode != 0:
                    return False, f"Ошибка конвертации: {result.stderr}"
            
            # Оптимизация с помощью ImageMagick (если доступен)
            self._optimize_gif_imagemagick(output_path, preset)
            
            # Проверка размера
            if os.path.exists(output_path):
                size_ok = self._check_file_size(output_path)
                
                if not size_ok and self.optimize_level < 2:
                    print("🔄 Повторная конвертация с максимальной оптимизацией...")
                    self.optimize_level = 2
                    return self.convert_mp4_to_gif(
                        input_path, output_path, start_time, end_time
                    )
                
                print(f"✅ Готово! GIF сохранен: {output_path}")
                return True, output_path
            else:
                return False, "Выходной файл не создан"
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False, str(e)
    
    def _optimize_gif_imagemagick(self, gif_path: str, preset: dict):
        """Оптимизация GIF с помощью ImageMagick (если доступен)"""
        try:
            # Проверяем наличие ImageMagick
            subprocess.run(['magick', '-version'], 
                          capture_output=True, 
                          check=True)
            
            # Создаем временный файл
            temp_path = gif_path + '.tmp.gif'
            
            # Команда оптимизации
            cmd = [
                'magick', gif_path,
                '-layers', 'Optimize',
                '-colors', str(preset['colors']),
                temp_path
            ]
            
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True,
                                  creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
            
            if result.returncode == 0 and os.path.exists(temp_path):
                os.replace(temp_path, gif_path)
                print("🔧 GIF оптимизирован с помощью ImageMagick")
            else:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
        except:
            # ImageMagick не доступен, используем простую оптимизацию через ffmpeg
            try:
                temp_path = gif_path + '.tmp.gif'
                cmd = [
                    self.ffmpeg_path, '-y',
                    '-i', gif_path,
                    '-vf', 'split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse',
                    temp_path
                ]
                
                result = subprocess.run(cmd, 
                                      capture_output=True, 
                                      text=True,
                                      creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
                
                if result.returncode == 0 and os.path.exists(temp_path):
                    os.replace(temp_path, gif_path)
                    print("🔧 GIF оптимизирован с помощью ffmpeg")
                else:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            except:
                print("⚠️  ImageMagick не найден, оптимизация пропущена")
    
    def batch_convert(
        self,
        input_folder: str,
        output_folder: Optional[str] = None,
        pattern: str = "*.mp4"
    ) -> None:
        """
        Пакетная конвертация всех MP4 файлов в папке
        
        Args:
            input_folder: папка с MP4 файлами
            output_folder: папка для сохранения GIF
            pattern: шаблон поиска файлов
        """
        input_path = Path(input_folder)
        
        if output_folder is None:
            output_folder = input_folder + "_gifs"
        
        output_path = Path(output_folder)
        output_path.mkdir(exist_ok=True)
        
        # Поиск всех MP4 файлов
        mp4_files = list(input_path.glob(pattern))
        
        if not mp4_files:
            print(f"❌ MP4 файлы не найдены в {input_folder}")
            return
        
        print(f"📁 Найдено {len(mp4_files)} MP4 файлов")
        
        successful = 0
        for i, mp4_file in enumerate(mp4_files, 1):
            print(f"\n[{i}/{len(mp4_files)}] Конвертация: {mp4_file.name}")
            
            output_file = output_path / f"{mp4_file.stem}_discord.gif"
            
            success, _ = self.convert_mp4_to_gif(
                str(mp4_file),
                str(output_file)
            )
            
            if success:
                successful += 1
        
        print(f"\n📊 Итог: {successful}/{len(mp4_files)} успешно сконвертировано")


def main():
    parser = argparse.ArgumentParser(description='Конвертер MP4 в GIF для Discord')
    parser.add_argument('input', help='Путь к MP4 файлу или папке')
    parser.add_argument('-o', '--output', help='Путь для сохранения GIF')
    parser.add_argument('-f', '--fps', type=int, help='Кастомный FPS')
    parser.add_argument('-w', '--width', type=int, help='Ширина GIF в пикселях')
    parser.add_argument('-s', '--start', type=float, help='Начальное время (секунды)')
    parser.add_argument('-e', '--end', type=float, help='Конечное время (секунды)')
    parser.add_argument('-l', '--level', type=int, choices=[0, 1, 2], default=2,
                       help='Уровень оптимизации: 0-качество, 1-баланс, 2-размер (по умолчанию)')
    parser.add_argument('-b', '--batch', action='store_true',
                       help='Пакетная конвертация всех MP4 в папке')
    
    args = parser.parse_args()
    
    # Создание конвертера
    converter = DiscordGIFConverter(optimize_level=args.level)
    
    if args.batch:
        # Пакетная конвертация
        converter.batch_convert(args.input, args.output)
    else:
        # Конвертация одного файла
        success, result = converter.convert_mp4_to_gif(
            input_path=args.input,
            output_path=args.output,
            start_time=args.start,
            end_time=args.end,
            custom_fps=args.fps,
            custom_width=args.width
        )
        
        if not success:
            print(f"\n❌ Конвертация не удалась: {result}")
            sys.exit(1)


if __name__ == "__main__":
    print("=" * 50)
    print("Discord GIF Converter v2.0")
    print("Использует FFmpeg (без зависимостей от moviepy/opencv)")
    print("Оптимизировано для Discord (макс. 10MB)")
    print("=" * 50)
    
    main()