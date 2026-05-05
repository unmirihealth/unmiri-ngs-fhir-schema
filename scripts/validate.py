#!/usr/bin/env python3
"""
validate.py — validate every JSON file in examples/ against the JSON Schemas
in schemas/ and against the pydantic v2 models in types/python/.

Usage:
    python3 -m pip install jsonschema pydantic
    python3 scripts/validate.py

Exit code is non-zero if any example fails either validator. Both validators
are run because they catch slightly different things: JSON Schema enforces
patterns and required fields, pydantic enforces the same plus type-system
invariants the schema cannot easily express.
"""
from __future__ import annotations

import glob
import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent.parent


def validate_jsonschema() -> int:
    from jsonschema import Draft202012Validator
    from jsonschema.validators import RefResolver

    schemas = {}
    for p in sorted((ROOT / "schemas").glob("*.json")):
        s = json.loads(p.read_text())
        schemas[s["$id"]] = s

    root_id = "https://schemas.unmiri.com/ngs-interpretation/v0/ngs-interpretation-response.schema.json"
    resolver = RefResolver(base_uri=root_id, referrer=schemas[root_id], store=schemas)
    validator = Draft202012Validator(schemas[root_id], resolver=resolver)

    fail = 0
    for ex in sorted((ROOT / "examples").glob("*.json")):
        payload = json.loads(ex.read_text())
        errs = list(validator.iter_errors(payload))
        if errs:
            fail += 1
            print(f"  jsonschema FAIL: {ex.name}")
            for e in errs[:5]:
                path = "/".join(str(x) for x in e.absolute_path)
                print(f"    - /{path}: {e.message}")
    return fail


def validate_pydantic() -> int:
    sys.path.insert(0, str(ROOT / "types" / "python"))
    from unmiri_ngs_interpretation import NgsInterpretationResponse  # noqa: E402

    fail = 0
    for ex in sorted((ROOT / "examples").glob("*.json")):
        payload = json.loads(ex.read_text())
        try:
            NgsInterpretationResponse.model_validate(payload)
        except Exception as e:  # noqa: BLE001
            fail += 1
            print(f"  pydantic FAIL: {ex.name}: {type(e).__name__}: {str(e)[:200]}")
    return fail


def main() -> int:
    print("Validating against JSON Schemas...")
    js_fail = validate_jsonschema()
    print("Validating against pydantic models...")
    py_fail = validate_pydantic()
    total_examples = len(list((ROOT / "examples").glob("*.json")))
    if js_fail == 0 and py_fail == 0:
        print(f"\n✓ {total_examples} examples passed both validators.")
        return 0
    print(f"\n✗ {js_fail} JSON Schema failures, {py_fail} pydantic failures.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
