import requests

BASE_URL = "http://localhost:8000"

# Clean registered vehicle database for demos
SEED_VEHICLES = [
    {
        "plate_number": "MH12AB9999",
        "owner_phone": "+917042332006",
        "vehicle_type": "Sedan",
    },
    {
        "plate_number": "DL8CAF5032",
        "owner_phone": "+919876543210",
        "vehicle_type": "SUV",
    },
    {
        "plate_number": "GJ05CD7890",
        "owner_phone": "+917654321098",
        "vehicle_type": "Hatchback",
    },
    {
        "plate_number": "KA03EF4521",
        "owner_phone": "+916543210987",
        "vehicle_type": "Sedan",
    },
    {
        "plate_number": "TN09GH8876",
        "owner_phone": "+915432109876",
        "vehicle_type": "SUV",
    },
]


def register_vehicle(vehicle: dict) -> bool:
    res = requests.post(f"{BASE_URL}/vehicles/register", json=vehicle)
    if res.status_code == 201:
        print(f"  ✅  {vehicle['plate_number']:15}  {vehicle['vehicle_type']:12}  {vehicle['owner_phone']}")
        return True
    else:
        print(f"  ❌  {vehicle['plate_number']} — {res.status_code} {res.text}")
        return False


def run_seed():
    print()
    print("=" * 55)
    print("  ParkPulse — Seed Script")
    print("=" * 55)
    print(f"\nRegistering {len(SEED_VEHICLES)} vehicles...\n")

    success = sum(register_vehicle(v) for v in SEED_VEHICLES)

    print(f"\n{success}/{len(SEED_VEHICLES)} vehicles registered")

    print("\nVerifying via GET /vehicles/MH12AB9999...")
    res = requests.get(f"{BASE_URL}/vehicles/MH12AB9999")
    if res.ok:
        d = res.json()
        print(f"  plate:  {d['plate']}")
        print(f"  status: {d['status']}")
        print(f"  floor:  {d['current_floor']}")
    else:
        print(f"  ❌ Lookup failed: {res.status_code}")

    print()
    print("Seed complete. Ready to simulate.")
    print("=" * 55)


if __name__ == "__main__":
    run_seed()
