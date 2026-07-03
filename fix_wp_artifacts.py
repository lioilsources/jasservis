#!/usr/bin/env python3
"""
Phase 6: Remove remaining WP artifacts from all HTML files.

A) Remove WP Gutenberg/block-editor polyfill scripts (unused by CherryFramework)
B) Remove reCAPTCHA script (no CF7 backend, Formspree has own spam protection)
C) Upgrade http://jasservis.cz → https://jasservis.cz in meta/JSON-LD
"""

import os
import re
import glob

SITE_DIR = 'jasservis.cz'

# A+B: Script tags to remove — match src containing these substrings
REMOVE_SCRIPT_SRCS = [
    'wp-polyfill-inert',
    'regenerator-runtime',
    'wp-polyfill.min',
    'comment-reply',
    'recaptcha/api.js',
]

script_tag_re = re.compile(
    r"<script\b[^>]*\bsrc=['\"]([^'\"]*)['\"][^>]*>\s*</script>",
    re.IGNORECASE
)

def remove_wp_scripts(content):
    def should_remove(m):
        src = m.group(1)
        return any(pat in src for pat in REMOVE_SCRIPT_SRCS)
    return script_tag_re.sub(lambda m: '' if should_remove(m) else m.group(0), content)

def upgrade_http_to_https(content):
    # Only upgrade jasservis.cz own domain — leave dns-prefetch hints etc. alone
    return content.replace('http://jasservis.cz', 'https://jasservis.cz')

def process_file(path):
    with open(path, encoding='utf-8') as f:
        original = f.read()

    content = original
    content = remove_wp_scripts(content)
    content = upgrade_http_to_https(content)

    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    files = sorted(glob.glob(f'{SITE_DIR}/**/index.html', recursive=True))
    changed = 0
    for path in files:
        if process_file(path):
            changed += 1
            print(f'  fixed: {path}')
        else:
            print(f'  clean: {path}')
    print(f'\nDone: {changed}/{len(files)} files changed.')

    print('\n--- Verification ---')
    for label, pattern in [
        ('WP polyfills', r'wp-polyfill|regenerator-runtime|comment-reply'),
        ('reCAPTCHA',   r'recaptcha'),
        ('http://jasservis.cz', r'http://jasservis\.cz'),
    ]:
        hits = []
        for path in files:
            with open(path, encoding='utf-8') as f:
                content = f.read()
            count = len(re.findall(pattern, content))
            if count:
                hits.append(f'{path}:{count}')
        status = 'CLEAN' if not hits else f'REMAINING: {hits}'
        print(f'  {label}: {status}')

if __name__ == '__main__':
    main()
