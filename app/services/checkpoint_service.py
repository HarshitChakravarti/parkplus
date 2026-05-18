import re

# Checkpoint type constants
GATE_ENTRY  = "gate_entry"
FLOOR_ENTRY = "floor_entry"
FLOOR_EXIT  = "floor_exit"
GATE_EXIT   = "gate_exit"
UNKNOWN     = "unknown"


def classify_checkpoint(checkpoint: str) -> dict:
    """
    Parse a checkpoint string and return its type and floor (if any).

    Expected formats:
        GATE_ENTRY          → gate_entry
        F{n}_ENTRY          → floor_entry, floor=n
        F{n}_EXIT           → floor_exit,  floor=n
        EXIT_GATE           → gate_exit
    """
    cp = checkpoint.strip().upper()

    if cp == "GATE_ENTRY":
        return {"type": GATE_ENTRY, "floor": None}

    if cp in ("EXIT_GATE", "GATE_EXIT"):
        return {"type": GATE_EXIT, "floor": None}

    match = re.match(r"^F(\d+)_ENTRY$", cp)
    if match:
        return {"type": FLOOR_ENTRY, "floor": int(match.group(1))}

    match = re.match(r"^F(\d+)_EXIT$", cp)
    if match:
        return {"type": FLOOR_EXIT, "floor": int(match.group(1))}

    return {"type": UNKNOWN, "floor": None}


def derive_vehicle_status(checkpoint_type: str) -> str:
    """Map checkpoint type to vehicle status stored in DB."""
    if checkpoint_type == GATE_EXIT:
        return "exited"
    return "inside"

def resolve_state_floor(checkpoint_type: str, event_floor: int | None) -> int | None:
    """
    Determine what floor value should be stored in current_vehicle_state.
    
    FLOOR_EXIT and GATE_EXIT clear the floor.
    GATE_ENTRY has no floor yet.
    FLOOR_ENTRY sets the floor.
    """
    if checkpoint_type in (FLOOR_EXIT, GATE_EXIT, GATE_ENTRY):
        return None
    return event_floor

