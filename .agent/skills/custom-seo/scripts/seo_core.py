import urllib.request
import urllib.error
from html.parser import HTMLParser
import json
import csv
import re
import sys
import os
import html as html_module
import random
import time
import http.cookiejar
import gzip
import io
try:
    import brotli
    HAS_BROTLI = True
except ImportError:
    HAS_BROTLI = False
from ai_insights import AIInsights
from auto_fix_generator import AutoFixGenerator
from datetime import datetime

# ✅ TRY importing BeautifulSoup for robust HTML parsing
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

# ==========================================
# 🎭 HUMAN-LIKE BEHAVIOR FUNCTIONS (Stealth Mode)
# ==========================================
def get_human_headers():
    """Realistic browser headers return karega — random + complete"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
    ]
    
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,en-GB;q=0.8,en-CA;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "Referer": "https://www.google.com/",
        "TE": "trailers"
    }

def human_delay(min_sec=2, max_sec=7):
    """Human-like random delay add karega"""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)

def create_stealth_session():
    """Cookie jar ke saath stealth session banaye"""
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookie_jar),
        urllib.request.HTTPRedirectHandler()
    )
    opener.addheaders = list(get_human_headers().items())
    return opener

def decompress_response(response_data, encoding_header=None):
    """✅ NEW: Decompress gzip/deflate/br content"""
    # Check for gzip magic bytes (0x1f 0x8b)
    if response_data[:2] == b'\x1f\x8b':
        try:
            return gzip.GzipFile(fileobj=io.BytesIO(response_data)).read()
        except Exception as e:
            print(f"  ⚠️  GZIP decompression failed: {str(e)[:50]}")
            return response_data
    
    # Check for Brotli
    if encoding_header and 'br' in encoding_header.lower():
        if HAS_BROTLI:
            try:
                return brotli.decompress(response_data)
            except Exception as e:
                print(f"  ⚠️  Brotli decompression failed: {str(e)[:50]}")
                return response_data
        else:
            print("  ⚠️  Brotli encoding detected but brotli module not installed.")
            return response_data
    
    # Check for deflate
    if encoding_header and 'deflate' in encoding_header.lower():
        try:
            import zlib
            return zlib.decompress(response_data)
        except Exception as e:
            print(f"  ⚠️  Deflate decompression failed: {str(e)[:50]}")
            return response_data
    
    return response_data

def fetch_with_retry(url, max_retries=3, timeout=20):
    """Retry logic + human-like behavior + GZIP decompression"""
    for attempt in range(max_retries):
        try:
            # Human-like delay before each attempt
            human_delay(3 if attempt > 0 else 2, 8 if attempt > 0 else 5)
            
            # Create fresh session with new headers each time
            opener = create_stealth_session()
            req = urllib.request.Request(url, headers=get_human_headers())
            
            with opener.open(req, timeout=timeout) as resp:
                response_data = resp.read()
                encoding = resp.getheader('Content-Encoding', '')
                
                # ✅ NEW: Decompress if needed
                response_data = decompress_response(response_data, encoding)
                
                # Try different encodings
                for text_encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
                    try:
                        return response_data.decode(text_encoding, errors='ignore')
                    except:
                        continue
                return response_data.decode('utf-8', errors='ignore')
                
        except urllib.error.HTTPError as e:
            if e.code in [403, 429, 503]:  # Forbidden, Too Many Requests, Service Unavailable
                print(f"  ⚠️  Attempt {attempt+1}: Blocked ({e.code}), retrying with new headers...")
                if attempt == max_retries - 1:
                    print(f"  ❌ Failed after {max_retries} attempts: {e}")
                    return None
                continue
            elif e.code == 404:
                print(f"  ❌ Page not found (404): {url}")
                return None
            else:
                raise
        except urllib.error.URLError as e:
            if attempt == max_retries - 1:
                print(f"  ❌ Connection error: {e.reason}")
                return None
            continue
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"  ❌ Unexpected error: {e}")
                return None
            continue
    return None

def check_platform_compatibility(url):
    """Check if platform is supported + warn user about limitations"""
    domain = url.lower()
    
    # JavaScript-heavy platforms that may block or return incomplete data
    js_heavy = ['facebook.com', 'instagram.com', 'twitter.com', 'x.com', 'tiktok.com', 
                'linkedin.com', 'pinterest.com', 'etsy.com', 'amazon.com']
    
    # Platforms that work well with static parsing
    well_supported = ['wordpress', 'shopify', 'wix', 'squarespace', 'blogger', 
                      'medium.com', 'github.io', 'vercel.app', 'netlify.app']
    
    if any(p in domain for p in js_heavy):
        platform = [p for p in js_heavy if p in domain][0]
        print(f"\n⚠️  Notice: {platform} uses JavaScript rendering.")
        print("   • Some content may not be detected (dynamic loading)")
        print("   • For 100% accurate audits, test on static sites first")
        print("   • Still proceeding with best-effort analysis...\n")
        return 'limited'
    
    if any(p in domain for p in well_supported):
        return 'full'
    
    return 'unknown'

# ==========================================
# 🎬 PLAYWRIGHT SUPPORT (For JavaScript-Heavy Sites)
# ==========================================
def fetch_with_playwright(url, timeout=30):
    """✅ NEW: Playwright ke saath JavaScript-rendered content fetch karo"""
    try:
        from playwright.sync_api import sync_playwright
        print(f"  📱 Using Playwright for dynamic content rendering...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_extra_http_headers(get_human_headers())
            page.goto(url, wait_until="networkidle", timeout=timeout*1000)
            time.sleep(2)  # Wait for any late-loading content
            html = page.content()
            browser.close()
            return html
    except ImportError:
        print(f"  ⚠️  Playwright not installed. Installing...")
        os.system("pip install playwright -q && playwright install -q")
        return fetch_with_playwright(url, timeout)
    except Exception as e:
        print(f"  ⚠️  Playwright failed ({str(e)[:50]}), falling back to urllib...")
        return None

def fetch_html_smart(url):
    """✅ NEW: Auto-detect if site needs Playwright or regular fetch"""
    domain = url.lower()
    js_heavy = ['facebook.com', 'instagram.com', 'twitter.com', 'x.com', 'tiktok.com', 
                'linkedin.com', 'pinterest.com', 'etsy.com', 'amazon.com']
    
    if any(p in domain for p in js_heavy):
        html = fetch_with_playwright(url)
        if html: return html
    
    return fetch_with_retry(url, max_retries=3, timeout=20)

# ==========================================
# 1. HTML PARSER
# ==========================================
class SEOAnalyzer(HTMLParser):
    def __init__(self):
        super().__init__()
        self.data = {
            "title": "", "meta_desc": "", "h1_count": 0, "h2_count": 0,
            "canonical": "", "robots": "", "schema_found": False,
            "images_total": 0, "images_with_alt": 0,
            "internal_links": 0, "external_links": 0,
            "status_code": 200, "url": "", "visible_text": ""
        }
        self._in_title = False
        self._in_meta = False
        self._meta_name = ""
        self._meta_content = ""
        self._in_script_style = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag in ('script', 'style'): self._in_script_style = True
        elif tag == "title": self._in_title = True
        elif tag == "meta":
            self._in_meta = True
            meta_name = attrs_dict.get("name", attrs_dict.get("property", "")).lower()
            meta_content = attrs_dict.get("content", "")
            # ✅ FIX: Capture meta description immediately from content attribute
            if meta_name == "description": self.data["meta_desc"] = meta_content
            if meta_name == "robots": self.data["robots"] = meta_content
        elif tag == "link" and attrs_dict.get("rel", "").lower() == "canonical":
            self.data["canonical"] = attrs_dict.get("href", "")
        elif tag == "h1": self.data["h1_count"] += 1
        elif tag == "h2": self.data["h2_count"] += 1
        elif tag == "img":
            self.data["images_total"] += 1
            if attrs_dict.get("alt", "").strip(): self.data["images_with_alt"] += 1
        elif tag == "a":
            href = attrs_dict.get("href", "")
            if href.startswith("http"): self.data["external_links"] += 1
            elif href.startswith("/"): self.data["internal_links"] += 1
        elif tag == "script" and attrs_dict.get("type", "") == "application/ld+json":
            self.data["schema_found"] = True

    def handle_data(self, data):
        if self._in_title: self.data["title"] += data
        if not self._in_script_style: self.data["visible_text"] += " " + data

    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self._in_script_style = False
        if tag == "title": self._in_title = False
        if tag == "meta": self._in_meta = False

# ==========================================
# 🎨 BEAUTIFULSOUP-based PARSER (Fallback for robust parsing)
# ==========================================
def parse_with_beautifulsoup(html):
    """✅ NEW: More robust HTML parsing using BeautifulSoup"""
    if not HAS_BS4:
        return None
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        data = {
            "title": "", "meta_desc": "", "h1_count": 0, "h2_count": 0,
            "canonical": "", "robots": "", "schema_found": False,
            "images_total": 0, "images_with_alt": 0,
            "internal_links": 0, "external_links": 0,
            "visible_text": ""
        }
        
        # Title
        title_tag = soup.find('title')
        if title_tag:
            data['title'] = title_tag.get_text().strip()
        
        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', meta.get('property', '')).lower()
            content = meta.get('content', '')
            if name == 'description': data['meta_desc'] = content
            if name == 'robots': data['robots'] = content
        
        # Canonical
        canonical = soup.find('link', {'rel': 'canonical'})
        if canonical:
            data['canonical'] = canonical.get('href', '')
        
        # Headings
        data['h1_count'] = len(soup.find_all('h1'))
        data['h2_count'] = len(soup.find_all('h2'))
        
        # Images
        images = soup.find_all('img')
        data['images_total'] = len(images)
        data['images_with_alt'] = len([img for img in images if img.get('alt', '').strip()])
        
        # Links
        for a in soup.find_all('a'):
            href = a.get('href', '')
            if href.startswith('http'): data['external_links'] += 1
            elif href.startswith('/'): data['internal_links'] += 1
        
        # Schema
        data['schema_found'] = bool(soup.find('script', {'type': 'application/ld+json'}))
        
        # Visible text
        for script in soup(["script", "style"]):
            script.decompose()
        data['visible_text'] = ' '.join(soup.get_text().split())
        
        return data
    except Exception as e:
        return None

# ==========================================
# 2. MOBILE-FRIENDLY CHECKER
# ==========================================
def check_mobile_friendly(html):
    checks = {"viewport_meta": False, "responsive_css": False, "mobile_optimized": False, "score": 0}
    if 'name="viewport"' in html or "name='viewport'" in html:
        checks["viewport_meta"] = True
        checks["score"] += 50
    if "@media" in html or "max-width" in html or ".mobile" in html.lower():
        checks["responsive_css"] = True
        checks["score"] += 30
    if any(sig in html.lower() for sig in ['mobile', 'responsive', 'viewport', 'handheld']):
        checks["mobile_optimized"] = True
        checks["score"] += 20
    return checks

# ==========================================
# 3. PAGE SPEED CHECKER (Stealth Enhanced)
# ==========================================
def check_page_speed(url):
    try:
        start_time = time.time()
        html = fetch_with_retry(url, max_retries=2, timeout=15)
        if not html:
            return {"error": "Could not fetch page", "performance_score": 0, "load_time_seconds": 0, "page_size_kb": 0}
        
        load_time = round(time.time() - start_time, 2)
        page_size_kb = round(len(html.encode('utf-8')) / 1024, 2)
        
        score = 100
        if load_time > 5: score -= 40
        elif load_time > 3: score -= 20
        elif load_time > 2: score -= 10
        if page_size_kb > 2000: score -= 30
        elif page_size_kb > 1000: score -= 15
        
        return {"performance_score": max(0, score), "load_time_seconds": load_time, "page_size_kb": page_size_kb}
    except Exception as e:
        return {"error": str(e), "performance_score": 0, "load_time_seconds": 0, "page_size_kb": 0}

# ==========================================
# 4. KEYWORD DENSITY ANALYZER
# ==========================================
def analyze_keyword_density(text):
    # ✅ FIX: Improved stop words list to avoid garbage data
    stop_words = {'the','and','for','are','but','not','you','all','can','had','her','was','one','our','out','has','have','been','this','that','from','they','with','she','which','their','will','each','about','many','what','when','where','how','who','did','get','its','may','say','use','page','home','click','here','read','more','view','details','menu','search','login','signup','cart','checkout','contact','privacy','terms','cookie','or','by','to','in','is','it','a','an','as','be','do','if','no','of','on','so','up','us','we','at','be','he','me','my','or','be','do','go','he','if','in','is','it','me','my','no','of','on','or','so','to','up','us','we','am','i','html','css','js','lrl','fzi','xyz','abc','www'}
    # ✅ FIX: Match words with 4+ characters to avoid noise
    words = re.findall(r'\b[a-z]{4,}\b', text.lower())
    if not words: return {"top_keywords": [], "density": {}}
    freq = {}
    for w in words:
        if w not in stop_words and len(w) > 3: freq[w] = freq.get(w, 0) + 1
    total = len([w for w in words if w not in stop_words and len(w) > 3])
    if total == 0: return {"top_keywords": [], "density": {}}
    top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]
    density = {w: round((c / total) * 100, 2) for w, c in top}
    return {"top_keywords": [w for w, _ in top], "density": density}

# ==========================================
# 5. HELPER FUNCTIONS
# ==========================================
def calculate_overall_score(data):
    mobile = data.get('mobile_friendly', {}).get('score', 0)
    speed = data.get('page_speed', {}).get('performance_score', 0)
    technical = calculate_technical_score(data)
    return round((mobile + speed + technical) / 3)

def calculate_technical_score(data):
    score = 0
    if data.get('title'): score += 20
    if data.get('meta_desc'): score += 20
    if data.get('h1_count', 0) == 1: score += 20
    if data.get('images', {}).get('with_alt', 0) > 0: score += 20
    if data.get('schema_found'): score += 20
    return score

def get_status(score):
    if score >= 90: return "Excellent"
    elif score >= 70: return "Good"
    elif score >= 50: return "Average"
    else: return "Needs Improvement"

# ==========================================
# 6. PDF REPORT GENERATOR (Ultra Pro Max)
# ==========================================
def generate_pdf_report(data, output_file=None):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Preformatted
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        import tkinter as tk
        from tkinter import filedialog
        
        # Save Dialog
        if output_file is None:
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            output_file = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=f"SEO_Audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                title="Save SEO Report As..."
            )
            root.destroy()
            if not output_file:
                print("\n❌ Save cancelled by user.")
                return False
        
        # PDF Setup - A4 with professional margins
        doc = SimpleDocTemplate(output_file, pagesize=A4,
                               rightMargin=1.5*cm, leftMargin=1.5*cm,
                               topMargin=1.5*cm, bottomMargin=1.5*cm)
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom Professional Styles
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
            fontSize=22, textColor=colors.HexColor('#1a237e'), spaceAfter=15,
            alignment=TA_CENTER, fontName='Helvetica-Bold')
        heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'],
            fontSize=13, textColor=colors.HexColor('#0d47a1'), spaceAfter=8,
            spaceBefore=12, fontName='Helvetica-Bold')
        normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'],
            fontSize=9, textColor=colors.black, fontName='Helvetica', leading=11)
        
        # Header with branding
        elements.append(Paragraph("🔍 SEO AUDIT REPORT", title_style))
        elements.append(Spacer(1, 0.2*cm))
        
        # URL & Date (with truncation)
        url_text = data.get('url', 'N/A')
        if len(url_text) > 60: url_text = url_text[:57] + "..."
        elements.append(Paragraph(f"<b>URL:</b> {url_text}", normal_style))
        elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", normal_style))
        elements.append(Spacer(1, 0.4*cm))
        
        # Overall Score Box (Eye-catching)
        overall_score = calculate_overall_score(data)
        score_color = colors.green if overall_score >= 80 else colors.orange if overall_score >= 60 else colors.red
        score_label_style = ParagraphStyle('ScoreLabel', parent=styles['Normal'], alignment=TA_CENTER,
            fontSize=14, leading=18, fontName='Helvetica-Bold', textColor=colors.HexColor('#1a237e'))
        score_value_style = ParagraphStyle('ScoreValue', parent=styles['Normal'], alignment=TA_CENTER,
            fontSize=42, leading=46, fontName='Helvetica-Bold', textColor=score_color)
        score_box = Table([
            [Paragraph('OVERALL SEO SCORE', score_label_style)],
            [Paragraph(f'{overall_score}/100', score_value_style)]
        ], colWidths=[17*cm])
        score_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e3f2fd')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOX', (0, 0), (-1, -1), 2.5, colors.HexColor('#1a237e')),
            ('PADDING', (0, 0), (-1, -1), 16),
            ('ROUNDEDCORNERS', [5, 5, 5, 5]),
        ]))
        elements.append(score_box)
        elements.append(Spacer(1, 0.5*cm))
        
        # Key Metrics Table
        elements.append(Paragraph("📊 KEY METRICS", heading_style))
        mobile = data.get('mobile_friendly', {}).get('score', 0)
        speed = data.get('page_speed', {}).get('performance_score', 0)
        metrics_data = [
            [Paragraph('<b>Metric</b>', normal_style), Paragraph('<b>Score</b>', normal_style), Paragraph('<b>Status</b>', normal_style)],
            ['Overall SEO', f"{overall_score}/100", get_status(overall_score)],
            ['Mobile Friendly', f"{mobile}/100", get_status(mobile)],
            ['Page Speed', f"{speed}/100", get_status(speed)]
        ]
        metrics_table = Table(metrics_data, colWidths=[6*cm, 4.5*cm, 4.5*cm])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(metrics_table)
        elements.append(Spacer(1, 0.5*cm))
        
        # Technical Details (Clean, no HTML tags)
        elements.append(Paragraph("🔧 TECHNICAL DETAILS", heading_style))
        title = data.get('title', 'N/A') or "Not detected"
        meta = data.get('meta_desc', '') or "Missing"
        if len(title) > 45: title = title[:42] + "..."
        if len(meta) > 45: meta = meta[:42] + "..."
        
        tech_data = [
            ['Title', title],
            ['Meta Description', meta],
            ['H1/H2 Tags', f"{data.get('h1_count', 0)} / {data.get('h2_count', 0)}"],
            ['Images (with Alt)', f"{data.get('images', {}).get('with_alt', 0)}/{data.get('images', {}).get('total', 0)}"],
            ['Links (Int/Ext)', f"{data.get('links', {}).get('internal', 0)}/{data.get('links', {}).get('external', 0)}"],
            ['Schema Markup', '✅ Yes' if data.get('schema_found') else '❌ No'],
            ['Canonical URL', '✅ Yes' if data.get('canonical') else '❌ No']
        ]
        tech_table = Table(tech_data, colWidths=[5*cm, 12*cm])
        tech_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(tech_table)
        elements.append(Spacer(1, 0.5*cm))
        
        # AI Recommendations Table
        ai_data = data.get("ai_recommendations", {})
        if ai_data and ai_data.get("recommendations"):
            elements.append(Paragraph("🤖 AI RECOMMENDATIONS", heading_style))
            recs = ai_data["recommendations"]
            rec_data = [['Priority', 'Issue', 'Impact']]
            for r in recs[:5]:
                issue = r.get("issue", "")
                if len(issue) > 28: issue = issue[:25] + "..."
                rec_data.append([r.get("priority", ""), issue, r.get("impact", "")[:25]])
            rec_table = Table(rec_data, colWidths=[2.5*cm, 8.5*cm, 6*cm])
            rec_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            elements.append(rec_table)
            elements.append(Spacer(1, 0.5*cm))
        
        # Quick Fixes Section (Copy-Paste Ready Code)
        auto_fixes = data.get("auto_fixes", [])
        if auto_fixes:
            elements.append(Paragraph("🛠️ QUICK FIXES (Copy-Paste Ready)", heading_style))
            for i, fix in enumerate(auto_fixes[:3], 1):
                elements.append(Paragraph(f"<b>#{i}. {fix['issue']}</b>", normal_style))
                elements.append(Paragraph(f"📍 Location: {fix['location']}", normal_style))
                
                # ✅ FIXED: Use raw code (NO HTML escape) + proper wrapping in Table
                code = fix['code']
                
                # Split long lines to prevent word-breaking
                code_lines = code.split('\n')
                code_display = '\n'.join(code_lines)
                
                # Use Table for better wrapping and alignment
                code_style = ParagraphStyle('CodeStyle', parent=styles['Code'],
                    fontSize=8, textColor=colors.HexColor('#1a237e'), 
                    backColor=colors.HexColor('#f5f5f5'),
                    fontName='Courier', leading=10,
                    leftIndent=5, rightIndent=5)
                
                code_para = Paragraph(f"<tt>{html_module.escape(code_display)}</tt>", code_style)
                code_table = Table([[code_para]], colWidths=[16*cm])
                code_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
                    ('BORDER', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
                    ('PADDING', (0, 0), (-1, -1), 8),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ]))
                elements.append(code_table)
                elements.append(Spacer(1, 0.3*cm))
        
        # Footer
        elements.append(Spacer(1, 0.5*cm))
        footer_style = ParagraphStyle('Footer', parent=styles['Normal'],
            fontSize=8, textColor=colors.grey, alignment=TA_CENTER, fontName='Helvetica-Oblique')
        elements.append(Paragraph("Generated by Mr Moosa AI SEO Agent • 100% Free & Open Source", footer_style))
        
        # Build PDF
        doc.build(elements)
        print(f"\n✅ PDF Report saved to: {output_file}")
        return True
        
    except ImportError as e:
        print(f"\n⚠️  Error: {e}")
        print("Please install reportlab: pip install reportlab")
        return False
    except Exception as e:
        print(f"\n❌ PDF generation error: {e}")
        import traceback
        traceback.print_exc()
        return False

# ==========================================
# 7. BULK AUDITOR (Stealth Enhanced)
# ==========================================
def run_bulk_audit(input_source, output_file="seo_report.csv"):
    urls = []
    if os.path.isfile(input_source):
        with open(input_source, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    else:
        urls = [u.strip() for u in input_source.split(',') if u.strip()]
    if not urls:
        print("❌ No valid URLs found.")
        return
    print(f"🔍 Starting Bulk Audit for {len(urls)} URLs...")
    fieldnames = ["url", "status_code", "title", "meta_desc", "h1_count", "mobile_score", "page_speed_score", "top_keywords", "keyword_density", "timestamp"]
    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] 🔍 Auditing: {url}")
            try:
                data = analyze_single_url(url)
                row = {
                    "url": url, "status_code": data.get("status_code", "Error"),
                    "title": data.get("title", "")[:50], "meta_desc": data.get("meta_desc", "")[:80],
                    "h1_count": data.get("h1_count", 0),
                    "mobile_score": data.get("mobile_friendly", {}).get('score', 0),
                    "page_speed_score": data.get("page_speed", {}).get("performance_score", 0),
                    "top_keywords": ", ".join(data.get("keyword_density", {}).get("top_keywords", [])[:3]),
                    "keyword_density": str(data.get("keyword_density", {}).get("density", {})),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                writer.writerow(row)
                # Delay between URLs to avoid rate limiting
                if i < len(urls):
                    human_delay(3, 6)
            except Exception as e:
                print(f"  ⚠️ Error: {e}")
                writer.writerow({"url": url, "status_code": f"Error: {e}", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    print(f"\n✅ Bulk Audit Complete! Report saved to: {os.path.abspath(output_file)}")

# ==========================================
# 8. CORE ANALYZER (Ultra Pro Max Stealth)
# ==========================================
def analyze_single_url(url):
    # Platform compatibility check
    platform_status = check_platform_compatibility(url)
    
    try:
        # ✅ NEW: Smart fetch - uses Playwright for JS-heavy sites, urllib for others
        html = fetch_html_smart(url)
        if not html:
            return {"error": "Could not fetch page (blocked or unreachable)", "status_code": 0, "url": url}
        
        status = 200  # If we got HTML, consider it success
        
    except Exception as e:
        return {"error": str(e), "status_code": 0, "url": url}
    
    # ✅ NEW: Try BeautifulSoup first (more robust), fall back to HTMLParser
    parser_data = None
    if HAS_BS4:
        parser_data = parse_with_beautifulsoup(html)
    
    if not parser_data:
        # Fallback to custom HTMLParser
        parser = SEOAnalyzer()
        parser.feed(html)
        parser_data = parser.data
    
    result = {
        "url": url, "status_code": status,
        "title": parser_data.get("title", "").strip(), "meta_desc": parser_data.get("meta_desc", "").strip(),
        "h1_count": parser_data.get("h1_count", 0), "h2_count": parser_data.get("h2_count", 0),
        "canonical": parser_data.get("canonical", ""), "schema_found": parser_data.get("schema_found", False),
        "images": {"total": parser_data.get("images_total", 0), "with_alt": parser_data.get("images_with_alt", 0)},
        "links": {"internal": parser_data.get("internal_links", 0), "external": parser_data.get("external_links", 0)},
        "mobile_friendly": check_mobile_friendly(html),
        "page_speed": check_page_speed(url),
        "keyword_density": analyze_keyword_density(parser_data.get("visible_text", "")),
        "platform_status": platform_status  # For reference
    }
    
    # AI Insights Generate Karein
    ai = AIInsights()
    result["ai_recommendations"] = ai.generate_recommendations(result)
    
    # Auto-Fix Codes Generate Karein
    fix_gen = AutoFixGenerator()
    result["auto_fixes"] = fix_gen.generate_fixes(result)
    
    return result

# ==========================================
# 9. MAIN EXECUTION (Ultra Pro Max)
# ==========================================
if __name__ == "__main__":
    print("🚀 Mr Moosa AI — Ultra Pro Max SEO Agent")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("📖 Usage:")
        print("   Single URL: python seo_core.py https://example.com")
        print("   With PDF:   python seo_core.py https://example.com --pdf")
        print("   Bulk Mode:  python seo_core.py urls.txt")
        print("\n💡 Tip: Works best on WordPress, Shopify, static sites.")
        print("   JavaScript-heavy sites (Facebook, Etsy) may have limited data.\n")
        sys.exit(1)
    
    target = sys.argv[1]
    generate_pdf = "--pdf" in sys.argv
    
    if os.path.isfile(target):
        run_bulk_audit(target)
    else:
        url = target
        print(f"\n🔍 Auditing: {url}")
        print("   Using stealth mode + human-like behavior...\n")
        
        result = analyze_single_url(url)
        
        # Show results
        print("\n" + "="*50)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Generate PDF if requested
        if generate_pdf:
            print("\n📄 Generating professional PDF report...")
            generate_pdf_report(result, "seo_audit_report.pdf")
        
        print("\n✅ Audit complete!")