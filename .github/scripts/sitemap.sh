#!/usr/bin/env bash
# Writes <site>/sitemap.xml: one entry per <dir>/index.html, with the date of
# the last commit that touched the page. Run at deploy time, so a page added
# through a PR shows up without anyone editing a list by hand.
#
# <site> is the built artifact (.pages-dist, untracked), <src> the tracked
# source it was built from: git dates come from <src>, the page list from
# <site>, so pages the build drops never make it into the sitemap.
#
# Needs full git history (actions/checkout with fetch-depth: 0); without it
# every page would get the date of the latest commit.
set -euo pipefail

site="${1:-jasservis.cz}"
base="${2:-https://jasservis.cz}"
src="${3:-$site}"

{
  echo '<?xml version="1.0" encoding="UTF-8"?>'
  echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
  find "$site" -name index.html -not -path "$site/wp-*" | LC_ALL=C sort | while read -r file; do
    path="${file#"$site"/}"
    path="${path%index.html}"
    lastmod="$(git log -1 --format=%cs -- "$src/${path}index.html" 2>/dev/null || true)"
    echo "  <url>"
    echo "    <loc>$base/$path</loc>"
    [ -n "$lastmod" ] && echo "    <lastmod>$lastmod</lastmod>"
    echo "  </url>"
  done
  echo '</urlset>'
} > "$site/sitemap.xml"

echo "sitemap.xml: $(grep -c '<loc>' "$site/sitemap.xml") pages"
