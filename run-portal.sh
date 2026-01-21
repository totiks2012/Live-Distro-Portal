#!/bin/bash

set -e  # Прерывать при любой ошибке

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY_SCRIPT="$SCRIPT_DIR/main-09.py"
VENV_DIR="$SCRIPT_DIR/myenv"

# === 1. Проверка Python 3 и pip ===
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Устанавливаю..."
    sudo apt update
    sudo apt install -y python3 python3-pip
fi

if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 не найден. Устанавливаю..."
    sudo apt update
    sudo apt install -y python3-pip
fi

# === 2. Создание виртуального окружения (если нужно) ===
if [ ! -d "$VENV_DIR" ]; then
    echo "📁 Создаю виртуальное окружение: $VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

# === 3. Активация и установка зависимостей ===
echo "🐍 Активирую виртуальное окружение..."
source "$VENV_DIR/bin/activate"

# Проверим, установлены ли eel и markdown
if ! python3 -c "import eel, markdown" &> /dev/null; then
    echo "📦 Устанавливаю зависимости: eel, markdown..."
    pip3 install --no-cache-dir --upgrade pip
    pip3 install --no-cache-dir eel markdown
else
    echo "✅ Зависимости уже установлены."
fi

# === 4. Запуск скрипта ===
if [ -f "$PY_SCRIPT" ]; then
    echo "🚀 Запускаю LiveDistro Portal..."
    python3 "$PY_SCRIPT"
else
    echo "❌ Ошибка: не найден скрипт $PY_SCRIPT"
    exit 1
fi