"""
Repository Monitor: SHA256-based change detection

Сканирует config/ и README.md по SHA256 хешам.
Триггерит переиндексацию в SQLite vector store при изменениях.
"""

import os
import hashlib
import json
import asyncio
from pathlib import Path
from typing import Dict, Set, Optional

from utils.logging import get_logger

logger = get_logger(__name__)

# Путь к файлу с сохраненными хешами
HASHES_FILE = "data/repo_hashes.json"

# Директории и файлы для мониторинга
WATCH_DIRS = ["config"]
WATCH_FILES = ["README.md"]


def calculate_sha256(filepath: str) -> str:
    """
    Вычислить SHA256 хеш файла.

    Parameters
    ----------
    filepath : str
        Путь к файлу

    Returns
    -------
    str
        SHA256 хеш в hex формате
    """
    sha256 = hashlib.sha256()

    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        logger.warning("Failed to hash %s: %s", filepath, e)
        return ""


def scan_repository() -> Dict[str, str]:
    """
    Сканировать репозиторий и собрать хеши всех отслеживаемых файлов.

    Returns
    -------
    Dict[str, str]
        Словарь {filepath: sha256_hash}
    """
    hashes = {}

    # Сканируем директории
    for watch_dir in WATCH_DIRS:
        if not os.path.isdir(watch_dir):
            logger.warning("Watch directory not found: %s", watch_dir)
            continue

        for root, _, files in os.walk(watch_dir):
            for filename in files:
                # Только markdown файлы
                if not filename.endswith('.md'):
                    continue

                filepath = os.path.join(root, filename)
                file_hash = calculate_sha256(filepath)
                if file_hash:
                    hashes[filepath] = file_hash

    # Сканируем отдельные файлы
    for watch_file in WATCH_FILES:
        if os.path.isfile(watch_file):
            file_hash = calculate_sha256(watch_file)
            if file_hash:
                hashes[watch_file] = file_hash
        else:
            logger.debug("Watch file not found: %s", watch_file)

    return hashes


def load_saved_hashes() -> Dict[str, str]:
    """
    Загрузить сохраненные хеши из файла.

    Returns
    -------
    Dict[str, str]
        Словарь {filepath: sha256_hash} или пустой словарь
    """
    if not os.path.exists(HASHES_FILE):
        return {}

    try:
        with open(HASHES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error("Failed to load saved hashes: %s", e)
        return {}


def save_hashes(hashes: Dict[str, str]) -> None:
    """
    Сохранить хеши в файл.

    Parameters
    ----------
    hashes : Dict[str, str]
        Словарь {filepath: sha256_hash}
    """
    # Создать директорию data/ если не существует
    Path(HASHES_FILE).parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(HASHES_FILE, 'w', encoding='utf-8') as f:
            json.dump(hashes, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error("Failed to save hashes: %s", e)


def detect_changes(
    current_hashes: Dict[str, str],
    saved_hashes: Dict[str, str]
) -> tuple[Set[str], Set[str], Set[str]]:
    """
    Определить изменения между текущими и сохраненными хешами.

    Parameters
    ----------
    current_hashes : Dict[str, str]
        Текущие хеши
    saved_hashes : Dict[str, str]
        Сохраненные хеши

    Returns
    -------
    tuple[Set[str], Set[str], Set[str]]
        (added, modified, deleted) - множества путей файлов
    """
    current_files = set(current_hashes.keys())
    saved_files = set(saved_hashes.keys())

    # Новые файлы
    added = current_files - saved_files

    # Удаленные файлы
    deleted = saved_files - current_files

    # Измененные файлы (существуют в обоих, но хеш отличается)
    modified = {
        filepath
        for filepath in current_files & saved_files
        if current_hashes[filepath] != saved_hashes[filepath]
    }

    return added, modified, deleted


async def check_repository_changes(
    vector_store=None,
    force_reindex: bool = False
) -> bool:
    """
    Проверить изменения в репозитории и триггернуть переиндексацию если нужно.

    Parameters
    ----------
    vector_store : Optional
        SQLite vector store для переиндексации
    force_reindex : bool
        Если True, переиндексировать в любом случае

    Returns
    -------
    bool
        True если были изменения (или force_reindex), False иначе
    """
    logger.debug("Checking repository changes...")

    # Текущие хеши (async wrapper for os.walk + file I/O)
    current_hashes = await asyncio.to_thread(scan_repository)

    if force_reindex:
        logger.info("Force reindex requested")
        if vector_store:
            try:
                await vector_store.vectorize_all_files(force=True)
                # Only save hashes after successful reindexing (async wrapper for json.dump)
                await asyncio.to_thread(save_hashes, current_hashes)
            except Exception as e:
                logger.error("Force reindex failed: %s", e, exc_info=True)
                raise
        else:
            await asyncio.to_thread(save_hashes, current_hashes)
        return True

    # Сохраненные хеши (async wrapper for json.load)
    saved_hashes = await asyncio.to_thread(load_saved_hashes)

    # Первый запуск - нет сохраненных хешей
    if not saved_hashes:
        logger.info("First run - creating initial snapshot")
        if vector_store:
            try:
                await vector_store.vectorize_all_files(force=True)
                # Only save hashes after successful reindexing (async wrapper for json.dump)
                await asyncio.to_thread(save_hashes, current_hashes)
            except Exception as e:
                logger.error("Initial indexing failed: %s", e, exc_info=True)
                raise
        else:
            await asyncio.to_thread(save_hashes, current_hashes)
        return True

    # Определяем изменения
    added, modified, deleted = detect_changes(current_hashes, saved_hashes)

    if not (added or modified or deleted):
        logger.debug("No changes detected")
        return False

    # Логируем изменения
    if added:
        logger.info("Added files: %s", ", ".join(added))
    if modified:
        logger.info("Modified files: %s", ", ".join(modified))
    if deleted:
        logger.info("Deleted files: %s", ", ".join(deleted))

    # Триггерим переиндексацию
    if vector_store:
        logger.info("Triggering vector store reindexing...")
        try:
            await vector_store.vectorize_all_files(force=True)
            # Only save hashes after successful reindexing (async wrapper for json.dump)
            await asyncio.to_thread(save_hashes, current_hashes)
        except Exception as e:
            logger.error("Reindexing failed: %s", e, exc_info=True)
            raise
    else:
        # No vector store - just save hashes (async wrapper for json.dump)
        await asyncio.to_thread(save_hashes, current_hashes)

    return True


async def monitor_loop(
    vector_store=None,
    interval: int = 300
) -> None:
    """
    Основной loop мониторинга (для фоновой задачи).

    Parameters
    ----------
    vector_store : Optional
        SQLite vector store
    interval : int
        Интервал проверки в секундах (по умолчанию 5 минут)
    """
    logger.info("Repository monitor started (interval: %ds)", interval)

    while True:
        try:
            await check_repository_changes(vector_store)
        except Exception as e:
            logger.error("Repository monitor error: %s", e, exc_info=True)

        await asyncio.sleep(interval)
