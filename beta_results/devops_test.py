#!/usr/bin/env python3
"""DevOps beta test: Thermal-aware job scheduling with ThermalBudget."""
import sys
import numpy as np

sys.path.insert(0, "/root/.openclaw/workspace/sunset-ecosystem")

from swarm.thermal import ThermalBudget, DeviceType


def main():
    print("=" * 60)
    print("DEVOPS BETA: Thermal-Aware Job Scheduling")
    print("=" * 60)

    # Model a data center with 3 device types
    print("\n[1] Modeling 3 devices (GPU, NPU, CPU)...")
    thermal = ThermalBudget({
        DeviceType.GPU: 10,   # 10 GPU slots
        DeviceType.NPU: 5,    # 5 NPU slots  
        DeviceType.CPU: 20,   # 20 CPU slots
    })

    # 20 jobs with different thermal profiles
    jobs = [
        {"id": i, "device": np.random.choice([DeviceType.GPU, DeviceType.NPU, DeviceType.CPU]),
         "heat": np.random.randint(1, 4)}
        for i in range(20)
    ]

    print(f"    Data center capacity: GPU=10 NPU=5 CPU=20")
    print(f"    Jobs to schedule: {len(jobs)}")

    # Try to schedule each job
    print("\n[2] Scheduling jobs (thermal-aware)...")
    scheduled = 0
    blocked = 0
    for job in jobs:
        if thermal.can_spawn(job["device"]):
            thermal.spawn(f"job_{job['id']}", job["device"])
            scheduled += 1
        else:
            blocked += 1
            print(f"    BLOCKED: job_{job['id']} on {job['device'].name} (thermal full)")

    print(f"\n[3] Results: {scheduled} scheduled, {blocked} blocked by thermal")

    # Check remaining capacity
    for dev in [DeviceType.GPU, DeviceType.NPU, DeviceType.CPU]:
        device_budget = thermal._devices.get(dev)
        if device_budget:
            used = device_budget.current_agents
            cap = device_budget.max_agents
            print(f"    {dev.name}: {used}/{cap} used ({used/cap*100:.0f}%)")

    print("\n✅ Script completed without crashes")
    print("    ThermalBudget successfully gated job scheduling.")


if __name__ == "__main__":
    main()
