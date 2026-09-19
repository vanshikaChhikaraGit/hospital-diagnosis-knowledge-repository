"""
repository_tools.py - Load, validate and search the Hospital Knowledge Repository.

Usage:
    python repository_tools.py                  -> validate all files + print summary
    python repository_tools.py search <word>    -> keyword search across all files
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).parent
REQUIRED_KEYS = ("domain", "category", "version")


def load_all():
    """Read every .json knowledge file in the repository folder."""
    data = {}
    for path in sorted(REPO.glob("*.json")):
        with open(path, encoding="utf-8") as f:
            data[path.name] = json.load(f)
    return data


def validate(data):
    """Run consistency checks. Returns a list of (check_name, list_of_errors)."""
    ids = lambda file, key: {item["id"] for item in data[file][key]}
    symptoms = ids("symptom_knowledge.json", "symptoms")
    diseases = ids("disease_knowledge.json", "diseases")
    treatments = ids("treatment_knowledge.json", "treatments")
    doctors = ids("doctor_department_knowledge.json", "doctors")
    depts = ids("doctor_department_knowledge.json", "departments")
    maps = data["relationship_knowledge.json"]["mappings"]
    checks = []

    errs = [f"{fn}: missing '{k}'" for fn, doc in data.items() for k in REQUIRED_KEYS if k not in doc]
    checks.append(("Every file has domain, category and version", errs))

    errs = []
    for r in data["diagnosis_rules.json"]["rules"]:
        errs += [f"{r['id']}: unknown symptom {s}" for s in r["if"] if s not in symptoms]
        if r["then"] not in diseases:
            errs.append(f"{r['id']}: unknown disease {r['then']}")
    checks.append(("Diagnosis rules refer to valid symptoms and diseases", errs))

    errs = [f"{d}: no treatment" for d in diseases
            if not set(maps["disease_treated_by"].get(d, [])) & treatments]
    checks.append(("Every disease has a valid treatment", errs))

    errs = [f"{d}: no valid department" for d in diseases
            if maps["disease_handled_by_department"].get(d) not in depts]
    checks.append(("Every disease is handled by a valid department", errs))

    errs = [f"{d['id']}: head doctor {d['head_doctor']} not found"
            for d in data["doctor_department_knowledge.json"]["departments"]
            if d["head_doctor"] not in doctors]
    checks.append(("Every department head is a valid doctor", errs))

    errs = [f"{s}: unknown disease {d}" for s, ds in maps["symptom_indicates_disease"].items()
            for d in ds if d not in diseases or s not in symptoms]
    checks.append(("Symptom-disease mapping uses valid IDs", errs))
    return checks


def summary(data):
    """Count the knowledge items stored in each file."""
    for name, doc in data.items():
        counts = [f"{len(v)} {k}" for k, v in doc.items() if isinstance(v, list)]
        print(f"  {name:<34} v{doc['version']}  {doc['category']:<34} {', '.join(counts)}")


def walk(obj, path=""):
    """Yield (path, text) for every string value inside a JSON structure."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield path, obj


def search(data, word):
    print(f"Search results for '{word}':")
    found = 0
    for name, doc in data.items():
        for path, text in walk(doc):
            if word.lower() in text.lower():
                print(f"  {name}  {path}  ->  {text}")
                found += 1
    print(f"{found} match(es) found.")


if __name__ == "__main__":
    repo_data = load_all()
    if len(sys.argv) >= 3 and sys.argv[1] == "search":
        search(repo_data, sys.argv[2])
    else:
        print(f"Loaded {len(repo_data)} knowledge files from '{REPO.name}'")
        summary(repo_data)
        print("\nVALIDATION")
        failed = 0
        for check, errors in validate(repo_data):
            print(f"  [{'PASS' if not errors else 'FAIL'}] {check}")
            for e in errors:
                print(f"         - {e}")
            failed += bool(errors)
        print("\nRepository is consistent." if not failed else f"\n{failed} check(s) failed.")
