#!/usr/bin/env python3
"""
Phase 5: Convert root-relative paths (/path) to document-relative paths,
and fix broken social icons.

Works correctly on both GitHub Pages subpath (/jasservis/)
and the final custom domain (jasservis.cz).
"""

import os
import re
import sys

SITE_DIR = 'jasservis.cz'

def depth_of(html_path):
    """
    Return depth relative to SITE_DIR.
    jasservis.cz/index.html            → 0
    jasservis.cz/kontakt/index.html    → 1
    jasservis.cz/a/b/index.html        → 2
    """
    rel = os.path.relpath(html_path, SITE_DIR)
    parts = rel.replace('\\', '/').split('/')
    return len(parts) - 1  # subtract the filename itself

def make_relative(root_path, depth):
    """
    Convert '/wp-content/...' to 'wp-content/...' (depth 0)
    or '../wp-content/...' (depth 1), etc.
    """
    # strip leading slash
    stripped = root_path.lstrip('/')
    if depth == 0:
        return stripped
    else:
        return '../' * depth + stripped

def fix_html_attrs(content, depth):
    """
    Convert root-relative values in HTML attribute positions.
    Matches: href="/...", src="/...", data-anything="/...", action="/..."
    Does NOT touch: href="https://...", href="//...", href="#", href=""
    """
    attr_pat = re.compile(
        r'((?:href|src|action|data-[a-z-]+)=")(/(?!/)[^"]*?)(")',
        re.IGNORECASE
    )
    def replacer(m):
        attr_start = m.group(1)
        path = m.group(2)
        attr_end = m.group(3)
        return attr_start + make_relative(path, depth) + attr_end
    return attr_pat.sub(replacer, content)

def fix_js_vars(content, depth):
    """
    Fix the 4 known root-relative JS vars:
    system_folder, CHILD_URL, PARENT_URL, var image
    These use single-quoted string literals.
    """
    js_var_pat = re.compile(
        r"((?:system_folder|CHILD_URL|PARENT_URL|var image)\s*=\s*')(/[^']+)(')"
    )
    def replacer(m):
        return m.group(1) + make_relative(m.group(2), depth) + m.group(3)
    return js_var_pat.sub(replacer, content)

SOCIAL_OLD = (
    r'<li><a href="index\.html#" title="facebook"><img src="index\.html" alt="facebook"></a></li>'
    r'<li><a href="index\.html#" title="twitter"><img src="index\.html" alt="twitter"></a></li>'
    r'<li><a href="index\.html#" title="youtube"><img src="index\.html" alt="youtube"></a></li>'
)
SOCIAL_NEW = (
    '<li><a href="#" title="facebook"><i class="icon-facebook"></i></a></li>'
    '<li><a href="#" title="twitter"><i class="icon-twitter"></i></a></li>'
    '<li><a href="#" title="youtube"><i class="icon-youtube"></i></a></li>'
)

def fix_social_icons(content):
    """
    Replace broken <img src="index.html"> social icons with Font Awesome icons.
    Also remove motopress data attributes from wrapper.
    """
    # Fix the <li> items
    content = re.sub(SOCIAL_OLD, SOCIAL_NEW, content)
    # Remove motopress static-file data attributes from wrapper div
    content = re.sub(
        r'(<div class="social-nets-wrapper")[^>]*(>)',
        r'\1\2',
        content
    )
    return content

def process_file(html_path):
    d = depth_of(html_path)
    with open(html_path, 'r', encoding='utf-8') as f:
        original = f.read()

    content = original
    content = fix_html_attrs(content, d)
    content = fix_js_vars(content, d)
    content = fix_social_icons(content)

    if content != original:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    html_files = []
    for root, dirs, files in os.walk(SITE_DIR):
        # skip backup
        dirs[:] = [d for d in dirs if d != 'backup']
        for fn in files:
            if fn == 'index.html':
                html_files.append(os.path.join(root, fn))
    html_files.sort()

    changed = 0
    for path in html_files:
        d = depth_of(path)
        if process_file(path):
            changed += 1
            print(f'  fixed (depth={d}): {path}')
        else:
            print(f'  no change:         {path}')
    print(f'\nDone: {changed}/{len(html_files)} files changed.')

if __name__ == '__main__':
    main()
