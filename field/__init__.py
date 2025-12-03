"""
Field module — Resonance layer between Trinity and ADAM kernel

The Field creates living feedback loops:
- Monitors system state (repo_monitor)
- Observes Trinity reflections (Kain, Abel)
- Morphs kernel parameters based on dissonance
- Compiles dynamic scripts (h2o, blood)
"""

from .repo_monitor import get_monitor, start_monitoring, RepoMonitor

__all__ = ['get_monitor', 'start_monitoring', 'RepoMonitor']
