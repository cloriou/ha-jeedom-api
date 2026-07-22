import hashlib, json
from .registry import expected_unique_ids

def topology_signature(equipment, selected):
    payload = []
    for eq_id in sorted(selected):
        eq = equipment.get(eq_id)
        payload.append((eq_id, sorted(expected_unique_ids(eq)) if eq else []))
    return hashlib.sha256(json.dumps(payload).encode()).hexdigest()
