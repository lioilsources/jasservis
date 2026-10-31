#!/usr/bin/env python3
"""Read-only integrity checks for the warning catalogue and its review evidence.

This checks relationships and generated artefacts, not automotive correctness.
It never repairs files, fetches remote sources or promotes a review to complete.
"""
from collections import Counter, defaultdict
import csv
import hashlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT.parent
LANGS = ("cs", "en", "de")
BRANDS = {
    "volkswagen", "audi", "skoda", "seat", "cupra",
    "volkswagen-uzitkove-vozy",
}
PAGE_NAMES = (
    "index.html", "zdroje.html", "revize.html",
    "revize-kapitol.html", "druha-kontrola.html",
)
ROUTE = "kontrolky-a-vystrazna-hlaseni"
AUDI_PHOTO_CLASSIFICATION_CODES = {
    "warning-indicator", "operating-status", "physical-control", "mmi-control", "control",
    "unresolved", "mmi-status", "driver-message", "vehicle-data", "service-reminder", "control-state",
}
AUDI_PHOTO_STATE_CODES = {
    "displayed", "control-visible-not-activation-proof", "menu-tile", "message-displayed",
    "control-visible", "visible", "steady-visible", "visible-state-duration-unknown",
    "visible-state-unknown", "control-visible-system-unknown", "control-visible-function-unconfirmed",
}
AUDI_MEANING_BASES = {"photo-visible-text-or-graphic", "photo-plus-candidate-manual", "unresolved"}
AUDI_SOURCE_PAGE_STATUS = "not-applicable-vehicle-display-photograph"
AUDI_INVENTORY_STATUS = {
    "cs": ("model nedoložen", "vydání nedoloženo; zdrojem je fotografie vozidla", "modelový rok nedoložen", "obrazově porovnáno", "stránka se nepoužije – zdrojem je fotografie displeje vozidla"),
    "en": ("model not established", "edition not established; source is a vehicle photograph", "model year not established", "visually reviewed", "page not applicable – source is a vehicle-display photograph"),
    "de": ("Modell unbelegt", "Ausgabe unbelegt; Quelle ist ein Fahrzeugfoto", "Modelljahr unbelegt", "visuell verglichen", "Seite nicht anwendbar – Quelle ist ein Foto der Fahrzeuganzeige"),
}
AUDI_MANUAL_PRINTED_PAGES = (9, 10, 12, 13)
AUDI_MANUAL_REQUESTED_PAGES = (9, 10, 11, 12, 13)
AUDI_MANUAL_PAGE_COUNTS = {9: (5, 5), 10: (35, 35), 12: (38, 38), 13: (24, 25)}
AUDI_MANUAL_POSITION_COUNTS = {
    (9, "main"): 5,
    (10, "left"): 17, (10, "right"): 18,
    (12, "left"): 18, (12, "right"): 20,
    (13, "left"): 19, (13, "right"): 5,
}
AUDI_MANUAL_SOURCE_PAGE_STATUS = "photographed-manual-page"
AUDI_MANUAL_INVENTORY_STATUS = {
    "cs": ("model nedoložen", "vydání návodu nedoloženo", "modelový rok nedoložen", "obrazově porovnáno a řádkově přepsáno", "tištěná strana fotografovaného návodu"),
    "en": ("model not established", "manual edition not established", "model year not established", "visually reviewed and transcribed row by row", "printed page of the photographed manual"),
    "de": ("Modell unbelegt", "Anleitungsausgabe unbelegt", "Modelljahr unbelegt", "visuell geprüft und zeilenweise transkribiert", "gedruckte Seite der fotografierten Anleitung"),
}
AUDI_MANUAL_SEMANTIC_RESULTS = {
    "compatible_candidate", "partial_candidate", "missing", "rejected_mismatch", "pending_only",
}
AUDI_MANUAL_GRAPHIC_RESULTS = {
    "compatible_unverified", "mismatch", "missing", "state_unresolved", "pending", "multiple_distinct",
}
AUDI_MANUAL_MODEL_SCOPE_RESULT = "unknown_source_model_no_exact_scope"
AUDI_MANUAL_SEMANTIC_LABELS = {
    "cs": {"compatible_candidate": "slučitelný významový kandidát", "partial_candidate": "částečný významový kandidát", "missing": "použitelný kandidát chybí", "rejected_mismatch": "kandidát odmítnut pro odlišný význam", "pending_only": "pouze čekající kandidát"},
    "en": {"compatible_candidate": "compatible semantic candidate", "partial_candidate": "partial semantic candidate", "missing": "no usable candidate", "rejected_mismatch": "candidate rejected as a semantic mismatch", "pending_only": "pending candidate only"},
    "de": {"compatible_candidate": "passender Bedeutungskandidat", "partial_candidate": "teilweiser Bedeutungskandidat", "missing": "kein nutzbarer Kandidat", "rejected_mismatch": "Kandidat wegen abweichender Bedeutung verworfen", "pending_only": "nur ausstehender Kandidat"},
}
AUDI_MANUAL_GRAPHIC_LABELS = {
    "cs": {"compatible_unverified": "podoba slučitelná, přesná grafika neověřena", "mismatch": "grafická varianta se neshoduje", "missing": "přesná grafická varianta chybí", "state_unresolved": "grafický stav nelze uzavřít z přehledu", "pending": "grafika zůstává čekající", "multiple_distinct": "řádek obsahuje více odlišných grafik"},
    "en": {"compatible_unverified": "appearance compatible; exact graphic unverified", "mismatch": "graphic variant differs", "missing": "exact graphic variant missing", "state_unresolved": "graphic state unresolved from the overview", "pending": "graphic remains pending", "multiple_distinct": "row contains multiple distinct graphics"},
    "de": {"compatible_unverified": "Darstellung passend; genaue Grafik ungeprüft", "mismatch": "Grafikvariante weicht ab", "missing": "genaue Grafikvariante fehlt", "state_unresolved": "Grafikzustand aus der Übersicht nicht geklärt", "pending": "Grafik bleibt ausstehend", "multiple_distinct": "Zeile enthält mehrere unterschiedliche Grafiken"},
}
AUDI_MANUAL_MODEL_SCOPE_LABELS = {
    "cs": "model zdroje není znám; přesný modelový rozsah nedoložen",
    "en": "source model unknown; no exact model scope established",
    "de": "Quellmodell unbekannt; kein genauer Modellumfang belegt",
}
AUDI_MANUAL_SPECIAL_COLOUR_LABELS = {
    "cs": "Smíšená / odstín nejistý",
    "en": "Mixed / hue unresolved",
    "de": "Gemischt / Farbton ungeklärt",
}


class Audit:
    def __init__(self):
        self.errors = []
        self.skipped = []
        self.checks = Counter()

    def check(self, condition, category, message):
        self.checks[category] += 1
        if not condition:
            self.errors.append(message)

    def read_json(self, name):
        path = HERE / name
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ValueError(f"{path}: cannot read JSON: {exc}") from exc

    def csv_rows(self, name):
        path = HERE / name
        if not path.exists():
            self.errors.append(f"{name}: required catalogue CSV is missing")
            return None
        with path.open(encoding="utf-8-sig", newline="") as source:
            return list(csv.DictReader(source, delimiter=";"))

    def local_file(self, name, label):
        path = (ROOT / name).resolve()
        try:
            path.relative_to(ROOT)
        except ValueError:
            self.check(False, "local_paths", f"{label}: path leaves site root: {name!r}")
            return None
        self.check(path.is_file(), "local_paths", f"{label}: missing file {name!r}")
        return path if path.is_file() else None


def unique_ids(audit, objects, label):
    ids = [x.get("id") for x in objects]
    audit.check(all(isinstance(x, str) and x for x in ids), "ids", f"{label}: missing/invalid ID")
    repeated = sorted(str(x) for x, n in Counter(ids).items() if n > 1)
    audit.check(not repeated, "ids", f"{label}: duplicate IDs {repeated}")
    return set(ids)


def check_catalogue(audit, cat, locales):
    items, manuals, graphics = cat["items"], cat["manuals"], cat["graphics"]
    ids = unique_ids(audit, items, "catalog.json.items")
    audit.check(set(cat["counts"]["by_brand"]) == BRANDS, "counts", "catalog.json: expected six declared brands")
    used_manuals = set()
    for item in items:
        label = f"catalog.json item {item['id']}"
        for field in ("name", "meaning", "action", "note", "alt"):
            value = item.get(field, {})
            for lang in LANGS:
                audit.check(isinstance(value.get(lang), str) and bool(value[lang].strip()),
                            "translations", f"{label}.{field}.{lang}: empty/missing text")
        scope_serialized = [json.dumps(s, sort_keys=True, ensure_ascii=False) for s in item["scopes"]]
        audit.check(len(scope_serialized) == len(set(scope_serialized)), "scopes", f"{label}: duplicate identical scope")
        for scope in item["scopes"]:
            brand = scope["brand"]
            audit.check(brand in BRANDS, "scopes", f"{label}: unknown brand {brand!r}")
            manual_id = scope.get("manual")
            if manual_id:
                audit.check(manual_id in manuals, "manual_refs", f"{label}: missing manual {manual_id!r}")
                if manual_id in manuals:
                    used_manuals.add(manual_id)
                    audit.check(manuals[manual_id]["brand"] == brand, "manual_refs",
                                f"{label}: brand {brand} disagrees with manual {manual_id}")
            else:
                audit.check(bool(scope.get("url")), "manual_refs", f"{label}: general scope lacks source URL")
            for lang in LANGS:
                ui = locales[lang]
                for group, key in (("states", scope.get("signal_state", item["state"])),
                                   ("colors", item["color"]), ("kinds", item["kind"])):
                    audit.check(key in ui[group], "translations", f"{label}: missing {lang}.{group}.{key}")
        meta = item.get("graphic_source", {})
        path = item["graphic_path"]
        suffix = Path(path).suffix.lower()
        audit.check(suffix in {".svg", ".png"}, "graphics", f"{label}: public graphic must be a standalone SVG or PNG")
        audit.check(not re.search(r"(?:photo|manual|screen|screenshot|page|fotograf)", path, re.I),
                    "graphics", f"{label}: public graphic path looks like a source photograph: {path}")
        audit.check(meta.get("file") == path, "graphics", f"{label}: graphic_source.file differs from graphic_path")
        candidates = [g for g in graphics.values() if g.get("file") == path]
        audit.check(len(candidates) == 1, "graphics", f"{label}: graphic metadata is not unique for {path}")
        if len(candidates) == 1:
            audit.check(meta.get("sha256") == candidates[0].get("sha256"), "graphics", f"{label}: inconsistent graphic hash")
    used_paths = {x["graphic_path"] for x in items}
    metadata_paths = {g["file"] for g in graphics.values()}
    audit.check(used_paths == metadata_paths, "graphics", "catalog.json: graphic metadata and actual usage differ")
    hashes = {}
    for key, meta in graphics.items():
        path = audit.local_file(meta["file"], f"catalog.json.graphics[{key}]")
        if path:
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            hashes[meta["file"]] = actual
            audit.check(actual == meta.get("sha256"), "graphics", f"{meta['file']}: SHA-256 mismatch")
            if path.suffix.lower() == ".svg":
                svg = path.read_text(encoding="utf-8", errors="replace")
                audit.check(not re.search(r"<image\b|data:image/", svg, re.I), "graphics",
                            f"{meta['file']}: standalone SVG embeds a raster or remote image")
    computed = {
        "semantic_records": len(items),
        "distinct_pictogram_shapes": len({x["graphic"] for x in items}),
        "shared_graphic_colour_variants": len(used_paths),
        "model_edition_assignments": sum(bool(s.get("manual")) for x in items for s in x["scopes"]),
        "model_documented_semantic_records": sum(any(s.get("manual") for s in x["scopes"]) for x in items),
        "partially_reviewed_manual_editions": len(used_manuals),
        "legacy_generic_volkswagen": sum(s["brand"] == "volkswagen" and not s.get("manual") for x in items for s in x["scopes"]),
    }
    for key, value in computed.items():
        audit.check(cat["counts"].get(key) == value, "counts", f"catalog.json.counts.{key}: expected {value}, found {cat['counts'].get(key)!r}")
    for brand in sorted(BRANDS):
        brand_items = [x for x in items if any(s["brand"] == brand for s in x["scopes"])]
        scopes = [s for x in items for s in x["scopes"] if s["brand"] == brand]
        brand_manuals = {s["manual"] for s in scopes if s.get("manual") in manuals}
        third_party = sum(manuals[m].get("host_kind") == "third-party-copy" for m in brand_manuals)
        values = {
            "distinct_pictogram_shapes": len({x["graphic"] for x in brand_items}),
            "graphic_colour_variants": len({x["graphic_path"] for x in brand_items}),
            "semantic_variants": len(brand_items),
            "model_edition_assignments": sum(bool(s.get("manual")) for s in scopes),
            "generic_brand_assignments": sum(not s.get("manual") for s in scopes),
            "reviewed_manual_editions": len(brand_manuals),
            "first_party_hosted_manual_editions": len(brand_manuals) - third_party,
            "third_party_hosted_manual_editions": third_party,
        }
        for key, value in values.items():
            actual = cat["counts"]["by_brand"].get(brand, {}).get(key)
            audit.check(actual == value, "counts", f"catalog.json.counts.by_brand.{brand}.{key}: expected {value}, found {actual!r}")
    return ids, hashes, computed


def check_csv(audit, cat, hashes):
    items = {x["id"]: x for x in cat["items"]}
    for lang in LANGS:
        name = f"catalog-texts.{lang}.csv"
        rows = audit.csv_rows(name)
        if rows is None:
            continue
        keys = [r.get("id") for r in rows]
        audit.check(len(keys) == len(set(keys)) and set(keys) == set(items), "csv", f"{name}: catalogue IDs/count differ")
        for row in rows:
            item = items.get(row.get("id"))
            if item is None:
                continue
            expected = {field: item[field][lang] for field in ("name", "meaning", "action", "note", "alt")}
            expected.update({"kind": item["kind"], "state": item["state"], "colour": item["color"],
                             "group": item["group"], "shared_image": item["graphic_path"]})
            for field, value in expected.items():
                audit.check(row.get(field) == value, "csv", f"{name}:{item['id']}.{field}: differs from catalogue")
            try:
                actual_scopes = json.loads(row.get("source_scope_json", ""))
            except ValueError:
                actual_scopes = None
            audit.check(actual_scopes == item["scopes"], "csv", f"{name}:{item['id']}.source_scope_json: differs from catalogue")
    rows = audit.csv_rows("coverage.csv")
    if rows is not None:
        expected = []
        for item in items.values():
            for scope in item["scopes"]:
                manual = cat["manuals"].get(scope.get("manual"), {})
                expected.append((item["id"], item["name"]["cs"], item["name"]["en"], item["name"]["de"],
                                 scope["brand"], scope.get("model") or "Not documented",
                                 str(scope.get("model_year") or "Not documented"), scope.get("edition") or "",
                                 ",".join(map(str, scope.get("printed_pages", []))),
                                 ",".join(map(str, scope.get("pdf_pages", []))), ",".join(scope["powertrains"]),
                                 scope.get("signal_state", item["state"]), item["color"],
                                 manual.get("url", scope.get("url", "")), item["graphic_path"],
                                 item["graphic_source"].get("page", ""), item["graphic_source"]["license"], item["checked"]))
        columns = ("ID", "Název CZ", "Name EN", "Name DE", "Brand", "Model", "Model year", "Edition",
                   "Printed pages", "PDF pages", "Powertrains", "State", "Colour", "Source", "Graphic",
                   "Graphic source", "Licence", "Checked")
        actual = [tuple(r.get(k, "") for k in columns) for r in rows]
        missing = Counter(expected) - Counter(actual)
        extra = Counter(actual) - Counter(expected)
        audit.check(not missing and not extra, "csv", f"coverage.csv: {sum(missing.values())} missing/changed and {sum(extra.values())} extra/changed rows")
    rows = audit.csv_rows("used-symbols.csv")
    if rows is not None:
        actual_paths = [r.get("shared_file") for r in rows]
        audit.check(len(actual_paths) == len(set(actual_paths)) and set(actual_paths) == set(hashes), "csv", "used-symbols.csv: asset inventory differs")
        for row in rows:
            path = row["shared_file"]
            audit.check(row.get("sha256") == hashes.get(path), "csv", f"used-symbols.csv:{path}: SHA-256 mismatch")
            expected_ids = {x["id"] for x in items.values() if x["graphic_path"] == path}
            audit.check(set(filter(None, row.get("catalogue_ids", "").split(","))) == expected_ids,
                        "csv", f"used-symbols.csv:{path}: item references differ")


def check_reviews(audit, cat, register, queues):
    rows = register["manuals"]
    ids = unique_ids(audit, rows, "review-register.json.manuals")
    audit.check(ids == set(cat["manuals"]), "reviews", "review-register.json: manual inventory differs from catalogue")
    complete = set(register["fully_compared_manuals"])
    audit.check(complete <= ids, "reviews", "review-register.json: completed manual reference is unknown")
    for row in rows:
        actual_items = {x["id"] for x in cat["items"] if any(s.get("manual") == row["id"] for s in x["scopes"])}
        audit.check(set(row["verified_item_ids"]) == actual_items, "reviews", f"review-register.json:{row['id']}: verified item IDs differ")
        is_complete = row.get("whole_manual_comparison") in {"complete", "fully-compared", "whole-manual-complete"}
        audit.check(is_complete == (row["id"] in complete), "reviews", f"review-register.json:{row['id']}: whole-manual completion flags disagree")
    audit.check(queues["whole_manuals_complete"] == len(complete), "reviews", "work-queues.json: whole-manual count differs from register")
    audit.check(register["latest_round"]["whole_manuals_complete"] == len(complete), "reviews", "review-register.json.latest_round: whole-manual count differs")
    chapter_path = HERE / "chapter-review.json"
    if chapter_path.exists():
        chapter = audit.read_json("chapter-review.json")
        audit.check(set(chapter["fully_compared_manuals"]) == complete, "reviews", "chapter-review.json: complete manuals differ from register")
    manual_rows = audit.csv_rows("manual-review.csv")
    if manual_rows is not None:
        by_id = {r["id"]: r for r in rows}
        audit.check(len(manual_rows) == len(by_id) and {r.get("id") for r in manual_rows} == set(by_id),
                    "csv", "manual-review.csv: manual inventory differs")
        for row in manual_rows:
            source = by_id.get(row.get("id"))
            if source:
                audit.check(row.get("whole_manual_comparison") == source.get("whole_manual_comparison"),
                            "csv", f"manual-review.csv:{row['id']}: completion differs from register")
    return len(complete)


def photo_occurrences(row):
    occurrences = row.get("occurrences") or []
    if occurrences:
        return occurrences
    if row.get("photos"):
        return [{"photo": photo, "position": ""} for photo in row["photos"]]
    if row.get("photo"):
        return [{"photo": row["photo"], "position": row.get("position") or row.get("position_cs") or ""}]
    return []


def photo_candidates(row):
    return row.get("candidate_catalogue_ids_not_model_verified",
                   row.get("candidate_catalogue_ids", row.get("catalogue_entries", []))) or []


def check_photo_queue_identity(audit, row, evidence, label):
    model = evidence.get("model_confirmed_by_user")
    brand_id = evidence.get("brand_id")
    if brand_id:
        audit.check(row.get("brand") == brand_id, "photo_identity",
                    f"{label}: brand {row.get('brand')!r} disagrees with photo evidence {brand_id!r}")
    if model:
        audit.check(row.get("model") == model, "photo_identity",
                    f"{label}: model {row.get('model')!r} disagrees with photo evidence {model!r}")
    else:
        audit.check(not row.get("model"), "photo_identity",
                    f"{label}: model {row.get('model')!r} is claimed although photo evidence establishes no model")
        audit.check(evidence.get("document_identity_established") is False, "photo_identity",
                    f"{label}: unknown-model photo evidence must explicitly keep document identity unestablished")
    if evidence.get("manual_edition") is None:
        audit.check(row.get("source_edition_identified") is False, "photo_identity",
                    f"{label}: unidentified photo edition must remain explicitly unestablished")
        audit.check(bool(re.search(r"undocumented|not established|nedoložen|unbelegt", row.get("edition", ""), re.I)),
                    "photo_identity", f"{label}: title presents an unidentified photographed edition as established")
    audit.check(not row.get("source_url"), "photo_identity",
                f"{label}: photo evidence must not inherit an unrelated manual URL")


def check_audi_photo_review(audit, cat, evidence, attachment_group=None, check_csv=True):
    label = "audi-photo-review.json"
    audit.check(evidence.get("brand_id") == "audi", "photo_identity", f"{label}: brand_id must be 'audi'")
    audit.check(evidence.get("brand_confirmed_by_user") == "Audi", "photo_identity",
                f"{label}: Audi brand confirmation is missing")
    audit.check(evidence.get("model_confirmed_by_user") is None, "photo_identity",
                f"{label}: exact model is not established by the five photographs")
    audit.check(evidence.get("document_identity_established") is False, "photo_identity",
                f"{label}: document/model identity must remain explicitly unestablished")
    for field in ("manual_edition", "model_year", "generation"):
        audit.check(evidence.get(field) is None, "photo_identity", f"{label}: {field} must remain null")
    photos = evidence.get("photos", [])
    photo_ids = unique_ids(audit, photos, f"{label}.photos")
    audit.check(evidence.get("expected_photo_count_originally_requested") == 4, "photo_status",
                f"{label}: original requested count must remain four")
    audit.check(evidence.get("photos_received") == len(photos), "photo_status",
                f"{label}: photos_received differs from photo inventory")
    audit.check(evidence.get("photos_received") == 5, "photo_status", f"{label}: expected five received photographs")
    audit.check(evidence.get("original_filenames_available") is False, "photo_status",
                f"{label}: original filenames must not be claimed")
    audit.check(evidence.get("raw_image_files_available_in_workspace") is False, "photo_status",
                f"{label}: raw image files must not be claimed")
    inspected = evidence.get("photos_visually_inspected")
    audit.check(isinstance(inspected, int) and 0 <= inspected <= len(photos), "photo_status",
                f"{label}: photos_visually_inspected is invalid")
    if attachment_group:
        audit.check(evidence.get("photos_received") == attachment_group.get("available_in_conversation"),
                    "photo_status", f"{label}: photos_received differs from attachment inventory")
        audit.check(inspected == attachment_group.get("visually_compared"), "photo_status",
                    f"{label}: photos_visually_inspected differs from attachment inventory")
    observations = evidence.get("observations", [])
    observation_ids = unique_ids(audit, observations, f"{label}.observations")
    catalogue_ids = {item["id"] for item in cat.get("items", [])}
    occurrence_keys = []
    referenced_photos = Counter()
    for row in observations:
        row_label = f"{label}.observations[{row.get('id')}]"
        occurrences = photo_occurrences(row)
        audit.check(bool(occurrences), "photo_status", f"{row_label}: no photograph occurrence")
        for occurrence in occurrences:
            photo_id = occurrence.get("photo")
            audit.check(photo_id in photo_ids, "photo_status", f"{row_label}: unknown photograph {photo_id!r}")
            occurrence_keys.append((row.get("id", ""), photo_id or ""))
            referenced_photos[photo_id] += 1
        classification = row.get("classification") or row.get("category")
        audit.check(classification in AUDI_PHOTO_CLASSIFICATION_CODES, "photo_status",
                    f"{row_label}: unsupported classification {classification!r}")
        state = row.get("signal_state_from_photo")
        audit.check(state in AUDI_PHOTO_STATE_CODES, "photo_status", f"{row_label}: unsupported photo state {state!r}")
        audit.check("source_page" in row and row.get("source_page") is None, "photo_identity",
                    f"{row_label}: source_page must be explicit null for a vehicle photograph")
        audit.check(row.get("source_page_status") == AUDI_SOURCE_PAGE_STATUS, "photo_identity",
                    f"{row_label}: source_page_status must mark a vehicle photograph as not applicable")
        candidates = set(photo_candidates(row))
        audit.check(candidates <= catalogue_ids, "photo_candidates",
                    f"{row_label}: unknown catalogue candidates {sorted(candidates - catalogue_ids)}")
        audit.check(not (row.get("matching_model_scoped_catalogue_ids") or []), "photo_identity",
                    f"{row_label}: unknown model cannot have a model-scoped catalogue match")
        audit.check(row.get("published_from_this_photo_set") is False, "photo_identity",
                    f"{row_label}: unknown-model photo observation must not be published as a catalogue item")
        audit.check(row.get("exact_reusable_graphic_verified") is False, "photo_identity",
                    f"{row_label}: still photograph is not an independently reusable exact graphic")
        for field in ("manual_edition", "model_year"):
            audit.check(row.get(field) is None, "photo_identity", f"{row_label}: {field} must remain null")
        references = row.get("candidate_manual_references", [])
        basis = row.get("meaning_verification_basis")
        audit.check(basis in AUDI_MEANING_BASES, "photo_identity",
                    f"{row_label}: invalid or missing meaning_verification_basis {basis!r}")
        if row.get("meaning_verified") is True:
            expected_basis = "photo-plus-candidate-manual" if references else "photo-visible-text-or-graphic"
            audit.check(basis == expected_basis, "photo_identity",
                        f"{row_label}: meaning verification basis should be {expected_basis!r}")
        else:
            audit.check(basis == "unresolved", "photo_identity",
                        f"{row_label}: unverified meaning must remain unresolved")
        for reference in references:
            manual = reference.get("manual")
            audit.check(manual in cat.get("manuals", {}), "manual_refs",
                        f"{row_label}: unknown candidate manual {manual!r}")
            pages = reference.get("printed_pages") or []
            audit.check(bool(pages) and all(isinstance(page, int) and page > 0 for page in pages), "manual_refs",
                        f"{row_label}: candidate manual reference has no printed pages")
            relationship = json.dumps(reference.get("relationship", ""), ensure_ascii=False)
            audit.check(bool(reference.get("relationship")) and bool(re.search(
                        r"does not identify|not identify|neurčuje|neidentif|identifiziert nicht", relationship, re.I)), "photo_identity",
                        f"{row_label}: candidate manual relationship is not qualified")
            if manual in cat.get("manuals", {}):
                source = cat["manuals"][manual]
                audit.check(bool(source.get("edition")) and bool(source.get("part_number")), "manual_refs",
                            f"{row_label}: candidate manual lacks edition or part number")
    summary = evidence.get("summary", {})
    audit.check(summary.get("observation_count") == len(observations), "photo_status",
                f"{label}: summary observation count differs")
    audit.check(summary.get("meaning_verified_count") == sum(row.get("meaning_verified") is True for row in observations),
                "photo_status", f"{label}: summary meaning-verified count differs")
    audit.check(summary.get("unresolved_count") == sum(row.get("meaning_verified") is not True for row in observations),
                "photo_status", f"{label}: summary unresolved count differs")
    audit.check(summary.get("catalogue_result_unresolved_count") ==
                sum(row.get("catalogue_result") == "unresolved" for row in observations),
                "photo_status", f"{label}: summary catalogue-result unresolved count differs")
    audit.check(summary.get("occurrence_count") == len(occurrence_keys), "photo_status",
                f"{label}: summary occurrence count differs")
    audit.check(set(referenced_photos) == photo_ids and all(referenced_photos[photo_id] > 0 for photo_id in photo_ids),
                "photo_status", f"{label}: every received photograph must be referenced by an observation")
    audit.check(summary.get("published_from_this_photo_set_count") == 0 and
                evidence.get("customer_catalogue_entries_added_from_this_photo_set") == 0,
                "photo_identity", f"{label}: unknown-model photographs must add no customer catalogue records")
    audit.check(summary.get("exact_reusable_graphic_verified_count") == 0,
                "photo_identity", f"{label}: photographs must not claim independently reusable source graphics")
    reference = evidence.get("candidate_reference_manual", {})
    if reference:
        audit.check(reference.get("manual") in cat.get("manuals", {}), "manual_refs",
                    f"{label}: unknown candidate reference manual")
        audit.check(reference.get("model") != evidence.get("model_confirmed_by_user"), "photo_identity",
                    f"{label}: candidate reference model was promoted to photographed model")
        audit.check(bool(reference.get("relationship")), "photo_identity",
                    f"{label}: candidate reference manual needs an explicit non-identification relationship")
    if check_csv:
        observations_by_id = {row["id"]: row for row in observations}
        for lang in LANGS:
            comparison = audit.csv_rows(f"audi-photo-comparison.{lang}.csv")
            if comparison is not None:
                actual = [(r.get("observation_id", ""), r.get("photo", "")) for r in comparison]
                audit.check(Counter(actual) == Counter(occurrence_keys), "csv",
                            f"audi-photo-comparison.{lang}.csv: rows differ from JSON observations")
                for row in comparison:
                    row_label = f"audi-photo-comparison.{lang}.csv:{row.get('observation_id', '')}"
                    source_row = observations_by_id.get(row.get("observation_id"), {})
                    audit.check(row.get("brand") == "Audi", "photo_identity", f"{row_label}: brand differs")
                    audit.check(not row.get("model") and not row.get("manual_edition") and not row.get("model_year"),
                                "photo_identity", f"{row_label}: unknown identity must remain blank")
                    expected_model, expected_edition, expected_model_year, _, _ = AUDI_INVENTORY_STATUS[lang]
                    audit.check(row.get("model_status") == expected_model and
                                row.get("manual_edition_status") == expected_edition and
                                row.get("model_year_status") == expected_model_year,
                                "translations", f"{row_label}: missing identity statuses are not localised")
                    audit.check(not row.get("source_page") and
                                row.get("source_page_status_code") == AUDI_SOURCE_PAGE_STATUS and
                                bool(row.get("source_page_status")), "photo_identity",
                                f"{row_label}: vehicle photograph must explicitly mark page as not applicable")
                    audit.check(row.get("classification_code") == (source_row.get("classification") or source_row.get("category")) and
                                bool(row.get("classification")) and row.get("classification") != row.get("classification_code"),
                                "translations", f"{row_label}: classification is not localised")
                    audit.check(row.get("photo_colour_code") == source_row.get("photo_colour") and
                                bool(row.get("photo_colour")) and row.get("photo_colour") != row.get("photo_colour_code"),
                                "translations", f"{row_label}: photo colour is not localised")
                    audit.check(row.get("signal_state_from_photo_code") == source_row.get("signal_state_from_photo") and
                                bool(row.get("signal_state_from_photo")) and
                                row.get("signal_state_from_photo") != row.get("signal_state_from_photo_code"),
                                "translations", f"{row_label}: photo state is not localised")
                    audit.check(row.get("meaning_verification_basis_code") == source_row.get("meaning_verification_basis") and
                                bool(row.get("meaning_verification_basis")) and
                                row.get("meaning_verification_basis") != row.get("meaning_verification_basis_code"),
                                "translations", f"{row_label}: meaning verification basis is not localised")
                    try:
                        exported_references = json.loads(row.get("candidate_manual_references_json") or "[]")
                    except (TypeError, ValueError):
                        exported_references = None
                    expected_references = source_row.get("candidate_manual_references", [])
                    audit.check(isinstance(exported_references, list) and
                                [r.get("manual_id") for r in exported_references] == [r.get("manual") for r in expected_references] and
                                [r.get("printed_pages") for r in exported_references] == [r.get("printed_pages") for r in expected_references],
                                "csv", f"{row_label}: candidate manual references differ from JSON")
                    if isinstance(exported_references, list):
                        for reference in exported_references:
                            manual = cat.get("manuals", {}).get(reference.get("manual_id"), {})
                            audit.check(reference.get("edition") == manual.get("edition") and
                                        reference.get("part_number") == manual.get("part_number") and
                                        reference.get("candidate_only") is True and
                                        reference.get("identifies_photographed_vehicle") is False,
                                        "photo_identity", f"{row_label}: candidate manual metadata or qualification differs")
                    audit.check(bool(row.get("candidate_manual_reference_status")), "translations",
                                f"{row_label}: candidate manual reference status is missing")
                    for field in ("meaning_verified", "exact_reusable_graphic_verified", "published_from_this_photo_set"):
                        audit.check(row.get(field) == str(source_row.get(field)), "csv",
                                    f"{row_label}: {field} differs from JSON")
            inventory = audit.csv_rows(f"audi-photo-inventory.{lang}.csv")
            if inventory is not None:
                ids = [r.get("working_photo_reference") for r in inventory]
                audit.check(len(ids) == len(set(ids)) and set(ids) == photo_ids, "csv",
                            f"audi-photo-inventory.{lang}.csv: photo inventory differs from JSON")
                expected_model, expected_edition, _, expected_review, expected_page = AUDI_INVENTORY_STATUS[lang]
                for row in inventory:
                    row_label = f"audi-photo-inventory.{lang}.csv:{row.get('working_photo_reference', '')}"
                    audit.check(row.get("model_status") == expected_model and
                                row.get("edition_status") == expected_edition and
                                row.get("comparison_status") == expected_review,
                                "translations", f"{row_label}: inventory statuses are not localised")
                    audit.check(row.get("page_status_code") == AUDI_SOURCE_PAGE_STATUS and
                                row.get("page_status") == expected_page,
                                "translations", f"{row_label}: inventory page status is not localised")
                    audit.check(row.get("view") not in {"instrument-cluster", "mmi-dual-display", "mmi-and-centre-console"} and
                                row.get("role") not in {"primary evidence", "additional supplied view"},
                                "translations", f"{row_label}: photo view or role exposes a technical code")
    return observation_ids


def check_audi_manual_photo_review(audit, cat, evidence, attachment_group=None, check_csv=True):
    """Check the photographed Audi overview without assigning it to a model or edition."""
    label = "audi-manual-photo-review.json"
    audit.check(evidence.get("schema") == "jasservis-audi-manual-photo-review-v1", "photo_status",
                f"{label}: unsupported or missing schema")
    source = evidence.get("source", {})
    audit.check(source.get("kind") == "user-supplied-photographs", "photo_identity",
                f"{label}: source kind must remain user-supplied photographs")
    audit.check(source.get("brand") == "audi", "photo_identity", f"{label}: source brand must be 'audi'")
    for lang in LANGS:
        brand_evidence = source.get("brand_evidence", {})
        audit.check(isinstance(brand_evidence.get(lang), str) and bool(brand_evidence[lang].strip()),
                    "translations", f"{label}: source.brand_evidence.{lang} is missing")
        scope_note = evidence.get("scope_note", {})
        audit.check(isinstance(scope_note.get(lang), str) and bool(scope_note[lang].strip()),
                    "translations", f"{label}: scope_note.{lang} is missing")
        legend = source.get("checkmark_legend", {})
        audit.check(isinstance(legend.get(lang), str) and "✓" in legend[lang] and bool(legend[lang].strip()),
                    "translations", f"{label}: source.checkmark_legend.{lang} is missing or does not explain ✓")
    for field in ("model", "edition", "model_year", "generation", "imprint"):
        audit.check(field in source and source.get(field) is None, "photo_identity",
                    f"{label}: {field} must be explicit null")
    audit.check(source.get("language") == "cs", "photo_identity", f"{label}: photographed source language must be cs")
    audit.check(evidence.get("photos_received") == source.get("photo_count") == 4, "photo_status",
                f"{label}: expected four supplied photographs in both evidence and source inventory")
    audit.check(tuple(source.get("photographed_printed_pages", [])) == AUDI_MANUAL_PRINTED_PAGES,
                "photo_status", f"{label}: photographed pages must be 9, 10, 12 and 13")
    audit.check(source.get("missing_printed_pages") == [11], "photo_status",
                f"{label}: missing printed page 11 must remain explicit")

    photos = evidence.get("photos", [])
    photo_pages = [photo.get("printed_page") for photo in photos]
    audit.check(len(photos) == 5 and len(photo_pages) == len(set(photo_pages)) and
                tuple(sorted(photo_pages)) == AUDI_MANUAL_REQUESTED_PAGES,
                "photo_status", f"{label}: page inventory must explicitly cover supplied and missing pages 9–13")
    supplied_photos = [photo for photo in photos if photo.get("status") == "supplied"]
    missing_photos = [photo for photo in photos if photo.get("status") == "missing"]
    audit.check(tuple(photo.get("printed_page") for photo in supplied_photos) == AUDI_MANUAL_PRINTED_PAGES,
                "photo_status", f"{label}: exactly pages 9, 10, 12 and 13 must be supplied")
    audit.check(len(missing_photos) == 1 and missing_photos[0].get("printed_page") == 11 and
                missing_photos[0].get("row_count") is None and
                missing_photos[0].get("graphic_occurrence_count") is None,
                "photo_status", f"{label}: page 11 must remain an explicit missing inventory row")
    if attachment_group:
        audit.check(attachment_group.get("expected") == 3, "photo_status",
                    f"{label}: attachment inventory must preserve the historical expected count of three")
        audit.check(source.get("photo_count") == attachment_group.get("available_in_conversation") == 4,
                    "photo_status", f"{label}: supplied photo count differs from attachment inventory")
        audit.check(attachment_group.get("visually_compared") == 4, "photo_status",
                    f"{label}: all four supplied photographs must be visually compared")
        audit.check(attachment_group.get("unique_printed_pages_covered") == list(AUDI_MANUAL_PRINTED_PAGES),
                    "photo_status", f"{label}: attachment page coverage differs")
        audit.check(attachment_group.get("missing_printed_pages") == [11], "photo_status",
                    f"{label}: attachment inventory must retain missing page 11")

    rows = evidence.get("rows", [])
    row_ids = unique_ids(audit, rows, f"{label}.rows")
    audit.check(len(rows) == evidence.get("counts", {}).get("rows") == 102, "photo_status",
                f"{label}: expected 102 semantic rows")
    catalogue_ids = {item["id"] for item in cat.get("items", [])}
    positions = []
    position_numbers = defaultdict(list)
    page_rows = Counter()
    page_graphics = Counter()
    graphic_occurrences = 0
    for row in rows:
        row_label = f"{label}.rows[{row.get('id')}]"
        page = row.get("printed_page")
        audit.check(page in AUDI_MANUAL_PRINTED_PAGES and page != 11, "photo_status",
                    f"{row_label}: row uses an uncovered or missing printed page {page!r}")
        position = (page, row.get("column"), row.get("position_in_column"))
        positions.append(position)
        position_numbers[(page, row.get("column"))].append(row.get("position_in_column"))
        audit.check(row.get("column") in {"main", "left", "right"} and
                    isinstance(row.get("position_in_column"), int) and row["position_in_column"] > 0,
                    "photo_status", f"{row_label}: invalid row position")
        audit.check(isinstance(row.get("description_cs_verbatim"), str) and bool(row["description_cs_verbatim"].strip()),
                    "photo_status", f"{row_label}: literal Czech caption is missing")
        occurrence_count = row.get("graphic_occurrence_count")
        audit.check(isinstance(occurrence_count, int) and not isinstance(occurrence_count, bool) and occurrence_count > 0,
                    "photo_status", f"{row_label}: graphic_occurrence_count must be a positive integer")
        if isinstance(occurrence_count, int) and not isinstance(occurrence_count, bool):
            graphic_occurrences += occurrence_count
            page_graphics[page] += occurrence_count
        page_rows[page] += 1
        occurrences = row.get("graphic_occurrences", [])
        audit.check(isinstance(occurrences, list) and len(occurrences) == occurrence_count,
                    "photo_status", f"{row_label}: graphic occurrence inventory differs from its count")
        if isinstance(occurrences, list):
            audit.check([x.get("index") for x in occurrences] == list(range(1, len(occurrences) + 1)) and
                        all(isinstance(x.get("visual_description_cs"), str) and x["visual_description_cs"].strip() for x in occurrences),
                        "photo_status", f"{row_label}: graphic occurrences need ordered Czech descriptions")
        candidates = set(row.get("candidate_ids", []))
        audit.check(candidates <= catalogue_ids, "photo_candidates",
                    f"{row_label}: unknown catalogue candidates {sorted(candidates - catalogue_ids)}")
        rejected = set(row.get("rejected_merge_candidate_ids", []))
        audit.check(rejected <= catalogue_ids, "photo_candidates",
                    f"{row_label}: unknown rejected merge candidates {sorted(rejected - catalogue_ids)}")
        pending = set(row.get("pending_candidate_ids", []))
        audit.check(all(isinstance(x, str) and x for x in row.get("pending_candidate_ids", [])),
                    "photo_candidates", f"{row_label}: pending candidate IDs must be nonempty strings")
        semantic_result = row.get("semantic_result")
        audit.check(semantic_result in AUDI_MANUAL_SEMANTIC_RESULTS, "photo_status",
                    f"{row_label}: unsupported semantic result {row.get('semantic_result')!r}")
        audit.check(not (candidates & rejected), "photo_candidates",
                    f"{row_label}: the same catalogue ID cannot be a candidate and a rejected merge")
        if semantic_result in {"compatible_candidate", "partial_candidate"}:
            audit.check(bool(candidates), "photo_candidates", f"{row_label}: candidate result requires a published candidate ID")
        elif semantic_result == "missing":
            audit.check(not candidates, "photo_candidates", f"{row_label}: missing result cannot carry a usable candidate ID")
        elif semantic_result == "pending_only":
            audit.check(bool(pending) and not candidates, "photo_candidates",
                        f"{row_label}: pending-only result requires a pending ID and no published candidate")
        elif semantic_result == "rejected_mismatch":
            audit.check(bool(rejected) and not candidates, "photo_candidates",
                        f"{row_label}: rejected mismatch requires a rejected ID and no usable candidate")
        audit.check(row.get("graphic_result") in AUDI_MANUAL_GRAPHIC_RESULTS, "photo_status",
                    f"{row_label}: unsupported graphic result {row.get('graphic_result')!r}")
        audit.check(row.get("model_scope_result") == AUDI_MANUAL_MODEL_SCOPE_RESULT, "photo_identity",
                    f"{row_label}: unidentified source cannot claim exact model scope")
        result_text = row.get("text", {})
        for lang in LANGS:
            local = result_text.get(lang, {}) if isinstance(result_text, dict) else {}
            audit.check(isinstance(local.get("label"), str) and bool(local["label"].strip()) and
                        isinstance(local.get("assessment"), str) and bool(local["assessment"].strip()),
                        "translations", f"{row_label}: text.{lang} label or assessment is missing")
            if "review_note" in row:
                note = row.get("review_note", {}).get(lang)
                audit.check(isinstance(note, str) and bool(note.strip()), "translations",
                            f"{row_label}: review_note.{lang} is missing")
        audit.check(row.get("exact_reusable_graphic") is False, "photo_identity",
                    f"{row_label}: photograph must not claim an independently reusable exact graphic")
        audit.check(row.get("published") is False and row.get("published_exact_match") is False, "photo_identity",
                    f"{row_label}: photographed row must not be promoted directly to the catalogue")
        audit.check(all(isinstance(page, int) and page > 0 for page in row.get("referenced_printed_pages", [])),
                    "photo_status", f"{row_label}: referenced printed pages must be positive integers")
    audit.check(len(positions) == len(set(positions)), "photo_status",
                f"{label}: duplicate page/column/row positions")
    audit.check(set(position_numbers) == set(AUDI_MANUAL_POSITION_COUNTS), "photo_status",
                f"{label}: page/column groups differ from the photographed table")
    for page_column, expected_count in AUDI_MANUAL_POSITION_COUNTS.items():
        audit.check(sorted(position_numbers.get(page_column, [])) == list(range(1, expected_count + 1)),
                    "photo_status", f"{label}: {page_column} positions must be contiguous 1–{expected_count}")
    rows_by_id = {row.get("id"): row for row in rows}
    audit.check(rows_by_id.get("p10-left-04", {}).get("referenced_printed_pages") == [99, 274],
                "photo_status", f"{label}: p10-left-04 must retain both referenced pages 99 and 274")
    audit.check(rows_by_id.get("p10-left-17", {}).get("referenced_printed_pages") == [109],
                "photo_status", f"{label}: p10-left-17 must retain referenced page 109")
    audit.check(rows_by_id.get("p13-left-02", {}).get("color") == "bila",
                "photo_status", f"{label}: p13-left-02 must remain the white pull-away-assistant variant")
    audit.check(rows_by_id.get("p12-right-12", {}).get("color") == "smisena_neurcena" and
                rows_by_id.get("p12-right-12", {}).get("graphic_result") == "state_unresolved",
                "photo_status", f"{label}: p12-right-12 must retain mixed/unresolved source colour")
    audit.check(rows_by_id.get("p13-right-05", {}).get("graphic_occurrence_count") == 2,
                "photo_status", f"{label}: child-lock row must retain two graphic occurrences")
    audit.check(graphic_occurrences == evidence.get("counts", {}).get("graphic_occurrences") == 103, "photo_status",
                f"{label}: expected 103 graphic occurrences across 102 rows")
    photo_by_page = {photo.get("printed_page"): photo for photo in supplied_photos}
    for page in AUDI_MANUAL_PRINTED_PAGES:
        expected_rows, expected_graphics = AUDI_MANUAL_PAGE_COUNTS[page]
        audit.check(photo_by_page.get(page, {}).get("row_count") == page_rows[page] == expected_rows and
                    photo_by_page.get(page, {}).get("graphic_occurrence_count") == page_graphics[page] == expected_graphics,
                    "photo_status", f"{label}: page {page} inventory counts differ from rows")
    audit.check(sum("✓" in row.get("description_cs_verbatim", "") for row in rows) == 14,
                "photo_status", f"{label}: expected 14 rows carrying the source functional-check mark ✓")
    counts = evidence.get("counts", {})
    semantic_counts = Counter(row.get("semantic_result") for row in rows)
    graphic_counts = Counter(row.get("graphic_result") for row in rows)
    audit.check(counts.get("semantic_results") == dict(semantic_counts), "photo_status",
                f"{label}: semantic result counts differ from rows")
    audit.check(counts.get("graphic_results") == dict(graphic_counts), "photo_status",
                f"{label}: graphic result counts differ from rows")
    audit.check(counts.get("exact_model_scoped_matches") == 0 and
                counts.get("published_semantic_candidate_rows") == semantic_counts["compatible_candidate"] + semantic_counts["partial_candidate"] == 48 and
                counts.get("rows_without_usable_published_candidate") == len(rows) - 48 == 54 and
                counts.get("pending_only_candidate_rows") == semantic_counts["pending_only"] == 1,
                "photo_status", f"{label}: summary candidate/model-scope counts differ from rows")
    audit.check(not any(row.get("published") or row.get("published_exact_match") or row.get("exact_reusable_graphic")
                        for row in rows), "photo_identity",
                f"{label}: unidentified manual must publish no exact match or reusable graphic")
    rules = evidence.get("must_not_merge", [])
    audit.check(any(rule.get("catalog_id") == "audi-direct-wheel-change" and
                    {"p10-right-02", "p10-right-16"} <= set(rule.get("photo_rows", [])) for rule in rules),
                "photo_candidates", f"{label}: required loose-wheel/direct-wheel-change no-merge rule is missing")
    audit.check(any(rule.get("pending_catalog_id") == "audi-a8-parking-assistance-controls" and
                    rule.get("published_catalog_id") == "audi-park-assist-unavailable" and
                    {"p13-left-14", "p13-left-15"} <= set(rule.get("photo_rows", [])) for rule in rules),
                "photo_candidates", f"{label}: required parking-control/unavailability no-merge rule is missing")
    for index, rule in enumerate(rules):
        rule_label = f"{label}.must_not_merge[{index}]"
        audit.check(bool(rule.get("photo_rows")) and set(rule["photo_rows"]) <= row_ids,
                    "photo_candidates", f"{rule_label}: unknown or missing photo rows")
        published_id = rule.get("catalog_id") or rule.get("published_catalog_id")
        audit.check(not published_id or published_id in catalogue_ids, "photo_candidates",
                    f"{rule_label}: unknown published catalogue ID {published_id!r}")
        pending_id = rule.get("pending_catalog_id")
        pending_ids = {x for row in rows for x in row.get("pending_candidate_ids", [])}
        audit.check(not pending_id or pending_id in pending_ids, "photo_candidates",
                    f"{rule_label}: unknown pending candidate ID {pending_id!r}")
        for lang in LANGS:
            reason = rule.get("reason", {}).get(lang)
            audit.check(isinstance(reason, str) and bool(reason.strip()), "translations",
                        f"{rule_label}: reason.{lang} is missing")

    if check_csv:
        rows_by_id = {row["id"]: row for row in rows}
        supplied_by_id = {f"audi-manual-photo-p{photo['printed_page']:02d}": photo for photo in supplied_photos}
        for lang in LANGS:
            comparison = audit.csv_rows(f"audi-manual-photo-review.{lang}.csv")
            if comparison is not None:
                ids = [row.get("row_id") for row in comparison]
                audit.check(len(ids) == len(set(ids)) and set(ids) == row_ids, "csv",
                            f"audi-manual-photo-review.{lang}.csv: rows differ from JSON")
                expected_model, expected_edition, expected_model_year, _, expected_page = AUDI_MANUAL_INVENTORY_STATUS[lang]
                for exported in comparison:
                    row_label = f"audi-manual-photo-review.{lang}.csv:{exported.get('row_id', '')}"
                    source_row = rows_by_id.get(exported.get("row_id"), {})
                    expected_photo = f"audi-manual-photo-p{source_row.get('printed_page', 0):02d}"
                    audit.check(exported.get("photo") == expected_photo and
                                exported.get("printed_page") == str(source_row.get("printed_page", "")) and
                                exported.get("graphic_occurrence_count") == str(source_row.get("graphic_occurrence_count", "")),
                                "csv", f"{row_label}: photo, page or graphic occurrence count differs")
                    audit.check(exported.get("semantic_result_code") == source_row.get("semantic_result") and
                                exported.get("semantic_result") == AUDI_MANUAL_SEMANTIC_LABELS[lang].get(source_row.get("semantic_result")) and
                                exported.get("semantic_assessment") == source_row.get("text", {}).get(lang, {}).get("assessment"),
                                "translations", f"{row_label}: semantic result is not localised from JSON")
                    audit.check(exported.get("source_checkmark_legend") == source.get("checkmark_legend", {}).get(lang),
                                "translations", f"{row_label}: source checkmark legend is missing or not localised")
                    audit.check(exported.get("graphic_result_code") == source_row.get("graphic_result") and
                                exported.get("graphic_result") == AUDI_MANUAL_GRAPHIC_LABELS[lang].get(source_row.get("graphic_result")),
                                "translations", f"{row_label}: graphic result is not localised")
                    audit.check(exported.get("model_scope_result_code") == AUDI_MANUAL_MODEL_SCOPE_RESULT and
                                exported.get("model_scope_result") == AUDI_MANUAL_MODEL_SCOPE_LABELS[lang],
                                "translations", f"{row_label}: model-scope result is not localised")
                    for field in ("published", "published_exact_match", "exact_reusable_graphic"):
                        audit.check(exported.get(field) == str(source_row.get(field)), "csv",
                                    f"{row_label}: {field} differs from JSON")
                    audit.check(not exported.get("model") and not exported.get("manual_edition") and not exported.get("model_year"),
                                "photo_identity", f"{row_label}: unknown identity must remain blank")
                    audit.check(exported.get("model_status") == expected_model and
                                exported.get("manual_edition_status") == expected_edition and
                                exported.get("model_year_status") == expected_model_year,
                                "translations", f"{row_label}: missing identity statuses are not localised")
                    audit.check(exported.get("source_page_status_code") == AUDI_MANUAL_SOURCE_PAGE_STATUS and
                                exported.get("source_page_status") == expected_page,
                                "translations", f"{row_label}: photographed-page status is not localised")
                    if source_row.get("color") == "smisena_neurcena":
                        audit.check(exported.get("photo_colour") == AUDI_MANUAL_SPECIAL_COLOUR_LABELS[lang],
                                    "translations", f"{row_label}: mixed unresolved source colour is not localised")
                    try:
                        exported_graphics = json.loads(exported.get("graphic_occurrences_CS_json") or "[]")
                    except (TypeError, ValueError):
                        exported_graphics = None
                    audit.check(exported_graphics == source_row.get("graphic_occurrences"), "csv",
                                f"{row_label}: graphic occurrence inventory differs from JSON")
            inventory = audit.csv_rows(f"audi-manual-photo-inventory.{lang}.csv")
            if inventory is not None:
                ids = [row.get("working_photo_reference") for row in inventory]
                audit.check(len(ids) == len(set(ids)) and set(ids) == set(supplied_by_id), "csv",
                            f"audi-manual-photo-inventory.{lang}.csv: photo inventory differs from JSON")
                expected_model, expected_edition, expected_model_year, expected_review, expected_page = AUDI_MANUAL_INVENTORY_STATUS[lang]
                for exported in inventory:
                    row_label = f"audi-manual-photo-inventory.{lang}.csv:{exported.get('working_photo_reference', '')}"
                    source_photo = supplied_by_id.get(exported.get("working_photo_reference"), {})
                    audit.check(exported.get("printed_page") == str(source_photo.get("printed_page", "")) and
                                exported.get("row_count") == str(source_photo.get("row_count", "")) and
                                exported.get("graphic_occurrence_count") == str(source_photo.get("graphic_occurrence_count", "")), "csv",
                                f"{row_label}: printed page differs from JSON")
                    audit.check(exported.get("model_status") == expected_model and
                                exported.get("edition_status") == expected_edition and
                                exported.get("model_year_status") == expected_model_year and
                                exported.get("comparison_status") == expected_review,
                                "translations", f"{row_label}: inventory statuses are not localised")
                    audit.check(exported.get("page_status_code") == AUDI_MANUAL_SOURCE_PAGE_STATUS and
                                exported.get("page_status") == expected_page,
                                "translations", f"{row_label}: inventory page status is not localised")
    return row_ids


def check_photos_and_queues(audit, register, attachments, queues, cat=None):
    groups = {g["id"]: g for g in attachments["groups"]}
    latest = register["latest_round"]
    chosen = latest.get("requested_photos_scope_group_ids", [])
    audit.check(bool(chosen) and len(chosen) == len(set(chosen)), "photo_status", "latest_round: explicit nonduplicate photograph scope group IDs required")
    audit.check(set(chosen) <= set(groups), "photo_status", "latest_round: unknown photograph scope group")
    selected = [groups[i] for i in chosen if i in groups]
    for field, inventory_field in (("requested_photos_available", "available_in_conversation"),
                                   ("requested_photos_expected", "expected"),
                                   ("requested_photos_visually_compared", "visually_compared")):
        expected = sum(g[inventory_field] for g in selected)
        audit.check(latest.get(field) == expected, "photo_status", f"latest_round.{field}: expected {expected} from attachment-groups.json, found {latest.get(field)!r}")
    audit.check(latest.get("requested_photos_source") == "attachment-groups.json", "photo_status", "latest_round: authoritative attachment source is not declared")
    audit.check(bool(latest.get("requested_photos_expected_basis")), "photo_status", "latest_round: original expected count and overlapping/replacement photographs need an explicit counting basis")
    declared = {g["id"]: g for g in latest.get("requested_photos_by_group", [])}
    audit.check(set(declared) == set(chosen), "photo_status", "latest_round: group breakdown differs from explicit photograph scope")
    for group in selected:
        for field in ("expected", "available_in_conversation", "visually_compared", "unique_printed_pages_covered"):
            audit.check(declared.get(group["id"], {}).get(field) == group.get(field), "photo_status", f"latest_round:{group['id']}.{field}: differs from authoritative inventory")
    missing = {g["id"]: g for g in groups.values() if g["id"] not in chosen and g["available_in_conversation"] == 0}
    declared_missing = {g["id"]: g for g in latest.get("other_missing_requested_photo_groups", [])}
    audit.check(set(missing) == set(declared_missing), "photo_status", "latest_round: other missing photograph groups differ from inventory")
    for group_id, group in missing.items():
        for field in ("expected", "available_in_conversation"):
            audit.check(declared_missing.get(group_id, {}).get(field) == group[field], "photo_status", f"latest_round:{group_id}.{field}: other-missing count differs")
    audit.check(latest.get("other_missing_requested_photos_expected") == sum(g["expected"] for g in missing.values()), "photo_status", "latest_round: other missing photograph total differs")
    available_other = {g["id"]: g for g in groups.values() if g["id"] not in chosen and g["available_in_conversation"] > 0}
    declared_other = {g["id"]: g for g in latest.get("other_available_photo_groups_excluded_from_this_round", [])}
    audit.check(set(available_other) == set(declared_other), "photo_status", "latest_round: excluded available photo groups differ from inventory")
    for group_id, group in available_other.items():
        for field in ("expected", "available_in_conversation"):
            audit.check(declared_other.get(group_id, {}).get(field) == group[field], "photo_status", f"latest_round:{group_id}.{field}: excluded-available count differs")
    photo_evidence = {}
    for group in groups.values():
        name = group.get("row_comparison")
        if name:
            source = audit.read_json(name)
            photo_evidence[name] = source
            audit.check(source.get("photos_received") == group["available_in_conversation"], "photo_status", f"{name}: photos_received differs from attachment inventory")
            if name == "audi-photo-review.json" and cat is not None:
                check_audi_photo_review(audit, cat, source, group)
            if name == "audi-manual-photo-review.json" and cat is not None:
                check_audi_manual_photo_review(audit, cat, source, group)
    audi_path = HERE / "audi-photo-review.json"
    if audi_path.exists() and "audi-photo-review.json" not in photo_evidence:
        source = audit.read_json("audi-photo-review.json")
        photo_evidence["audi-photo-review.json"] = source
        if cat is not None:
            check_audi_photo_review(audit, cat, source)
        audit.check(any(g.get("row_comparison") == "audi-photo-review.json" for g in groups.values()),
                    "photo_status", "audi-photo-review.json: no attachment group row_comparison binding")
    audi_manual_path = HERE / "audi-manual-photo-review.json"
    if audi_manual_path.exists() and "audi-manual-photo-review.json" not in photo_evidence:
        source = audit.read_json("audi-manual-photo-review.json")
        photo_evidence["audi-manual-photo-review.json"] = source
        if cat is not None:
            check_audi_manual_photo_review(audit, cat, source)
        audit.check(any(g.get("row_comparison") == "audi-manual-photo-review.json" for g in groups.values()),
                    "photo_status", "audi-manual-photo-review.json: no attachment group row_comparison binding")
    source_bindings = []
    for group in queues["groups"]:
        for index, row in enumerate(group["rows"]):
            label = f"work-queues.json:{group['id']}.rows[{index}]"
            source_file = row.get("source_file")
            if source_file:
                path = audit.local_file(source_file, label)
                if path and path.suffix == ".json":
                    evidence = json.loads(path.read_text(encoding="utf-8"))
                    if "model_confirmed_by_user" in evidence:
                        check_photo_queue_identity(audit, row, evidence, label)
                    if evidence.get("schema") == "jasservis-audi-manual-photo-review-v1":
                        source_meta = evidence.get("source", {})
                        audit.check(row.get("brand") == "audi" and row.get("model") is None,
                                    "photo_identity", f"{label}: unidentified Audi manual queue must not claim a model")
                        audit.check(source_meta.get("model") is None and source_meta.get("edition") is None,
                                    "photo_identity", f"{label}: bound Audi manual evidence must retain unknown model and edition")
                        audit.check(not urlsplit(row.get("source_url") or "").scheme,
                                    "photo_identity", f"{label}: photographed manual queue must use its local evidence, not an external manual")
                        audit.check(row.get("meaning_verified") is False and
                                    row.get("exact_source_graphic_verified") is False and
                                    row.get("published") is False and
                                    row.get("source_edition_identified") is False and
                                    row.get("document_identity_established") is False,
                                    "photo_identity", f"{label}: photographed manual queue overclaims identity, meaning, graphic or publication")
                    source_bindings.append(Path(source_file).name)
            if group["id"] == "unverified-meanings-and-graphics":
                text = " ".join(row.get("remaining", {}).values())
                mentioned = [(name, evidence) for name, evidence in photo_evidence.items()
                             if evidence.get("model_confirmed_by_user") and
                             re.search(r"\b" + re.escape(evidence["model_confirmed_by_user"]) + r"\b", text, re.I)]
                if len(mentioned) == 1:
                    name, evidence = mentioned[0]
                    model = evidence["model_confirmed_by_user"]
                    audit.check(row.get("model") == model, "photo_identity", f"{label}: description concerns {model}, title says {row.get('model')!r}")
                    audit.check(bool(source_file), "photo_identity", f"{label}: photographed {model} work lacks a source_file link to its own review evidence")
                    audit.check(not urlsplit(row.get("source_url") or "").scheme, "photo_identity", f"{label}: photographed {model} work points to an external manual instead of its own review evidence")
                    if source_file:
                        audit.check(Path(source_file).name == name, "photo_identity", f"{label}: wrong photo review file for {model}")
    if "audi-photo-review.json" in photo_evidence:
        audit.check("audi-photo-review.json" in source_bindings, "photo_identity",
                    "audi-photo-review.json: work queue lacks a source_file binding")
    if "audi-manual-photo-review.json" in photo_evidence:
        audit.check("audi-manual-photo-review.json" in source_bindings, "photo_identity",
                    "audi-manual-photo-review.json: work queue lacks a source_file binding")
    return sum(g["available_in_conversation"] for g in selected)


def check_queue_csv(audit, queues):
    columns = ("queue", "brand", "model", "edition", "document_kind", "meaning_verified",
               "exact_graphic_verified", "published", "remaining", "source_url", "source_file")
    for lang in LANGS:
        name = f"work-queues.{lang}.csv"
        rows = audit.csv_rows(name)
        if rows is None:
            continue
        expected = []
        for group in queues["groups"]:
            for source in group["rows"]:
                row = {key: source.get(key, "") for key in columns}
                row.update(queue=group["id"], remaining=source["remaining"][lang])
                row["exact_graphic_verified"] = source.get("exact_source_graphic_verified", "")
                row["document_kind"] = source.get("document_kind") or source.get("source_kind") or ("owner-manual" if source.get("manual") else "")
                expected.append(tuple("" if row[key] is None else str(row[key]) for key in columns))
        actual = [tuple(row.get(key, "") for key in columns) for row in rows]
        missing, extra = Counter(expected) - Counter(actual), Counter(actual) - Counter(expected)
        audit.check(not missing and not extra, "csv", f"{name}: {sum(missing.values())} missing/changed and {sum(extra.values())} extra/changed queue rows")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.svg_sources = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag == "img" and attrs.get("src"):
            self.svg_sources.append(attrs["src"])


def local_target(page, url):
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc:
        return None, None
    path = (page.parent / unquote(parsed.path)).resolve() if parsed.path else page
    if parsed.path.endswith("/") or path.is_dir():
        path = path / "index.html"
    return path, unquote(parsed.fragment)


def check_pages(audit):
    paths = [ROOT / ("" if lang == "cs" else lang) / ROUTE / name for lang in LANGS for name in PAGE_NAMES]
    pages = {}
    for path in paths:
        audit.check(path.is_file(), "html", f"{path.relative_to(ROOT)}: missing audited route page")
        if path.is_file():
            parser = Page()
            parser.feed(path.read_text(encoding="utf-8"))
            repeated = sorted(x for x, count in Counter(parser.ids).items() if count > 1)
            audit.check(not repeated, "html", f"{path.relative_to(ROOT)}: duplicate HTML IDs {repeated}")
            pages[path.resolve()] = parser
    anchors = 0
    for path, parser in pages.items():
        label = str(path.relative_to(ROOT))
        for href in parser.links:
            target, fragment = local_target(path, href)
            if target in pages and fragment:
                anchors += 1
                audit.check(fragment in pages[target].ids, "html_anchors", f"{label}: missing target #{fragment} in {target.relative_to(ROOT)} (href={href!r})")
        for src in parser.svg_sources:
            target, _ = local_target(path, src)
            if target and target.suffix.lower() == ".svg" and ("wp-content/uploads/kontrolky" in target.as_posix() or "wp-content/uploads/infotainment" in target.as_posix()):
                audit.check(target.is_file(), "html_assets", f"{label}: missing catalogue SVG {src!r}")
    return len(pages), anchors

def check_infotainment(audit, catalogue_ids):
    root = REPO / "source-materials/infotainment-2026-10-31-rev2"
    manifest = json.loads((root / "internal/manifest.json").read_text(encoding="utf-8"))
    translations = json.loads((root / "translations.json").read_text(encoding="utf-8"))
    scopes = json.loads((root / "scope-translations.json").read_text(encoding="utf-8"))
    items = manifest["items"]
    ids = unique_ids(audit, items, "infotainment manifest items")
    audit.check(len(items) == 253, "infotainment", f"expected 253 infotainment meanings, found {len(items)}")
    audit.check(not ids.intersection(catalogue_ids), "infotainment", "infotainment IDs collide with warning catalogue IDs")
    audit.check(set(translations) == ids, "infotainment", "infotainment translations do not match item IDs")
    audit.check(set(scopes) == set(manifest["scopes"]), "infotainment", "scope translations do not match scope IDs")
    public_paths = set()
    for item in items:
        label = f"infotainment {item['id']}"
        audit.check(item["scope_id"] in manifest["scopes"], "infotainment", f"{label}: unknown scope")
        for lang in LANGS:
            value = translations.get(item["id"], {}).get(lang, {})
            audit.check(bool(value.get("name", "").strip()) and bool(value.get("meaning", "").strip()), "translations", f"{label}: missing {lang} text")
        relpath = Path(item["svg_file"]).relative_to("icons")
        path = ROOT / "wp-content/uploads/infotainment" / relpath
        public_paths.add(path)
        audit.check(path.is_file(), "infotainment", f"{label}: missing public SVG {relpath}")
        if path.is_file():
            content = path.read_bytes()
            audit.check(hashlib.sha256(content).hexdigest() == item["svg_sha256"], "infotainment", f"{label}: SVG hash mismatch")
            text = content.decode("utf-8", errors="replace")
            audit.check(not re.search(r"<image\b|data:image/|<script\b|https?://[^\s\"']+\.(?:png|jpe?g|webp)", text, re.I), "infotainment", f"{label}: SVG embeds a photo or script")
    audit.check(len(public_paths) == 235, "infotainment", f"expected 235 public SVG paths, found {len(public_paths)}")
    for lang in LANGS:
        page = ROOT / ("" if lang == "cs" else lang) / ROUTE / "index.html"
        html = page.read_text(encoding="utf-8")
        audit.check('class="wl-info-scope"' not in html, "infotainment", f"{lang}: public infotainment cards still expose model/system scope paragraphs")
    return {"semantic_items": len(items), "svg_paths": len(public_paths), "distinct_svg_hashes": len({x["svg_sha256"] for x in items})}

def check_online_services(audit):
    account_urls = {
        "https://www.myvolkswagen.net/cz/cs/myvolkswagen.html",
        "https://my.audi.com/", "https://skodaid.vwgroup.io/",
        "https://seatid.vwgroup.io/", "https://cupraid.vwgroup.io/",
    }
    help_urls = {
        "https://www.volkswagen.cz/technologie/konektivita/vw-connect",
        "https://www.audi.cz/servis-a-prislusenstvi/konektivita-a-technologie/audi-connect/nastaveni-sluzby",
        "https://www.skoda-auto.cz/konektivita/skoda-connect",
        "https://www.skoda-auto.cz/konektivita/myskoda",
        "https://www.seat.cz/servis-a-prislusenstvi/konektivita-a-technologie/seat-connect",
        "https://www.cupraofficial.cz/cupra-connect/cupra-connect-gen3",
        "https://www.cupra.com/en/faqs/cupra-connect/gen-4-general-information",
        "https://www.vw-uzitkove.cz/digitalni-sluzby-a-aplikace/vw-connect/aktivace",
    }
    first_tile = {"cs": "Můj Volkswagen", "en": "My Volkswagen", "de": "Mein Volkswagen"}
    for lang in LANGS:
        page = ROOT / ("" if lang == "cs" else lang) / ROUTE / "index.html"
        text = page.read_text(encoding="utf-8")
        label = f"{lang} online services"
        audit.check('class="online-brand-tile"' not in text and 'class="online-brand-tiles"' not in text, "online_services", f"{label}: online services must reuse the selected page brand")
        audit.check(text.count('class="online-brand-panel"') == 6, "online_services", f"{label}: expected six brand panels")
        audit.check('id="brand-advice" class="brand-advice" hidden' in text, "online_services", f"{label}: brand topic menu must be initially hidden")
        audit.check(text.count('<details class="driver-topic"') == 8, "online_services", f"{label}: expected eight equal main topic accordions")
        audit.check(text.find('id="identifikace-vozu-vin"') < text.find('id="prihlaseni-online-sluzby"') < text.find('id="kontrolky"'), "online_services", f"{label}: VIN, online services and warning-light topic order is wrong")
        audit.check(text.count('class="vin-brand-panel"') == 6, "online_services", f"{label}: expected six brand-aware VIN panels")
        audit.check(text.count('class="fuse-safety"') == 1 and text.find('class="fuse-safety"') > text.find('id="pojistky"'), "online_services", f"{label}: fuse safety notice is missing or misplaced")
        audit.check(text.count('class="fuse-swatch ') == 13 and text.count('class="fuse-colour-guide"') == 1, "online_services", f"{label}: fuse colour guide must contain 13 documented rows")
        audit.check(text.count('class="tyre-code-token"') == 7 and text.count('class="tyre-pressure-note"') == 1, "online_services", f"{label}: tyre code or pressure guidance is incomplete")
        coolant_start = text.find('<div class="coolant-guide">')
        coolant_end = text.find('<details class="driver-topic"', coolant_start + 1)
        coolant_html = text[coolant_start:coolant_end] if coolant_start >= 0 and coolant_end > coolant_start else ""
        audit.check(coolant_html.count('class="coolant-section"') == 5 and coolant_html.count('class="coolant-safety"') == 1, "online_services", f"{label}: coolant layout must contain one safety notice and five subtopics")
        audit.check(coolant_html.find('class="coolant-safety"') < coolant_html.find('class="coolant-accordion"') < coolant_html.find('class="coolant-section"'), "online_services", f"{label}: coolant safety notice must precede the uninterrupted accordion")
        audit.check('<details class="coolant-section" open' not in coolant_html and coolant_html.count('class="coolant-table ') == 2, "online_services", f"{label}: coolant subtopics must start closed and include both tables")
        audit.check(coolant_html.find('VW TL 774 G') < coolant_html.find('VW TL 774 J') < coolant_html.find('VW TL 774 L') < coolant_html.find('000 096 320 JG') < coolant_html.find('G 12E 050 A2'), "online_services", f"{label}: coolant specifications or product details are missing or out of order")
        audit.check('<details class="driver-topic" id="kontrolky"' in text, "online_services", f"{label}: warning lights must be a main topic accordion")
        audit.check('class="wl-intro"' not in text, "online_services", f"{label}: obsolete explanatory text remains below the brand tiles")
        audit.check('data-after-brand' not in text, "online_services", f"{label}: obsolete per-topic brand gating remains")
        warning_start=text.find('<details class="driver-topic" id="kontrolky"')
        audit.check(warning_start >= 0 and text.find('class="wl-contact"',warning_start) > warning_start, "online_services", f"{label}: warning contact block is not inside the warning topic")
        audit.check('wl-results-title' not in text and 'wl-vin-note' not in text and 'wl-brand-search' not in text, "online_services", f"{label}: obsolete catalogue heading, note or search remains")
        audit.check(text.count('<details class="wl-infotainment-section"') == 6, "online_services", f"{label}: every brand must have one collapsed infotainment section")
        audit.check('<section class="wl-info-category"' not in text and '<details class="wl-info-category"' in text, "online_services", f"{label}: infotainment categories must be nested accordions")
        audit.check(first_tile[lang] in text, "online_services", f"{label}: customer-facing brand labels are missing")
        for url in account_urls | help_urls:
            audit.check(url in text, "online_services", f"{label}: missing official URL {url}")
        audit.check(not re.search(r'<input[^>]+type=["\'](?:password|text)["\']', text, re.I), "online_services", f"{label}: must not contain a credential input")
        audit.check(not re.search(r'https?://[^"\']+(?:access_token|id_token|session=|oauth[^/]*\?)', text, re.I), "online_services", f"{label}: contains a temporary login URL")
    return {"brands": 6, "account_entry_urls": 5, "official_help_urls": len(help_urls)}


def main():
    audit = Audit()
    summary = {}
    try:
        cat = audit.read_json("catalog.json")
        locales = audit.read_json("locales.json")
        register = audit.read_json("review-register.json")
        attachments = audit.read_json("attachment-groups.json")
        queues = audit.read_json("work-queues.json")
        ids, hashes, summary = check_catalogue(audit, cat, locales)
        summary["infotainment"] = check_infotainment(audit, ids)
        summary["online_services"] = check_online_services(audit)
        check_csv(audit, cat, hashes)
        summary["whole_manuals_complete"] = check_reviews(audit, cat, register, queues)
        summary["selected_photos_available"] = check_photos_and_queues(audit, register, attachments, queues, cat)
        check_queue_csv(audit, queues)
        summary["html_pages"], summary["route_anchor_links"] = check_pages(audit)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        audit.errors.append(f"Cannot finish catalogue validation: {type(exc).__name__}: {exc}")
    print(json.dumps({"status": "FAIL" if audit.errors else "PASS", "counts": summary,
                      "checks": dict(sorted(audit.checks.items())), "skipped": audit.skipped,
                      "errors": audit.errors}, ensure_ascii=False, indent=2))
    return 1 if audit.errors else 0


if __name__ == "__main__":
    sys.exit(main())
