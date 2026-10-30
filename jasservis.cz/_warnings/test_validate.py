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

    def photo_checks(self):
        validation.check_photos_and_queues(self.audit, self.register, self.attachments, self.queues)

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
                '<a href="./?znacka=skoda#kontrolka-fatigue-skoda">invalid candidate</a></body>'))
            with patch.object(validation, 'ROOT', root):
                validation.check_pages(self.audit)
        self.assertTrue(any('kontrolka-fatigue-skoda' in e for e in self.audit.errors))

    def test_current_photo_bindings_and_counters_pass(self):
        self.photo_checks()
        self.assertEqual(self.audit.errors, [])

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
            self.assertTrue({'coverage.csv', 'manual-review.csv', 'work-queues.cs.csv',
                             'work-queues.en.csv', 'work-queues.de.csv'} <= set(names))


if __name__ == '__main__':
    unittest.main()
