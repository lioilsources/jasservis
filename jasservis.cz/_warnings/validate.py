#!/usr/bin/env python3
"""Read-only integrity checks for the warning catalogue and its review evidence.

This checks relationships and generated artefacts, not automotive correctness.
It never repairs files, fetches remote sources or promotes a review to complete.
"""
from collections import Counter
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


def check_photos_and_queues(audit, register, attachments, queues):
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
    for group in queues["groups"]:
        for index, row in enumerate(group["rows"]):
            label = f"work-queues.json:{group['id']}.rows[{index}]"
            source_file = row.get("source_file")
            if source_file:
                path = audit.local_file(source_file, label)
                if path and path.suffix == ".json":
                    evidence = json.loads(path.read_text(encoding="utf-8"))
                    model = evidence.get("model_confirmed_by_user")
                    if model:
                        audit.check(row.get("model") == model, "photo_identity", f"{label}: model {row.get('model')!r} disagrees with photo evidence {model!r}")
                        if evidence.get("manual_edition") is None:
                            audit.check(row.get("source_edition_identified") is False, "photo_identity", f"{label}: unidentified photo edition must remain explicitly unestablished")
                            audit.check(bool(re.search(r"undocumented|nedoložen|unbelegt", row.get("edition", ""), re.I)), "photo_identity", f"{label}: title presents an unidentified photographed edition as established")
                        audit.check(not row.get("source_url"), "photo_identity", f"{label}: photo evidence must not inherit an unrelated manual URL")
            if group["id"] == "unverified-meanings-and-graphics":
                text = " ".join(row.get("remaining", {}).values())
                mentioned = [(name, evidence) for name, evidence in photo_evidence.items()
                             if re.search(r"\b" + re.escape(evidence.get("model_confirmed_by_user", "")) + r"\b", text, re.I)]
                if len(mentioned) == 1:
                    name, evidence = mentioned[0]
                    model = evidence["model_confirmed_by_user"]
                    audit.check(row.get("model") == model, "photo_identity", f"{label}: description concerns {model}, title says {row.get('model')!r}")
                    audit.check(bool(source_file), "photo_identity", f"{label}: photographed {model} work lacks a source_file link to its own review evidence")
                    audit.check(not urlsplit(row.get("source_url") or "").scheme, "photo_identity", f"{label}: photographed {model} work points to an external manual instead of its own review evidence")
                    if source_file:
                        audit.check(Path(source_file).name == name, "photo_identity", f"{label}: wrong photo review file for {model}")
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
            if target and target.suffix.lower() == ".svg" and "wp-content/uploads/kontrolky" in target.as_posix():
                audit.check(target.is_file(), "html_assets", f"{label}: missing catalogue SVG {src!r}")
    return len(pages), anchors


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
        check_csv(audit, cat, hashes)
        summary["whole_manuals_complete"] = check_reviews(audit, cat, register, queues)
        summary["selected_photos_available"] = check_photos_and_queues(audit, register, attachments, queues)
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
