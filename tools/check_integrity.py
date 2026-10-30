"""Check release identities and the frozen proof inventory (no integral replay)."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def check_entries(base, entries):
    checked = 0
    for name, spec in entries.items():
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Unsafe manifest path: " + name)
        raw = (base / relative).read_bytes()
        if len(raw) != spec["bytes"] or hashlib.sha256(raw).hexdigest() != spec["sha256"]:
            raise ValueError("Artifact identity mismatch: " + name)
        checked += 1
    return checked


def main():
    manifest = json.loads((ROOT / "artifact-manifest.json").read_text(encoding="utf-8"))
    release_count = check_entries(ROOT, manifest["files"])
    proof = ROOT / "proof"
    inventory = json.loads((proof / "inventory.json").read_text(encoding="utf-8"))
    proof_count = check_entries(proof, inventory["files"])
    print(json.dumps({"status": "PASS_RELEASE_INTEGRITY", "release_files_checked": release_count,
                      "proof_inventory_entries_checked": proof_count,
                      "mathematical_verification_performed": False}))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"status": "FAIL_RELEASE_INTEGRITY", "error": str(error)}), file=sys.stderr)
        sys.exit(1)
