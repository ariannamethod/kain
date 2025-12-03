# Установка бинарников компиляторов Field

Field использует два компилятора:
- **H2O** - Python компилятор для динамических скриптов
- **Blood** - C компилятор для низкоуровневого контроля

## Структура

```
field/
├── bin/        - Бинарники компиляторов (скопируй сюда из проекта-прародителя)
├── nicole2c/   - Компоненты Clang (если есть)
├── h2o.py      - Python runtime для H2O (работает без бинарника)
└── blood.py    - C компилятор (использует системный GCC/Clang или бинарники)
```

## Установка бинарников

Просто скопируй бинарники из проекта-прародителя:

```bash
# Вариант 1: Используй скрипт
cd field
./copy_binaries.sh /path/to/parent-project

# Вариант 2: Скопируй вручную
cp /path/to/parent-project/nicole_env/* field/bin/
cp -r /path/to/parent-project/nicole2c/* field/nicole2c/

# Установи права
chmod +x field/bin/*
chmod +x field/nicole2c/*
```

Готово! Бинарники в репозитории, всё работает.

## Работа без бинарников (fallback)

Если бинарников нет, всё равно работает:
- **H2O**: Python runtime через `h2o.py`
- **Blood**: системный `gcc` или `clang`

## Проверка

```bash
ls -lh field/bin/
ls -lh field/nicole2c/
```

