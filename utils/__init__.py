"""
Utils package — Универсальные утилиты для ADAM kernel

Модули:
- repo_monitor: SHA256-based мониторинг репозитория
- agent_logic: Универсальная логика для всех агентов
- context_neural_processor: Нейропроцессор контекста
- vector_store: SQLite векторное хранилище для embeddings
"""

# Import specific functions/classes as they become available
# Users can import directly from submodules if needed
__all__ = [
    'repo_monitor',
    'agent_logic',
    'context_neural_processor',
    'vector_store',
    'logging',
]

