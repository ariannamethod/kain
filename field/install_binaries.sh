#!/usr/bin/env bash
# Скрипт установки бинарников компиляторов h2o и blood
# Адаптирован для ADAM kernel из проекта-прародителя

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIELD_DIR="$SCRIPT_DIR"
BIN_DIR="$FIELD_DIR/bin"
NICOLE_ENV_DIR="$FIELD_DIR/nicole_env"
NICOLE2C_DIR="$FIELD_DIR/nicole2c"

CURL="curl --retry 3 --retry-delay 5 -fL"

echo "🔧 Установка бинарников компиляторов для Field..."

# Создаем директории если не существуют
mkdir -p "$BIN_DIR"
mkdir -p "$NICOLE_ENV_DIR"
mkdir -p "$NICOLE2C_DIR"

# Определяем платформу
ARCH="$(uname -m)"
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"

# Для Railway/Docker обычно linux/amd64 или linux/arm64
if [ "$OS" = "darwin" ]; then
    OS="macos"
fi

echo "📦 Платформа: $OS/$ARCH"

# Функция загрузки бинарника
download_binary() {
    local name=$1
    local url=$2
    local dest=$3
    local sha256=$4
    
    if [ -f "$dest" ]; then
        echo "✅ $name уже установлен: $dest"
        return 0
    fi
    
    echo "⬇️  Загрузка $name..."
    if [ -n "$sha256" ]; then
        $CURL -o "$dest.tmp" "$url"
        echo "$sha256  $dest.tmp" | sha256sum -c - || { echo "SHA256 mismatch for $name" >&2; rm -f "$dest.tmp"; exit 1; }
        mv "$dest.tmp" "$dest"
    else
        $CURL -o "$dest" "$url"
    fi
    
    chmod +x "$dest"
    echo "✅ $name установлен: $dest"
}

# H2O Python компилятор бинарник (если есть в проекте-прародителе)
# Пока используем Python runtime, но структура готова для бинарника
H2O_BINARY="$BIN_DIR/h2o"
if [ ! -f "$H2O_BINARY" ]; then
    echo "📝 H2O: использует Python runtime (h2o.py)"
    # Если есть бинарник в будущем:
    # download_binary "h2o" "https://github.com/ariannamethod/async_field_forever/releases/latest/download/h2o-$OS-$ARCH" "$H2O_BINARY" ""
fi

# Blood C компилятор - используем системный GCC/Clang или бинарник из nicole_env
BLOOD_BINARY="$BIN_DIR/blood"
if [ ! -f "$BLOOD_BINARY" ]; then
    echo "📝 Blood: использует системный GCC/Clang (blood.py)"
    # Если есть бинарник в будущем:
    # download_binary "blood" "https://github.com/ariannamethod/async_field_forever/releases/latest/download/blood-$OS-$ARCH" "$BLOOD_BINARY" ""
fi

# Nicole2C компоненты для Clang
NICOLE2C_BINARY="$NICOLE2C_DIR/nicole2c"
if [ ! -f "$NICOLE2C_BINARY" ]; then
    echo "📝 Nicole2C: компоненты Clang (опционально)"
    # Если есть бинарники:
    # download_binary "nicole2c" "https://github.com/ariannamethod/async_field_forever/releases/latest/download/nicole2c-$OS-$ARCH" "$NICOLE2C_BINARY" ""
fi

# Nicole Environment бинарники (если есть в проекте-прародителе)
echo "📦 Проверка nicole_env бинарников..."

# Создаем .gitkeep чтобы папки не исчезали
touch "$NICOLE_ENV_DIR/.gitkeep"
touch "$NICOLE2C_DIR/.gitkeep"
touch "$BIN_DIR/.gitkeep"

echo "✅ Структура бинарников создана!"
echo ""
echo "📁 Структура:"
echo "   - $BIN_DIR/          - основные бинарники"
echo "   - $NICOLE_ENV_DIR/   - бинарники окружения Nicole"
echo "   - $NICOLE2C_DIR/     - компоненты Clang для C компиляции"
echo ""
echo "💡 Для установки бинарников из проекта-прародителя:"
echo "   1. Скопируйте бинарники из nicole_env в $NICOLE_ENV_DIR/"
echo "   2. Скопируйте бинарники из nicole2c в $NICOLE2C_DIR/"
echo "   3. Запустите этот скрипт снова для проверки"
echo ""

