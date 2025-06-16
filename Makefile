# MyTelegramBot Makefile
# Удобные команды для управления проектом

.PHONY: help install install-system check run clean test lint format requirements

# Цвета для вывода
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
BLUE=\033[0;34m
NC=\033[0m # No Color

# Python интерпретатор
PYTHON := python3
PIP := pip3

# Виртуальное окружение
VENV_NAME := .venv
VENV_BIN := $(VENV_NAME)/bin
VENV_PYTHON := $(VENV_BIN)/python
VENV_PIP := $(VENV_BIN)/pip

help: ## Показать справку по командам
	@echo "$(BLUE)MyTelegramBot - Доступные команды:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Полная установка проекта (создание venv + установка зависимостей)
	@echo "$(YELLOW)Создание виртуального окружения...$(NC)"
	$(PYTHON) -m venv $(VENV_NAME)
	@echo "$(YELLOW)Обновление pip...$(NC)"
	$(VENV_PIP) install --upgrade pip
	@echo "$(YELLOW)Установка зависимостей...$(NC)"
	$(VENV_PIP) install -r requirements.txt
	@echo "$(GREEN)✅ Установка завершена!$(NC)"
	@echo "$(BLUE)Активируйте окружение: source $(VENV_BIN)/activate$(NC)"

install-system: ## Установка системных зависимостей (Linux/Ubuntu)
	@echo "$(YELLOW)Установка системных зависимостей...$(NC)"
	@if command -v apt >/dev/null 2>&1; then \
		echo "$(BLUE)Обнаружен APT пакетный менеджер$(NC)"; \
		sudo apt update; \
		sudo apt install -y ffmpeg portaudio19-dev python3-dev; \
	elif command -v brew >/dev/null 2>&1; then \
		echo "$(BLUE)Обнаружен Homebrew$(NC)"; \
		brew install ffmpeg portaudio; \
	else \
		echo "$(RED)❌ Неподдерживаемая система. Установите ffmpeg вручную.$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✅ Системные зависимости установлены!$(NC)"

install-all: install-system install ## Полная установка (система + Python пакеты)

check: ## Проверка установки и конфигурации
	@echo "$(BLUE)Запуск проверки установки...$(NC)"
	@if [ -f $(VENV_PYTHON) ]; then \
		$(VENV_PYTHON) check_installation.py; \
	else \
		$(PYTHON) check_installation.py; \
	fi

run: ## Запуск бота
	@echo "$(BLUE)Запуск бота...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(RED)❌ Файл .env не найден!$(NC)"; \
		echo "$(YELLOW)Создайте .env файл на основе .env.example$(NC)"; \
		exit 1; \
	fi
	@if [ -f $(VENV_PYTHON) ]; then \
		$(VENV_PYTHON) bot.py; \
	else \
		$(PYTHON) bot.py; \
	fi

run-dev: ## Запуск бота в режиме разработки (с подробным логированием)
	@echo "$(BLUE)Запуск бота в режиме разработки...$(NC)"
	@if [ -f $(VENV_PYTHON) ]; then \
		LOG_LEVEL=DEBUG $(VENV_PYTHON) bot.py; \
	else \
		LOG_LEVEL=DEBUG $(PYTHON) bot.py; \
	fi

clean: ## Очистка временных файлов
	@echo "$(YELLOW)Очистка временных файлов...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "voice_*.ogg" -delete
	find . -type f -name "voice_*.wav" -delete
	find . -type f -name "response_*.mp3" -delete
	find . -type f -name "response_*.ogg" -delete
	find . -type f -name "test_audio*" -delete
	find . -type f -name "*.tmp" -delete
	find . -type f -name "*.log" -delete
	@echo "$(GREEN)✅ Очистка завершена!$(NC)"

clean-all: clean ## Полная очистка (включаая виртуальное окружение)
	@echo "$(YELLOW)Удаление виртуального окружения...$(NC)"
	rm -rf $(VENV_NAME)
	@echo "$(GREEN)✅ Полная очистка завершена!$(NC)"

test: ## Запуск тестов (простая проверка импортов)
	@echo "$(BLUE)Запуск тестов...$(NC)"
	@if [ -f $(VENV_PYTHON) ]; then \
		$(VENV_PYTHON) -c "import bot; print('✅ bot.py импортируется успешно')"; \
		$(VENV_PYTHON) -c "from services import voice_recognition; print('✅ voice_recognition работает')"; \
		$(VENV_PYTHON) -c "from handlers import basic; print('✅ handlers импортируются')"; \
	else \
		$(PYTHON) -c "import bot; print('✅ bot.py импортируется успешно')"; \
		$(PYTHON) -c "from services import voice_recognition; print('✅ voice_recognition работает')"; \
		$(PYTHON) -c "from handlers import basic; print('✅ handlers импортируются')"; \
	fi
	@echo "$(GREEN)✅ Все тесты пройдены!$(NC)"

lint: ## Проверка кода с помощью flake8 (если установлен)
	@echo "$(BLUE)Проверка стиля кода...$(NC)"
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 --max-line-length=120 --ignore=E501,W503 .; \
		echo "$(GREEN)✅ Проверка завершена!$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  flake8 не установлен. Установите: pip install flake8$(NC)"; \
	fi

format: ## Форматирование кода с помощью black (если установлен)
	@echo "$(BLUE)Форматирование кода...$(NC)"
	@if command -v black >/dev/null 2>&1; then \
		black --line-length=120 .; \
		echo "$(GREEN)✅ Форматирование завершено!$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  black не установлен. Установите: pip install black$(NC)"; \
	fi

requirements: ## Обновление requirements.txt
	@echo "$(BLUE)Обновление requirements.txt...$(NC)"
	@if [ -f $(VENV_PIP) ]; then \
		$(VENV_PIP) freeze > requirements_new.txt; \
		echo "$(GREEN)✅ Новый файл создан: requirements_new.txt$(NC)"; \
		echo "$(YELLOW)Проверьте и переименуйте в requirements.txt если нужно$(NC)"; \
	else \
		echo "$(RED)❌ Виртуальное окружение не найдено$(NC)"; \
		exit 1; \
	fi

env-example: ## Создание .env файла из .env.example
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN)✅ Файл .env создан из .env.example$(NC)"; \
		echo "$(YELLOW)Не забудьте заполнить токены в .env файле!$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  Файл .env уже существует$(NC)"; \
	fi

setup: env-example install-all check ## Полная настройка проекта с нуля

info: ## Показать информацию о системе и проекте
	@echo "$(BLUE)Информация о системе:$(NC)"
	@echo "OS: $$(uname -s)"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Pip: $$($(PIP) --version)"
	@echo ""
	@echo "$(BLUE)Информация о проекте:$(NC)"
	@echo "Рабочая директория: $$(pwd)"
	@echo "Виртуальное окружение: $(if $(wildcard $(VENV_PYTHON)),$(GREEN)активно$(NC),$(RED)не найдено$(NC))"
	@echo "Конфигурация: $(if $(wildcard .env),$(GREEN)найдена$(NC),$(RED)отсутствует$(NC))"
	@echo ""
	@echo "$(BLUE)Системные утилиты:$(NC)"
	@echo "ffmpeg: $(if $(shell command -v ffmpeg 2>/dev/null),$(GREEN)установлен$(NC),$(RED)не найден$(NC))"
	@echo "ffprobe: $(if $(shell command -v ffprobe 2>/dev/null),$(GREEN)установлен$(NC),$(RED)не найден$(NC))"

# Быстрые команды
up: run ## Алиас для run
dev: run-dev ## Алиас для run-dev
stop: ## Остановка бота (поиск и завершение процесса)
	@echo "$(YELLOW)Поиск и остановка процессов бота...$(NC)"
	@pkill -f "python.*bot.py" 2>/dev/null && echo "$(GREEN)✅ Бот остановлен$(NC)" || echo "$(BLUE)ℹ️  Процесс бота не найден$(NC)"

down: stop ## Алиас для stop

# Команды для разработчиков
dev-install: ## Установка дополнительных инструментов разработки
	@if [ -f $(VENV_PIP) ]; then \
		$(VENV_PIP) install flake8 black pytest; \
		echo "$(GREEN)✅ Инструменты разработки установлены!$(NC)"; \
	else \
		echo "$(RED)❌ Сначала создайте виртуальное окружение: make install$(NC)"; \
	fi

status: info ## Алиас для info

kill-bot: ## Принудительная остановка всех Python процессов бота
	@echo "$(RED)Принудительная остановка всех процессов бота...$(NC)"
	@pkill -9 -f "python.*bot.py" 2>/dev/null && echo "$(GREEN)✅ Все процессы остановлены$(NC)" || echo "$(BLUE)ℹ️  Процессы не найдены$(NC)"

ps-bot: ## Показать запущенные процессы бота
	@echo "$(BLUE)Поиск процессов бота...$(NC)"
	@ps aux | grep -E "(python.*bot\.py|PID)" | grep -v grep || echo "$(YELLOW)⚠️  Процессы бота не найдены$(NC)"

# Справка по умолчанию
.DEFAULT_GOAL := help
