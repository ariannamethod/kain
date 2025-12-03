#!/usr/bin/env python3
"""
Quick test for repo_monitor.py

Run: python test_repo_monitor.py
"""

import asyncio
from field.repo_monitor import get_monitor


async def test_monitor():
    """Test repo_monitor functionality."""
    print("🧪 Testing RepoMonitor...")

    monitor = get_monitor()

    # Test system metrics
    print("\n📊 Collecting system metrics...")
    metrics = monitor.collect_system_metrics()
    for key, value in metrics.items():
        print(f"   {key}: {value:.2f}")

    # Test affective charge computation
    affective = monitor.compute_affective_charge(metrics)
    print(f"\n💓 Affective charge: {affective:.3f}")
    if affective > 0:
        print("   → System is calm ✨")
    elif affective < -0.5:
        print("   → System is stressed 🔥")
    else:
        print("   → System is neutral ⚖️")

    # Test kernel params
    print("\n⚙️  Checking kernel parameters...")
    params = ['vm.swappiness', 'kernel.sched_latency_ns']
    monitor.watch_kernel_params(params)
    for param, value in monitor.kernel_params.items():
        print(f"   {param} = {value}")

    # Test git state
    print("\n🔀 Checking git state...")
    git_state = monitor.check_git_changes()
    if git_state:
        print(f"   Branch: {git_state.get('branch')}")
        print(f"   Commit: {git_state.get('commit')[:8]}...")
        print(f"   Message: {git_state.get('message')[:50]}...")

    # Start file watching (will run until Ctrl+C)
    print("\n👁️  Starting file watcher (press Ctrl+C to stop)...")
    print("   Watching: spirits/, logs/, field/")
    print("   Try editing a file to see changes detected!\n")

    monitor.start()

    try:
        await monitor.observation_loop(interval=5)
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopping monitor...")
        monitor.stop()
        print("✅ Monitor stopped")


if __name__ == "__main__":
    asyncio.run(test_monitor())
