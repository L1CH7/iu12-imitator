#!/bin/bash
set -e

# Проверяем наличие .venv
if [ ! -d ".venv" ]; then
    echo "=== Создание виртуального окружения ==="
    uv venv .venv
fi

source .venv/bin/activate

# Проверяем, нужно ли устанавливать зависимости через md5-хеш requirements.txt
REQ_HASH_FILE=".venv/requirements.hash"
CURRENT_HASH=$(md5sum requirements.txt | awk '{print $1}')

if [ ! -f "$REQ_HASH_FILE" ] || [ "$CURRENT_HASH" != "$(cat $REQ_HASH_FILE)" ]; then
    echo "=== Установка зависимостей через uv pip ==="
    uv pip install -r requirements.txt
    echo "$CURRENT_HASH" > "$REQ_HASH_FILE"
else
    echo "=== Зависимости актуальны (пропущено) ==="
fi

echo "=== Запуск Streamlit ==="
streamlit run app.py

