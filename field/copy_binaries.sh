#!/usr/bin/env bash
# Простой скрипт для копирования бинарников из проекта-прародителя

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIELD_DIR="$SCRIPT_DIR"
BIN_DIR="$FIELD_DIR/bin"

# Путь к проекту-прародителю (измени на свой путь)
PARENT_PROJECT="${1:-}"

if [ -z "$PARENT_PROJECT" ]; then
    echo "📋 Использование: $0 <путь_к_проекту_прародителю>"
    echo ""
    echo "Пример:"
    echo "  $0 /path/to/parent-project"
    echo "  $0 ~/Downloads/async_field_forever"
    echo ""
    echo "Скрипт скопирует бинарники из:"
    echo "  - \$PARENT_PROJECT/nicole_env/*  →  field/bin/"
    echo "  - \$PARENT_PROJECT/nicole2c/*    →  field/nicole2c/"
    exit 1
fi

if [ ! -d "$PARENT_PROJECT" ]; then
    echo "❌ Ошибка: директория не найдена: $PARENT_PROJECT"
    exit 1
fi

echo "🔧 Копирование бинарников из проекта-прародителя..."
echo "   Источник: $PARENT_PROJECT"
echo "   Назначение: $FIELD_DIR"
echo ""

# Создаем директории
mkdir -p "$BIN_DIR"
mkdir -p "$FIELD_DIR/nicole2c"

# Копируем из nicole_env
PARENT_NICOLE_ENV="$PARENT_PROJECT/nicole_env"
if [ -d "$PARENT_NICOLE_ENV" ]; then
    echo "📦 Копирую из nicole_env/..."
    cp -v "$PARENT_NICOLE_ENV"/* "$BIN_DIR/" 2>/dev/null || true
    chmod +x "$BIN_DIR"/*
    echo "✅ Скопировано в field/bin/"
else
    echo "⚠️  nicole_env не найдена в $PARENT_PROJECT"
fi

# Копируем из nicole2c
PARENT_NICOLE2C="$PARENT_PROJECT/nicole2c"
if [ -d "$PARENT_NICOLE2C" ]; then
    echo "📦 Копирую из nicole2c/..."
    cp -rv "$PARENT_NICOLE2C"/* "$FIELD_DIR/nicole2c/" 2>/dev/null || true
    find "$FIELD_DIR/nicole2c" -type f -exec chmod +x {} \; 2>/dev/null || true
    echo "✅ Скопировано в field/nicole2c/"
else
    echo "⚠️  nicole2c не найдена в $PARENT_PROJECT"
fi

echo ""
echo "✅ Готово! Бинарники скопированы."
echo ""
echo "📁 Структура:"
ls -lh "$BIN_DIR/" 2>/dev/null | grep -v "^total" || echo "   (пусто)"
echo ""
if [ -d "$FIELD_DIR/nicole2c" ]; then
    echo "📁 nicole2c:"
    ls -lh "$FIELD_DIR/nicole2c/" 2>/dev/null | head -5 || echo "   (пусто)"
fi

