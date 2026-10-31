"""Regression checks for previously observed review-data and navigation defects."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import zipfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('warning_validation', HERE / 'validate.py')
validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validation)


class ReviewRegressionTests(unittest.TestCase):
    def setUp(self):
        self.audit = validation.Audit()
        self.register = json.loads((HERE / 'review-register.json').read_text())
        self.attachments = json.loads((HERE / 'attachment-groups.json').read_text())
        self.queues = json.loads((HERE / 'work-queues.json').read_text())
        self.catalogue = json.loads((HERE / 'catalog.json').read_text())

    def photo_checks(self):
        validation.check_photos_and_queues(self.audit, self.register, self.attachments, self.queues, self.catalogue)

    def test_original_zero_available_counter_is_rejected(self):
        self.register['latest_round']['requested_photos_available'] = 0
        self.photo_checks()
        self.assertTrue(any('requested_photos_available' in e for e in self.audit.errors))

    def test_wrong_model_cannot_inherit_photo_evidence(self):
        row = next(r for g in self.queues['groups'] for r in g['rows']
                   if r.get('source_file') == '_warnings/enyaq-photo-review.json')
        row['model'] = 'Octavia'
        row['edition'] = '11.2018'
        self.photo_checks()
        self.assertTrue(any('model' in e and 'Octavia' in e for e in self.audit.errors))

    def test_missing_photo_source_binding_is_rejected(self):
        row = next(r for g in self.queues['groups'] for r in g['rows']
                   if r.get('source_file') == '_warnings/enyaq-photo-review.json')
        del row['source_file']
        self.photo_checks()
        self.assertTrue(any('source_file' in e for e in self.audit.errors))

    def test_required_csv_cannot_be_silently_skipped(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(validation, 'HERE', Path(directory)):
                self.audit.csv_rows('coverage.csv')
        self.assertTrue(self.audit.errors)

    def test_original_invalid_brand_anchor_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for lang in validation.LANGS:
                relative = Path('' if lang == 'cs' else lang) / validation.ROUTE
                shutil.copytree(validation.ROOT / relative, root / relative)
            relative = Path('wp-content/uploads/kontrolky')
            shutil.copytree(validation.ROOT / relative, root / relative)
            page = root / validation.ROUTE / 'druha-kontrola.html'
            page.write_text(page.read_text().replace('</body>',
                '<a href="./?znacka=volkswagen#kontrolka-fatigue-volkswagen">invalid candidate</a></body>'))
            with patch.object(validation, 'ROOT', root):
                validation.check_pages(self.audit)
        self.assertTrue(any('kontrolka-fatigue-volkswagen' in e for e in self.audit.errors))

    def test_current_photo_bindings_and_counters_pass(self):
        self.photo_checks()
        self.assertEqual(self.audit.errors, [])

    def test_unknown_audi_model_cannot_be_claimed_by_queue(self):
        evidence = {
            'brand_id': 'audi', 'model_confirmed_by_user': None,
            'manual_edition': None, 'document_identity_established': False,
        }
        row = {
            'brand': 'audi', 'model': 'A8', 'edition': 'vehicle photos; edition undocumented',
            'source_edition_identified': False, 'source_url': None,
        }
        validation.check_photo_queue_identity(self.audit, row, evidence, 'synthetic Audi row')
        self.assertTrue(any('A8' in error and 'establishes no model' in error for error in self.audit.errors))

    def test_unknown_audi_photo_candidates_are_rejected(self):
        evidence = {
            'brand_id': 'audi', 'brand_confirmed_by_user': 'Audi',
            'model_confirmed_by_user': None, 'manual_edition': None,
            'model_year': None, 'generation': None,
            'document_identity_established': False,
            'photos_received': 1, 'photos_visually_inspected': 1,
            'photos': [{'id': 'audi-photo-01'}],
            'observations': [{
                'id': 'audi-observation-01',
                'occurrences': [{'photo': 'audi-photo-01', 'position': {'cs': 'uprostřed'}}],
                'candidate_catalogue_ids_not_model_verified': ['does-not-exist'],
                'matching_model_scoped_catalogue_ids': [],
                'published_from_this_photo_set': False,
                'exact_reusable_graphic_verified': False,
                'manual_edition': None, 'model_year': None,
            }],
        }
        validation.check_audi_photo_review(self.audit, self.catalogue, evidence, check_csv=False)
        self.assertTrue(any('does-not-exist' in error for error in self.audit.errors))

    def test_audi_photo_summary_sources_and_page_status_pass(self):
        path = HERE / 'audi-photo-review.json'
        if not path.exists():
            self.skipTest('Audi photo evidence not present')
        evidence = json.loads(path.read_text())
        validation.check_audi_photo_review(self.audit, self.catalogue, evidence, check_csv=False)
        self.assertEqual(self.audit.errors, [])

    def test_audi_vehicle_photo_cannot_claim_a_manual_page(self):
        path = HERE / 'audi-photo-review.json'
        if not path.exists():
            self.skipTest('Audi photo evidence not present')
        evidence = json.loads(path.read_text())
        evidence['observations'][0]['source_page'] = 11
        validation.check_audi_photo_review(self.audit, self.catalogue, evidence, check_csv=False)
        self.assertTrue(any('source_page must be explicit null' in error for error in self.audit.errors))

    def test_audi_occurrence_summary_and_photo_coverage_are_enforced(self):
        path = HERE / 'audi-photo-review.json'
        if not path.exists():
            self.skipTest('Audi photo evidence not present')
        evidence = json.loads(path.read_text())
        evidence['summary']['occurrence_count'] -= 1
        for row in evidence['observations']:
            row['occurrences'] = [x for x in row['occurrences'] if x.get('photo') != 'audi-photo-05']
        validation.check_audi_photo_review(self.audit, self.catalogue, evidence, check_csv=False)
        self.assertTrue(any('summary occurrence count differs' in error for error in self.audit.errors))
        self.assertTrue(any('every received photograph must be referenced' in error for error in self.audit.errors))

    def test_audi_manual_photo_review_counts_and_identity_pass(self):
        path = HERE / 'audi-manual-photo-review.json'
        if not path.exists():
            self.skipTest('Audi manual photo evidence not present')
        evidence = json.loads(path.read_text())
        validation.check_audi_manual_photo_review(self.audit, self.catalogue, evidence, check_csv=False)
        self.assertEqual(self.audit.errors, [])

    def test_audi_manual_cannot_claim_model_or_missing_page_coverage(self):
        path = HERE / 'audi-manual-photo-review.json'
        if not path.exists():
            self.skipTest('Audi manual photo evidence not present')
        evidence = json.loads(path.read_text())
        evidence['source']['model'] = 'A8'
        evidence['source']['missing_printed_pages'] = []
        evidence['rows'][0]['printed_page'] = 11
        validation.check_audi_manual_photo_review(self.audit, self.catalogue, evidence, check_csv=False)
        self.assertTrue(any('model must be explicit null' in error for error in self.audit.errors))
        self.assertTrue(any('missing printed page 11' in error for error in self.audit.errors))
        self.assertTrue(any('uncovered or missing printed page' in error for error in self.audit.errors))

    def test_audi_manual_graphic_count_and_separate_states_are_enforced(self):
        path = HERE / 'audi-manual-photo-review.json'
        if not path.exists():
            self.skipTest('Audi manual photo evidence not present')
        evidence = json.loads(path.read_text())
        evidence['counts']['graphic_occurrences'] -= 1
        evidence['rows'][0]['exact_reusable_graphic'] = True
        evidence['rows'][0]['model_scope_result'] = 'claimed_exact_model_scope'
        evidence['rows'][0]['published'] = True
        validation.check_audi_manual_photo_review(self.audit, self.catalogue, evidence, check_csv=False)
        self.assertTrue(any('103 graphic occurrences' in error for error in self.audit.errors))
        self.assertTrue(any('independently reusable exact graphic' in error for error in self.audit.errors))
        self.assertTrue(any('cannot claim exact model scope' in error for error in self.audit.errors))
        self.assertTrue(any('must not be promoted directly' in error for error in self.audit.errors))

    def test_audi_manual_legend_references_and_required_no_merges_are_enforced(self):
        evidence = json.loads((HERE / 'audi-manual-photo-review.json').read_text())
        evidence['source']['checkmark_legend']['en'] = ''
        next(row for row in evidence['rows'] if row['id'] == 'p10-left-04')['referenced_printed_pages'] = [274]
        evidence['must_not_merge'] = []
        validation.check_audi_manual_photo_review(self.audit, self.catalogue, evidence, check_csv=False)
        self.assertTrue(any('checkmark_legend.en' in error for error in self.audit.errors))
        self.assertTrue(any('pages 99 and 274' in error for error in self.audit.errors))
        self.assertTrue(any('loose-wheel/direct-wheel-change' in error for error in self.audit.errors))
        self.assertTrue(any('parking-control/unavailability' in error for error in self.audit.errors))

    def test_unidentified_audi_manual_queue_cannot_claim_a_model(self):
        row = next(r for g in self.queues['groups'] for r in g['rows']
                   if r.get('source_file') == '_warnings/audi-manual-photo-review.json')
        row['model'] = 'A7 Sportback'
        self.photo_checks()
        self.assertTrue(any('unidentified Audi manual queue must not claim a model' in error
                            for error in self.audit.errors))

    def test_audi_html_localises_codes_and_separates_review_states(self):
        if not (HERE / 'audi-photo-review.json').exists():
            self.skipTest('Audi photo evidence not present')
        headings = {
            'cs': ('Význam ověřen', 'Přesná použitelná grafika ověřena', 'Vloženo z fotografií'),
            'en': ('Meaning verified', 'Exact reusable graphic verified', 'Added from the photos'),
            'de': ('Bedeutung geprüft', 'Genaue nutzbare Grafik geprüft', 'Aus den Fotos ergänzt'),
        }
        for lang in validation.LANGS:
            page = validation.ROOT / ('' if lang == 'cs' else lang) / validation.ROUTE / 'druha-kontrola.html'
            text = page.read_text()
            section = text.split('id="audi-fotografie"', 1)[1].split('id="audi-q4-climate"', 1)[0]
            self.assertTrue(all(heading in section for heading in headings[lang]))
            for raw_code in ('warning-indicator', 'steady-visible', 'mmi-control', 'menu-tile'):
                self.assertNotIn(raw_code, section)

    def test_audi_manual_html_separates_semantic_graphic_model_and_publication(self):
        if not (HERE / 'audi-manual-photo-review.json').exists():
            self.skipTest('Audi manual photo evidence not present')
        headings = {
            'cs': ('Odkázané tištěné strany', 'Významový výsledek', 'Grafický výsledek', 'Modelová platnost', 'Publikováno z fotografií'),
            'en': ('Referenced printed pages', 'Semantic result', 'Graphic result', 'Model scope', 'Published from the photos'),
            'de': ('Verwiesene Druckseiten', 'Bedeutungsergebnis', 'Grafikergebnis', 'Modellgültigkeit', 'Aus den Fotos veröffentlicht'),
        }
        evidence = json.loads((HERE / 'audi-manual-photo-review.json').read_text())
        for lang in validation.LANGS:
            page = validation.ROOT / ('' if lang == 'cs' else lang) / validation.ROUTE / 'druha-kontrola.html'
            text = page.read_text()
            self.assertIn('id="audi-manual-fotografie"', text)
            section = text.split('id="audi-manual-fotografie"', 1)[1].split('id="audi-q4-climate"', 1)[0]
            self.assertTrue(all(heading in section for heading in headings[lang]))
            self.assertIn(evidence['source']['checkmark_legend'][lang], section)
            self.assertIn(validation.AUDI_MANUAL_SPECIAL_COLOUR_LABELS[lang], section)
            tbody = section.split('<tbody>', 1)[1].split('</tbody>', 1)[0]
            self.assertEqual(tbody.count('<tr>'), 102)
            drive_row = next(part for part in tbody.split('<tr>') if 'Hnací systém; Palubní síť' in part)
            self.assertIn('99, 274', drive_row)
            for raw_position in ('main1', 'left1', 'right1'):
                self.assertNotIn(raw_position, section)
            catalogue = validation.ROOT / ('' if lang == 'cs' else lang) / validation.ROUTE / 'index.html'
            self.assertNotIn(validation.AUDI_MANUAL_SPECIAL_COLOUR_LABELS[lang], catalogue.read_text())

    def test_review_export_manifest_and_file_bytes(self):
        with zipfile.ZipFile(HERE / 'catalog-review-export.zip') as archive:
            names = archive.namelist()
            self.assertEqual(len(names), len(set(names)))
            self.assertIsNone(archive.testzip())
            manifest = json.loads(archive.read('export-manifest.json'))
            self.assertTrue(manifest['manifest_excludes_itself'])
            self.assertEqual({x['path'] for x in manifest['files']}, set(names) - {'export-manifest.json'})
            for entry in manifest['files']:
                name = entry['path']
                data = archive.read(name)
                self.assertEqual(entry['size_bytes'], len(data), name)
                self.assertEqual(entry['sha256'], hashlib.sha256(data).hexdigest(), name)
                if name != 'README.txt':
                    source = validation.ROOT / name if name.startswith('wp-content/') else HERE / name
                    self.assertEqual(data, source.read_bytes(), name)
            required = {'coverage.csv', 'manual-review.csv', 'work-queues.cs.csv',
                        'work-queues.en.csv', 'work-queues.de.csv', 'verification.json'}
            if (HERE / 'audi-photo-review.json').exists():
                required.add('audi-photo-review.json')
                required.update(f'audi-photo-comparison.{lang}.csv' for lang in validation.LANGS)
                required.update(f'audi-photo-inventory.{lang}.csv' for lang in validation.LANGS)
            if (HERE / 'audi-manual-photo-review.json').exists():
                required.add('audi-manual-photo-review.json')
                required.update(f'audi-manual-photo-review.{lang}.csv' for lang in validation.LANGS)
                required.update(f'audi-manual-photo-inventory.{lang}.csv' for lang in validation.LANGS)
            self.assertTrue(required <= set(names))


if __name__ == '__main__':
    unittest.main()
