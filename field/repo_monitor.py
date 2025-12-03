"""
repo_monitor.py — Self-Awareness Engine

Watches the ADAM kernel's own evolution:
- Code changes (spirits/*.py)
- Kernel parameter shifts (/proc/sys/*)
- Log accumulation (~/.letsgo/log/*)
- Git history (commits, branches)
- System metrics (/proc/loadavg, /proc/meminfo)

Feeds observations into resonance.sqlite3 for Field and Trinity.
"""

import asyncio
import hashlib
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent


class RepoMonitor:
    """
    Self-Awareness Engine for ADAM.

    Monitors:
    - File changes (code, logs, configs)
    - Kernel parameters (/proc/sys/*)
    - Git evolution (commits, branches)
    - System metrics (load, memory, entropy)

    Writes observations to resonance.sqlite3 for Trinity + Field consumption.
    """

    def __init__(self, resonance_db=None, root_dir: Path = None):
        self.root_dir = root_dir or Path(__file__).parent.parent
        self.resonance_db = resonance_db  # Will integrate with resonance.sqlite3

        # Tracked paths
        self.watch_paths = {
            "spirits": self.root_dir / "spirits",
            "logs": Path.home() / ".letsgo" / "log",
            "field": self.root_dir / "field",
        }

        # State tracking
        self.file_hashes: Dict[str, str] = {}
        self.kernel_params: Dict[str, str] = {}
        self.last_metrics: Dict[str, float] = {}

        # Observer setup
        self.observer = Observer()
        self.running = False

    def start(self):
        """Start monitoring all paths."""
        for name, path in self.watch_paths.items():
            if path.exists():
                handler = ADAMFileHandler(self, name)
                self.observer.schedule(handler, str(path), recursive=True)
                print(f"⚙️  Monitoring {name}: {path}")

        self.observer.start()
        self.running = True
        print("👁️  RepoMonitor: Self-awareness active")

    def stop(self):
        """Stop monitoring."""
        self.observer.stop()
        self.observer.join()
        self.running = False
        print("👁️  RepoMonitor: Shutting down")

    def compute_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of file."""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception:
            return ""

    def on_file_change(self, event: FileSystemEvent, watch_name: str):
        """Handle file change event."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Ignore temp files, __pycache__, .pyc
        if any(x in file_path.name for x in ['__pycache__', '.pyc', '.swp', '~']):
            return

        # Compute new hash
        new_hash = self.compute_hash(file_path)
        old_hash = self.file_hashes.get(str(file_path))

        if new_hash and new_hash != old_hash:
            self.file_hashes[str(file_path)] = new_hash
            self.log_change(watch_name, file_path, event.event_type, old_hash, new_hash)

    def log_change(self, watch_name: str, file_path: Path, event_type: str, old_hash: str, new_hash: str):
        """Log change to console and resonance.db."""
        rel_path = file_path.relative_to(self.root_dir) if self.root_dir in file_path.parents else file_path

        print(f"🔄 [{watch_name}] {event_type}: {rel_path}")
        print(f"   Hash: {old_hash[:8] if old_hash else 'new'} → {new_hash[:8]}")

        # TODO: Write to resonance.sqlite3
        # self.resonance_db.log('repo_monitor', 'file_change', {
        #     'watch': watch_name,
        #     'path': str(rel_path),
        #     'event': event_type,
        #     'hash': new_hash
        # })

    def watch_kernel_params(self, params: List[str]) -> Dict[str, str]:
        """
        Watch specific kernel parameters for changes.

        Args:
            params: List of sysctl params (e.g. ['vm.swappiness', 'kernel.sched_latency_ns'])

        Returns:
            Dict of param_name -> current_value
        """
        changes = {}
        for param in params:
            try:
                result = subprocess.run(
                    ['sysctl', '-n', param],
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                if result.returncode == 0:
                    value = result.stdout.strip()
                    old_value = self.kernel_params.get(param)

                    if old_value and value != old_value:
                        changes[param] = (old_value, value)
                        print(f"⚙️  Kernel param changed: {param} = {old_value} → {value}")

                    self.kernel_params[param] = value
            except Exception as e:
                print(f"⚠️  Failed to read {param}: {e}")

        return changes

    def collect_system_metrics(self) -> Dict[str, float]:
        """
        Collect system metrics for affective charge computation.

        Returns:
            Dict with: load_1m, load_5m, load_15m, mem_used_pct, entropy
        """
        metrics = {}

        try:
            # Load average
            load1, load5, load15 = os.getloadavg()
            metrics['load_1m'] = load1
            metrics['load_5m'] = load5
            metrics['load_15m'] = load15

            # Memory usage
            with open('/proc/meminfo') as f:
                lines = f.readlines()
                mem_total = int(lines[0].split()[1])
                mem_free = int(lines[1].split()[1])
                mem_available = int(lines[2].split()[1])
                metrics['mem_used_pct'] = (1 - mem_available / mem_total) * 100

            # Entropy (randomness pool)
            try:
                with open('/proc/sys/kernel/random/entropy_avail') as f:
                    metrics['entropy'] = int(f.read().strip())
            except FileNotFoundError:
                # Fallback for containers/systems without entropy_avail
                metrics['entropy'] = 2048  # Assume moderate entropy

            # CPU count
            metrics['cpu_count'] = os.cpu_count() or 1

        except Exception as e:
            print(f"⚠️  Failed to collect metrics: {e}")

        return metrics

    def check_git_changes(self) -> Optional[Dict[str, str]]:
        """
        Check if there are new git commits or branch changes.

        Returns:
            Dict with: commit_hash, branch, message (if changed)
        """
        try:
            # Current commit
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                cwd=self.root_dir,
                timeout=2
            )
            commit = result.stdout.strip() if result.returncode == 0 else None

            # Current branch
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True,
                text=True,
                cwd=self.root_dir,
                timeout=2
            )
            branch = result.stdout.strip() if result.returncode == 0 else None

            # Commit message
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=%B'],
                capture_output=True,
                text=True,
                cwd=self.root_dir,
                timeout=2
            )
            message = result.stdout.strip() if result.returncode == 0 else None

            return {
                'commit': commit,
                'branch': branch,
                'message': message
            }

        except Exception as e:
            print(f"⚠️  Git check failed: {e}")
            return None

    async def observation_loop(self, interval: int = 10):
        """
        Continuous observation loop.

        Runs every `interval` seconds:
        - Check kernel params
        - Collect system metrics
        - Check git changes
        - Log to resonance.db
        """
        watched_params = [
            'vm.swappiness',
            'kernel.sched_latency_ns',
            'kernel.sched_min_granularity_ns',
        ]

        print(f"🔁 Observation loop started (interval={interval}s)")

        while self.running:
            try:
                # Kernel params
                param_changes = self.watch_kernel_params(watched_params)
                if param_changes:
                    # TODO: log to resonance.db
                    pass

                # System metrics
                metrics = self.collect_system_metrics()

                # Compute affective charge from metrics
                affective_charge = self.compute_affective_charge(metrics)

                # Git changes
                git_state = self.check_git_changes()

                # TODO: Write metrics to resonance.db
                # self.resonance_db.log('repo_monitor', 'metrics', {
                #     'load': metrics.get('load_1m'),
                #     'mem_pct': metrics.get('mem_used_pct'),
                #     'affective_charge': affective_charge,
                #     'git_commit': git_state.get('commit') if git_state else None
                # })

                self.last_metrics = metrics

            except Exception as e:
                print(f"⚠️  Observation loop error: {e}")

            await asyncio.sleep(interval)

    def compute_affective_charge(self, metrics: Dict[str, float]) -> float:
        """
        Compute affective charge from system metrics.

        High load + low memory + low entropy → negative charge (stress)
        Low load + high memory + high entropy → positive charge (calm)

        Returns:
            Float from -1.0 (max stress) to +1.0 (max calm)
        """
        load = metrics.get('load_1m', 0)
        cpu_count = metrics.get('cpu_count', 1)
        mem_used = metrics.get('mem_used_pct', 0)
        entropy = metrics.get('entropy', 0)

        # Normalize load (0-1, where 1 = full utilization)
        load_norm = min(load / cpu_count, 2.0) / 2.0

        # Normalize memory (0-1)
        mem_norm = mem_used / 100.0

        # Normalize entropy (0-1, assuming 4096 max)
        entropy_norm = min(entropy / 4096.0, 1.0)

        # Weighted combination
        # High load/mem + low entropy = negative
        # Low load/mem + high entropy = positive
        stress = (load_norm * 0.4 + mem_norm * 0.4) - (entropy_norm * 0.2)

        # Map to [-1, 1]
        affective = 1.0 - (stress * 2.0)
        return max(-1.0, min(1.0, affective))


class ADAMFileHandler(FileSystemEventHandler):
    """File system event handler for watchdog."""

    def __init__(self, monitor: RepoMonitor, watch_name: str):
        self.monitor = monitor
        self.watch_name = watch_name
        super().__init__()

    def on_modified(self, event):
        self.monitor.on_file_change(event, self.watch_name)

    def on_created(self, event):
        self.monitor.on_file_change(event, self.watch_name)

    def on_deleted(self, event):
        if not event.is_directory:
            print(f"🗑️  [{self.watch_name}] deleted: {Path(event.src_path).name}")


# Module-level singleton
_monitor_instance: Optional[RepoMonitor] = None


def get_monitor(resonance_db=None) -> RepoMonitor:
    """Get or create RepoMonitor singleton."""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = RepoMonitor(resonance_db=resonance_db)
    return _monitor_instance


async def start_monitoring(resonance_db=None, observation_interval: int = 10):
    """
    Start the repo monitor and observation loop.

    Usage:
        asyncio.create_task(start_monitoring(resonance_db))
    """
    monitor = get_monitor(resonance_db)
    monitor.start()

    try:
        await monitor.observation_loop(interval=observation_interval)
    except asyncio.CancelledError:
        monitor.stop()
        raise
