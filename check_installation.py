#!/usr/bin/env python3
"""
Скрипт для быстрой проверки установки MyTelegramBot
Запуск: python check_installation.py
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def print_header(text):
    """Печать заголовка с разделителем"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print('='*60)

def print_check(name, status, details=""):
    """Печать результата проверки"""
    icon = "✅" if status else "❌"
    print(f"{icon} {name:<30} {details}")

def check_python_version():
    """Проверка версии Python"""
    print_header("ПРОВЕРКА ВЕРСИИ PYTHON")

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    if version.major == 3 and version.minor >= 8:
        print_check("Python версия", True, f"v{version_str} (OK)")
        return True
    else:
        print_check("Python версия", False, f"v{version_str} (Требуется Python 3.8+)")
        return False

def check_module(module_name, display_name=None):
    """Проверка установки Python модуля"""
    if display_name is None:
        display_name = module_name

    try:
        spec = importlib.util.find_spec(module_name)
        if spec is not None:
            module = importlib.import_module(module_name)
            version = getattr(module, '__version__', 'unknown')
            print_check(display_name, True, f"v{version}")
            return True
        else:
            print_check(display_name, False, "не найден")
            return False
    except ImportError as e:
        print_check(display_name, False, f"ошибка импорта: {e}")
        return False

def check_python_dependencies():
    """Проверка Python зависимостей"""
    print_header("ПРОВЕРКА PYTHON ЗАВИСИМОСТЕЙ")

    dependencies = [
        ('telegram', 'python-telegram-bot'),
        ('openai', 'OpenAI'),
        ('speech_recognition', 'SpeechRecognition'),
        ('gtts', 'gTTS'),
        ('pydub', 'pydub'),
        ('dotenv', 'python-dotenv'),
    ]

    all_ok = True
    for module, display in dependencies:
        if not check_module(module, display):
            all_ok = False

    return all_ok

def check_system_command(command, display_name=None):
    """Проверка системной команды"""
    if display_name is None:
        display_name = command

    try:
        result = subprocess.run([command, '-version'],
                              capture_output=True,
                              text=True,
                              timeout=10)
        if result.returncode == 0:
            # Извлекаем версию из первой строки
            version_line = result.stdout.split('\n')[0]
            print_check(display_name, True, version_line[:50] + "..." if len(version_line) > 50 else version_line)
            return True
        else:
            print_check(display_name, False, "команда завершилась с ошибкой")
            return False
    except FileNotFoundError:
        print_check(display_name, False, "команда не найдена")
        return False
    except subprocess.TimeoutExpired:
        print_check(display_name, False, "таймаут выполнения")
        return False
    except Exception as e:
        print_check(display_name, False, f"ошибка: {e}")
        return False

def check_system_dependencies():
    """Проверка системных зависимостей"""
    print_header("ПРОВЕРКА СИСТЕМНЫХ ЗАВИСИМОСТЕЙ")

    commands = [
        ('ffmpeg', 'FFmpeg'),
        ('ffprobe', 'FFprobe'),
    ]

    all_ok = True
    for command, display in commands:
        if not check_system_command(command, display):
            all_ok = False

    return all_ok

def check_project_structure():
    """Проверка структуры проекта"""
    print_header("ПРОВЕРКА СТРУКТУРЫ ПРОЕКТА")

    required_files = [
        'bot.py',
        'requirements.txt',
        '.env.example',
        'handlers/__init__.py',
        'services/__init__.py',
        'data/__init__.py',
    ]

    required_dirs = [
        'handlers',
        'services',
        'data',
    ]

    all_ok = True

    # Проверка файлов
    for file_path in required_files:
        if os.path.exists(file_path):
            print_check(f"Файл {file_path}", True)
        else:
            print_check(f"Файл {file_path}", False, "не найден")
            all_ok = False

    # Проверка директорий
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            print_check(f"Папка {dir_path}/", True)
        else:
            print_check(f"Папка {dir_path}/", False, "не найдена")
            all_ok = False

    return all_ok

def check_configuration():
    """Проверка конфигурации"""
    print_header("ПРОВЕРКА КОНФИГУРАЦИИ")

    # Проверка .env файла
    env_exists = os.path.exists('.env')
    print_check(".env файл", env_exists)

    if env_exists:
        try:
            from dotenv import load_dotenv
            load_dotenv()

            telegram_token = os.getenv('TELEGRAM_TOKEN')
            openai_key = os.getenv('OPENAI_API_KEY')

            token_ok = telegram_token and telegram_token != 'your_telegram_bot_token_here' and len(telegram_token) > 10
            key_ok = openai_key and openai_key != 'your_openai_api_key_here' and len(openai_key) > 10

            print_check("TELEGRAM_TOKEN", token_ok, "настроен" if token_ok else "не настроен или пустой")
            print_check("OPENAI_API_KEY", key_ok, "настроен" if key_ok else "не настроен или пустой")

            return token_ok and key_ok
        except Exception as e:
            print_check("Загрузка .env", False, f"ошибка: {e}")
            return False
    else:
        print_check("TELEGRAM_TOKEN", False, ".env файл не найден")
        print_check("OPENAI_API_KEY", False, ".env файл не найден")
        return False

def check_project_imports():
    """Проверка импорта модулей проекта"""
    print_header("ПРОВЕРКА ИМПОРТА МОДУЛЕЙ ПРОЕКТА")

    modules_to_test = [
        ('handlers.basic', 'handlers/basic.py'),
        ('handlers.chatgpt_interface', 'handlers/chatgpt_interface.py'),
        ('handlers.voice_chat', 'handlers/voice_chat.py'),
        ('services.openai_client', 'services/openai_client.py'),
        ('services.voice_recognition', 'services/voice_recognition.py'),
        ('data.languages', 'data/languages.py'),
        ('data.personalities', 'data/personalities.py'),
    ]

    all_ok = True
    for module_name, file_path in modules_to_test:
        try:
            importlib.import_module(module_name)
            print_check(f"Импорт {module_name}", True)
        except ImportError as e:
            print_check(f"Импорт {module_name}", False, f"ошибка: {e}")
            all_ok = False
        except Exception as e:
            print_check(f"Импорт {module_name}", False, f"неожиданная ошибка: {e}")
            all_ok = False

    return all_ok

def test_audio_processing():
    """Тест обработки аудио"""
    print_header("ТЕСТ ОБРАБОТКИ АУДИО")

    try:
        from pydub import AudioSegment
        from pydub.generators import Sine

        # Создаем тестовый аудиосигнал
        tone = Sine(440).to_audio_segment(duration=1000)  # 1 секунда
        print_check("Создание аудио", True)

        # Тестируем экспорт в разные форматы
        formats_to_test = ['wav', 'mp3', 'ogg']
        for fmt in formats_to_test:
            try:
                test_file = f"test_audio_temp.{fmt}"
                tone.export(test_file, format=fmt)

                # Проверяем, что файл создался
                if os.path.exists(test_file):
                    # Пробуем загрузить обратно
                    if fmt == 'wav':
                        AudioSegment.from_wav(test_file)
                    elif fmt == 'mp3':
                        AudioSegment.from_mp3(test_file)
                    elif fmt == 'ogg':
                        AudioSegment.from_ogg(test_file)

                    print_check(f"Формат {fmt.upper()}", True)

                    # Удаляем тестовый файл
                    os.remove(test_file)
                else:
                    print_check(f"Формат {fmt.upper()}", False, "файл не создался")

            except Exception as e:
                print_check(f"Формат {fmt.upper()}", False, f"ошибка: {e}")

        return True

    except ImportError as e:
        print_check("Тест аудио", False, f"ошибка импорта: {e}")
        return False
    except Exception as e:
        print_check("Тест аудио", False, f"неожиданная ошибка: {e}")
        return False

def print_summary(results):
    """Печать итогового резюме"""
    print_header("ИТОГОВОЕ РЕЗЮМЕ")

    total_checks = len(results)
    passed_checks = sum(1 for status in results.values() if status)

    print(f"Всего проверок: {total_checks}")
    print(f"Успешно: {passed_checks}")
    print(f"Неудачно: {total_checks - passed_checks}")
    if total_checks > 0:
        print(f"Процент успеха: {(passed_checks/total_checks)*100:.1f}%")

    if all(results.values()):
        print("\n🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
        print("   Ваш бот готов к запуску: python bot.py")
    else:
        print("\n⚠️  НЕКОТОРЫЕ ПРОВЕРКИ НЕ ПРОЙДЕНЫ")
        print("   Обратитесь к README.md для инструкций по установке")

        failed_checks = [name for name, status in results.items() if not status]
        print(f"   Проблемные области: {', '.join(failed_checks)}")

def main():
    """Главная функция"""
    print("🔧 MyTelegramBot - Проверка установки")
    print(f"Рабочая директория: {os.getcwd()}")

    # Добавляем текущую директорию в Python path для импорта модулей проекта
    sys.path.insert(0, os.getcwd())

    # Выполняем все проверки
    results = {}

    results["Python версия"] = check_python_version()
    results["Python зависимости"] = check_python_dependencies()
    results["Системные зависимости"] = check_system_dependencies()
    results["Структура проекта"] = check_project_structure()
    results["Конфигурация"] = check_configuration()
    results["Импорт модулей"] = check_project_imports()
    results["Обработка аудио"] = test_audio_processing()

    # Печатаем итоговое резюме
    print_summary(results)

    # Возвращаем код выхода
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Проверка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        sys.exit(1)
