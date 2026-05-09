#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug script to test HTML parsing"""

import sys
sys.path.insert(0, '.agent/skills/custom-seo/scripts')

from seo_core import fetch_with_retry, SEOAnalyzer, parse_with_beautifulsoup, HAS_BS4, get_human_headers

# Test fetching
print("=" * 60)
print("🔍 FETCHING HTML FROM example.com...")
print("=" * 60)

html = fetch_with_retry('https://example.com', max_retries=2, timeout=15)

if not html:
    print("❌ Failed to fetch HTML!")
    sys.exit(1)

# Add raw header debug for fetched page
print("\n🔧 RAW FETCH DEBUG:")
print("-" * 60)
import urllib.request, http.cookiejar
headers = get_human_headers()
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar), urllib.request.HTTPRedirectHandler())
req = urllib.request.Request('https://example.com', headers=headers)
with opener.open(req, timeout=20) as resp:
    print('STATUS', resp.status)
    print('HEADERS:')
    for k, v in resp.getheaders():
        print(f'  {k}: {v}')
    raw = resp.read()
    print('RAW LENGTH:', len(raw))
    print('RAW FIRST 100 BYTES HEX:', raw[:100].hex())
    try:
        print('RAW DECODE UTF-8 PREVIEW:', raw[:200].decode('utf-8', errors='replace'))
    except Exception as e:
        print('DECODE ERROR', e)
print("-" * 60)

print(f"✅ HTML fetched successfully: {len(html)} bytes\n")

# Show first 800 chars
print("📝 FIRST 800 CHARACTERS:")
print("-" * 60)
print(html[:800])
print("-" * 60)

# Check for key elements
print("\n🔍 KEY ELEMENT CHECKS:")
print(f"  • <title> tag present: {'<title>' in html}")
print(f"  • <meta> tags present: {'<meta' in html}")
print(f"  • 'description' attribute: {'description' in html}")
print(f"  • <h1> tags present: {'<h1>' in html}")
print(f"  • <h2> tags present: {'<h2>' in html}")

# Test HTMLParser
print("\n\n" + "=" * 60)
print("🧪 TESTING HTMLParser (SEOAnalyzer)...")
print("=" * 60)

try:
    parser = SEOAnalyzer()
    parser.feed(html)
    print(f"✅ HTMLParser completed successfully")
    print(f"   • Title: {parser.data['title'][:100] if parser.data['title'] else '(empty)'}")
    print(f"   • Meta Desc: {parser.data['meta_desc'][:100] if parser.data['meta_desc'] else '(empty)'}")
    print(f"   • H1 Count: {parser.data['h1_count']}")
    print(f"   • H2 Count: {parser.data['h2_count']}")
    print(f"   • Images: {parser.data['images_total']}")
    print(f"   • Visible text length: {len(parser.data['visible_text'])} chars")
except Exception as e:
    print(f"❌ HTMLParser error: {e}")
    import traceback
    traceback.print_exc()

# Test BeautifulSoup
print("\n\n" + "=" * 60)
print(f"🧪 TESTING BeautifulSoup (HAS_BS4={HAS_BS4})...")
print("=" * 60)

if HAS_BS4:
    try:
        bs_data = parse_with_beautifulsoup(html)
        if bs_data:
            print(f"✅ BeautifulSoup parsed successfully")
            print(f"   • Title: {bs_data.get('title', '')[:100] if bs_data.get('title') else '(empty)'}")
            print(f"   • Meta Desc: {bs_data.get('meta_desc', '')[:100] if bs_data.get('meta_desc') else '(empty)'}")
            print(f"   • H1 Count: {bs_data.get('h1_count', 0)}")
            print(f"   • H2 Count: {bs_data.get('h2_count', 0)}")
            print(f"   • Images: {bs_data.get('images_total', 0)}")
            print(f"   • Visible text length: {len(bs_data.get('visible_text', ''))} chars")
        else:
            print(f"⚠️  BeautifulSoup returned None")
    except Exception as e:
        print(f"❌ BeautifulSoup error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("⚠️  BeautifulSoup not installed")

print("\n" + "=" * 60)
print("✅ Debug complete!")
print("=" * 60)
