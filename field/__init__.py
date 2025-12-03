"""
Field module — Resonance layer between Trinity and ADAM kernel

The Field creates living feedback loops:
- Monitors system state (repo_monitor)
- Observes Trinity reflections (Kain, Abel)
- Morphs kernel parameters based on dissonance
- Compiles dynamic scripts (h2o, blood)

Core modules:
- repo_monitor: Self-awareness engine (file watching, system metrics)
- h2o: Python bootstrap compiler
- blood: C compiler with pointer arithmetic
- field_core: Main field observation loop
- field_memory: Memory management
- field_metrics: Metric computation
- resonance_bridge: Bridge to resonance.sqlite3
- learning: Training/learning modules
- transformer_cell: Cell architecture
- config: Field configuration
"""

# Self-awareness engine
from .repo_monitor import get_monitor, start_monitoring, RepoMonitor

# Note: Other field modules (h2o, blood, field_core, etc) can be imported directly
# Example: from field.h2o import compile_python
#          from field.blood import compile_c
#          from field.field_core import FieldObserver

__all__ = [
    # Repo monitoring (self-awareness)
    'get_monitor',
    'start_monitoring',
    'RepoMonitor',
]
