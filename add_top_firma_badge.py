#!/usr/bin/env python3
"""
Add the "TOP firma 2025" Firmy.cz badge right after the logo in the
sticky header bar (.header_block_2), before the "Úvod" nav item.

Placed as a plain inline-block element right after the logo link (before
the hidden .logo_tagline paragraph) rather than absolutely positioned —
.logo is a floated, auto-width div, and an absolutely positioned child
anchored with left:100% ended up clipped out of view by
#motopress-main.main-holder's overflow:hidden. Normal inline flow avoids
that whole class of bug.
"""

import glob

SITE_DIR = 'jasservis.cz'

BADGE_LINK = (
    '<a href="https://www.firmy.cz/detail/12996882-j-s-servis-jaroslav-mateju-statenice.html" '
    'target="_blank" rel="noopener" class="top-firma-badge" title="TOP firma 2025 – Firmy.cz">'
    '<img src="https://www.firmy.cz/top-firma/2025.svg" width="138" height="120" '
    'alt="TOP firma 2025" loading="lazy"></a>'
)

ANCHOR = '<p class="logo_tagline">'
REPLACEMENT = BADGE_LINK + '\n\t' + ANCHOR

def process_file(path):
    with open(path, encoding='utf-8') as f:
        content = f.read()

    count = content.count(ANCHOR)
    if count != 1:
        raise RuntimeError(f'{path}: expected exactly 1 anchor, found {count}')

    content = content.replace(ANCHOR, REPLACEMENT, 1)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    files = sorted(glob.glob(f'{SITE_DIR}/**/index.html', recursive=True))
    for path in files:
        process_file(path)
        print(f'  badge added: {path}')
    print(f'\nDone: {len(files)} files updated.')

if __name__ == '__main__':
    main()
