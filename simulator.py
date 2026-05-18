import requests
import time
import random
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Pre-registered vehicles — these will receive SMS notifications
REGISTERED_VEHICLES = [
    "MH12AB9999",
    "DL8CAF5032",
    "GJ05CD7890",
    "KA03EF4521",
    "TN09GH8876",
]

# Unknown vehicles — tracked silently, no SMS
UNKNOWN_VEHICLES = [
    "UNKNOWN001",
    "UNKNOWN002",
    "XX99ZZ0001",
]

FLOORS = [1, 2, 3]


def now() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def fire(plate: str, floor: int | None, checkpoint: str, label: str):
    payload = {
        "plate": plate,
        "floor": floor,
        "checkpoint": checkpoint,
        "timestamp": now(),
    }
    try:
        res = requests.post(f"{BASE_URL}/events", json=payload)
        status = "✅" if res.status_code == 201 else f"❌ {res.status_code}"
        floor_label = f"Floor {floor}" if floor else "      "
        print(f"  {status}  {plate:15}  {label:20}  {checkpoint}")
    except Exception as e:
        print(f"  ❌  {plate} — request failed: {e}")


def simulate_journey(plate: str, speed: float = 1.0):
    """
    Full realistic journey:
    GATE_ENTRY → F{n}_ENTRY → (optional floor change) → F{n}_EXIT → EXIT_GATE
    """
    entry_floor = random.choice(FLOORS)

    # 1. Enter facility gate
    fire(plate, None, "GATE_ENTRY", "enters facility")
    time.sleep(1.5 * speed)

    # 2. Enter a floor
    fire(plate, entry_floor, f"F{entry_floor}_ENTRY", f"enters floor {entry_floor}")
    time.sleep(random.uniform(2, 4) * speed)

    # 3. Optional — move to another floor (35% chance)
    current_floor = entry_floor
    if random.random() < 0.35:
        new_floor = random.choice([f for f in FLOORS if f != current_floor])
        fire(plate, None, f"F{current_floor}_EXIT", f"exits floor {current_floor}")
        time.sleep(1.0 * speed)
        fire(plate, new_floor, f"F{new_floor}_ENTRY", f"enters floor {new_floor}")
        time.sleep(random.uniform(2, 4) * speed)
        current_floor = new_floor

    # 4. Exit the floor
    fire(plate, None, f"F{current_floor}_EXIT", f"exits floor {current_floor}")
    time.sleep(1.5 * speed)

    # 5. Exit facility gate
    fire(plate, None, "EXIT_GATE", "exits facility")


def run_simulation(rounds: int = 3, speed: float = 1.0):
    print()
    print("=" * 60)
    print("  ParkPulse — Traffic Simulator")
    print(f"  Rounds: {rounds}   Speed: {speed}x")
    print("  Watch → localhost:8000/demo")
    print("=" * 60)

    for round_num in range(1, rounds + 1):
        print(f"\n── Round {round_num}/{rounds} ──────────────────────────────")

        # Pick a mix of registered and unknown vehicles
        registered_pick = random.sample(REGISTERED_VEHICLES, k=random.randint(2, 3))
        unknown_pick = random.sample(UNKNOWN_VEHICLES, k=random.randint(1, 2))
        all_vehicles = registered_pick + unknown_pick
        random.shuffle(all_vehicles)

        for plate in all_vehicles:
            tag = "[registered]" if plate in REGISTERED_VEHICLES else "[unknown]  "
            print(f"\n🚗 {plate} {tag}")
            simulate_journey(plate, speed=speed)
            time.sleep(random.uniform(1, 2) * speed)

    print("\n" + "=" * 60)
    print("  Simulation complete")
    print("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ParkPulse Traffic Simulator")
    parser.add_argument("--rounds", type=int, default=3, help="Number of rounds")
    parser.add_argument("--speed", type=float, default=1.0, help="Speed multiplier (0.5 = faster, 2.0 = slower)")
    args = parser.parse_args()

    run_simulation(rounds=args.rounds, speed=args.speed)
