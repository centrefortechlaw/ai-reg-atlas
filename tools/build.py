#!/usr/bin/env python3
"""Regenerate the atlas data embedded in index.html from data/*.json.

Run from the repository root:  python3 tools/build.py
It validates every plate against the CTL codebook vocabularies, rewrites the block
between the DATA:BEGIN and DATA:END markers in index.html, and writes
data/atlas-register.csv (one row per instrument, for the cross-plate heatmaps).
"""
import csv, html, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
INDEX = ROOT / "index.html"

STATUS = {"Binding", "Soft law", "Proposed"}
TYPES = {"Statute", "Subordinate rules", "Regulator guidance", "Advisory", "Technical standard", "Bill"}
ACTORS = {"Developer", "Deployer", "Platform", "User", "State"}
DUTIES = {"Transparency", "Labelling", "Risk management", "Impact assessment", "Audit",
          "Human oversight", "Data governance", "Registration or filing", "Prohibition"}
RIGHTS = {"Notice", "Explanation", "Contestation", "Human review", "None"}
MODELS = {"Comprehensive statute", "Sectoral", "Soft-law-led", "Hybrid"}
STATUS_ORDER = {"Binding": 0, "Soft law": 1, "Proposed": 2}

errors = []

def err(where, msg):
    errors.append(f"{where}: {msg}")

def check_list(where, field, value, allowed):
    items = [x.strip() for x in value.split(";") if x.strip()]
    if not items:
        err(where, f"{field} is empty")
    for x in items:
        if x not in allowed:
            err(where, f"{field} has '{x}', not in the codebook vocabulary")
    if field == "rights" and "None" in items and len(items) > 1:
        err(where, "rights combines None with other values")

def esc(s):
    return html.escape(str(s), quote=True)

def year_key(y):
    m = re.match(r"\d{4}", y)
    return int(m.group()) if m else 9999

jurisdictions = json.loads((DATA_DIR / "jurisdictions.json").read_text(encoding="utf-8"))
known = {j["id"] for j in jurisdictions}

plates, instruments, csv_rows = {}, [], []
for path in sorted((DATA_DIR / "plates").glob("*.json")):
    p = json.loads(path.read_text(encoding="utf-8"))
    jid = p["plate"]
    w = f"plate {jid}"
    if jid not in known:
        err(w, "plate id is not in data/jurisdictions.json")
    insts = p["instruments"]
    if not 5 <= len(insts) <= 12:
        err(w, f"{len(insts)} instruments (codebook requires 5 to 12)")
    if p["governance_model"] not in MODELS:
        err(w, f"governance_model '{p['governance_model']}' not allowed")
    if len(p["conv"]) != 2 or len(p["gaps"]) != 2:
        err(w, "Part B needs exactly two convergences and two gaps")
    if len(p["assume"].split()) > 200:
        err(w, f"assumptions are {len(p['assume'].split())} words (max 200)")
    if not p.get("members"):
        err(w, "no members")
    members = sorted(p["members"], key=lambda m: m["n"].casefold())
    plates[jid] = {
        "members": [{"n": esc(m["n"]), "r": esc(m.get("r") or "Coder")} for m in members],
        "model": esc(p["governance_model"]),
        "modelWhy": esc(p["governance_justification"]),
        "map": esc(p["institutional_map"]),
        "conv": [esc(c) for c in p["conv"]],
        "gaps": [esc(g) for g in p["gaps"]],
        "assume": esc(p["assume"]),
        "asOf": esc(p["as_of"]),
    }
    insts = sorted(insts, key=lambda i: (STATUS_ORDER.get(i["status"], 9), year_key(i["year"])))
    for n, i in enumerate(insts, 1):
        wi = f"{jid} #{n} {i['name'][:40]}"
        if i["status"] not in STATUS: err(wi, f"status '{i['status']}'")
        if i["type"] not in TYPES: err(wi, f"type '{i['type']}'")
        if i["ai_defined"] not in {"Yes", "No"}: err(wi, f"ai_defined '{i['ai_defined']}'")
        if i["risk"] not in {"Present", "Absent"}: err(wi, f"risk '{i['risk']}'")
        if i["risk"] == "Present" and not i.get("tiers"): err(wi, "risk Present but no tiers")
        check_list(wi, "actor", i["actor"], ACTORS)
        if i["duties"].strip():  # strategies and similar soft law may impose no duties at all
            check_list(wi, "duties", i["duties"], DUTIES)
        check_list(wi, "rights", i["rights"], RIGHTS)
        if not i["src"].startswith("https://"): err(wi, f"src is not an https URL: {i['src']}")
        for f in ("name", "year", "systems", "trigger", "enf", "remedy", "gap", "citation"):
            if not str(i.get(f, "")).strip(): err(wi, f"{f} is empty")
        instruments.append({
            "j": jid, "name": esc(i["name"]), "orig": esc(i.get("original_title", "")),
            "year": esc(i["year"]), "status": i["status"], "type": esc(i["type"]),
            "actor": esc(i["actor"]), "systems": esc(i["systems"]), "aiDef": i["ai_defined"],
            "trigger": esc(i["trigger"]), "duties": esc(i["duties"]) or "None imposed", "dutyNote": esc(i.get("duty_note", "")),
            "risk": i["risk"], "tiers": esc(i.get("tiers", "")), "rights": esc(i["rights"]),
            "enf": esc(i["enf"]), "remedy": esc(i["remedy"]), "gap": esc(i["gap"]),
            "cite": esc(i["citation"]), "src": esc(i["src"]),
        })
        csv_rows.append({"plate": jid.upper(), "instrument": i["name"], "original_title": i.get("original_title", ""),
                         "year": i["year"], "legal_status": i["status"], "instrument_type": i["type"],
                         "regulated_actor": i["actor"], "ai_systems_covered": i["systems"],
                         "ai_legally_defined": i["ai_defined"], "regulatory_trigger": i["trigger"],
                         "core_duties": i["duties"], "risk_classification": i["risk"], "risk_tiers": i.get("tiers", ""),
                         "rights_of_affected_persons": i["rights"], "enforcement_authority": i["enf"],
                         "remedy_or_sanction": i["remedy"], "identified_gap": i["gap"],
                         "source_citation": i["citation"], "source_link": i["src"], "status_as_of": p["as_of"]})

if errors:
    print("Validation failed:\n  " + "\n  ".join(errors), file=sys.stderr)
    sys.exit(1)

data = {"jurisdictions": jurisdictions, "plates": plates, "instruments": instruments}
block = ("/* DATA:BEGIN (generated by tools/build.py from data/*.json; do not edit by hand) */\n"
         "const DATA = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n/* DATA:END */")
page = INDEX.read_text(encoding="utf-8")
new, n = re.subn(r"/\* DATA:BEGIN.*?/\* DATA:END \*/", lambda _: block, page, flags=re.S)
if n != 1:
    sys.exit("DATA markers not found exactly once in index.html")
INDEX.write_text(new, encoding="utf-8")

with open(DATA_DIR / "atlas-register.csv", "w", newline="", encoding="utf-8") as f:
    wr = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
    wr.writeheader(); wr.writerows(csv_rows)

print(f"Built {len(plates)} plates, {len(instruments)} instruments.")
