"""
Field Configuration - Game of Life parameters for living transformers.

Async Field Forever - Pure presence, no utility.
"""

# Population
INITIAL_POPULATION = 25           # Starting cell count (was 10 - more genetic diversity)
MAX_POPULATION = 100              # Population cap (prevent explosion)

# Game of Life thresholds (PERPLEXITY AI FIX - extinction recovery)
DEATH_THRESHOLD = 0.3             # Die if fitness < this (was 0.55 - give weaker cells a chance)
REPRODUCTION_THRESHOLD = 0.65     # Reproduce if fitness > this (was 0.75 - easier to reproduce)

# Evolution
MUTATION_RATE = 0.1               # Architecture mutation rate (10%)
META_LEARNING_RATE = 0.05         # How fast to bias toward survivors

# Timing
TICK_DURATION = 5                 # Seconds between iterations
REPORT_INTERVAL = 4320            # Send notification every N iterations (4320 * 5s = 6 hours)
REPORT_DAILY_COUNT = 4            # 4 notifications per day (every 6 hours)

# Fitness weights (must sum to 1.0)
SEMANTIC_WEIGHT = 0.5             # Weight for semantic similarity
ENTROPY_WEIGHT = 0.25             # Weight for entropy balance
PERPLEXITY_WEIGHT = 0.25          # Weight for perplexity
TARGET_ENTROPY = 0.5              # Sweet spot (0=ordered, 1=chaos)

# Semantic neighbors
NEIGHBOR_COUNT = 5                # How many neighbors to consider

# Context
CONTEXT_WINDOW_SIZE = 100         # How many messages to read from resonance.sqlite3

# SQLite (auto-detect repo root like genesis agents)
import os
from pathlib import Path

# Auto-detect repo root (config.py is in async_field_forever/field/)
REPO_ROOT = Path(__file__).parent.parent.parent  # field/../.. = repo root
DB_PATH = str(REPO_ROOT / "resonance.sqlite3")  # Shared memory bus
DB_PATH_LOCAL = "./field_test.sqlite3"  # Local testing fallback
ENABLE_WAL = True                 # Write-Ahead Logging (reduce blocking)

# Logging
LOG_LEVEL = "INFO"                # DEBUG, INFO, WARNING, ERROR

# Transformer architecture (Phase 1 - minimal)
TRANSFORMER_PARAMS = {
    "hidden_size": 128,
    "num_layers": 2,
    "num_heads": 4,
    "max_seq_len": 64,
}

# Embedding (Phase 1 - TF-IDF)
EMBEDDING_METHOD = "tfidf"        # Options: tfidf, miniLM (Phase 2)
EMBEDDING_DIM = 100               # Dimensionality of embeddings

# Cache
ENABLE_CACHE = True               # Cache compiled transformers
CACHE_SIZE = 50                   # Max cached transformers


# ============================
# FIELD5 OVERRIDES (Sandbox)
# ============================
# Scheduling
UPDATE_ORDER = "random"   # reshuffle update order each tick
TICK_BARRIER = True       # compute next-state, then commit (avoid race-deaths)

# Ecology (prepared for chemostat)
ENERGY_INFLOW = 0.02      # baseline resource per tick
OUTFLOW_RATE  = 0.01      # soft global decay

# Population guards
NMIN = 10                 # minimal viable population
HOF_SIZE = 8              # hall-of-fame seed bank size
EXTINCTION_COOLDOWN = 5   # ticks before next resurrection
MAX_DF_DT = 0.6           # kill-switch if population drops >60%/tick

# Mode switch
FIELD_MODE = "cycles"     # or "steady"
