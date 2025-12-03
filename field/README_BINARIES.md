# Установка бинарников компиляторов Field

Field использует два компилятора:
- **H2O** - Python компилятор для динамических скриптов
- **Blood** - C компилятор для низкоуровневого контроля

## Структура директорий

```
field/
├── bin/              - Основные бинарники компиляторов
├── nicole_env/       - Бинарники окружения Nicole (из проекта-прародителя)
├── nicole2c/         - Компоненты Clang для C компиляции
├── h2o.py           - Python runtime для H2O (работает без бинарника)
└── blood.py         - C компилятор (использует системный GCC/Clang или бинарники)
```

## Установка бинарников из проекта-прародителя

Если у вас есть доступ к проекту-прародителю с папками `nicole2c` и `nicole_env`:

### 1. Скопируйте бинарники

```bash
# Из проекта-прародителя в поле Field
cp -r /path/to/parent-project/nicole_env/* field/nicole_env/
cp -r /path/to/parent-project/nicole2c/* field/nicole2c/

# Или только нужные бинарники
cp /path/to/parent-project/nicole_env/h2o field/nicole_env/
cp /path/to/parent-project/nicole_env/compiler field/nicole_env/
cp /path/to/parent-project/nicole2c/nicole2c field/nicole2c/
```

### 2. Установите права выполнения

```bash
chmod +x field/nicole_env/*
chmod +x field/nicole2c/*
chmod +x field/bin/*
```

### 3. Запустите скрипт установки

```bash
cd field
./install_binaries.sh
```

## Работа без бинарников (fallback)

Если бинарники не установлены, Field будет работать с fallback:

- **H2O**: использует встроенный Python runtime через `compile()` и `exec()`
- **Blood**: использует системный компилятор (`gcc` или `clang`)

### Проверка системных компиляторов

```bash
# Проверка GCC
which gcc
gcc --version

# Проверка Clang
which clang
clang --version
```

## Приоритет использования компиляторов

### Blood (C компилятор):
1. `field/nicole_env/compiler` - бинарник из проекта-прародителя
2. `field/nicole2c/nicole2c` - компоненты Clang
3. Системный `clang` (если доступен)
4. Системный `gcc` (fallback)

### H2O (Python компилятор):
1. `field/bin/h2o` - бинарник H2O (если есть)
2. `field/nicole_env/h2o` - бинарник из проекта-прародителя
3. Python runtime через `h2o.py` (по умолчанию)

## Проверка установки

После установки бинарников проверьте:

```bash
# Проверка структуры
ls -la field/bin/
ls -la field/nicole_env/
ls -la field/nicole2c/

# Проверка прав выполнения
find field/bin field/nicole_env field/nicole2c -type f -executable
```

## Разработка

Если вы разрабатываете бинарники:

1. Соберите их в соответствующих проектах
2. Скопируйте в `field/bin/` или `field/nicole_env/`
3. Убедитесь что они исполняемые: `chmod +x`
4. Обновите пути в `h2o.py` и `blood.py` при необходимости

## Railway/Docker

При деплое на Railway или в Docker:

1. Добавьте бинарники в репозиторий (или используйте multi-stage build)
2. Убедитесь что они совместимы с целевой платформой (linux/amd64, linux/arm64)
3. Скопируйте бинарники в образ на этапе сборки

## Поддержка

Если бинарники не работают:
- Проверьте права доступа: `chmod +x`
- Проверьте платформу (linux/macos, amd64/arm64)
- Используйте системные компиляторы как fallback
- Смотрите логи в `field/*.log`

