from ddgs import DDGS
import json
import sys
import os
import re
from urllib.parse import urlparse, parse_qs

sys.path.append(os.path.dirname(__file__))
from seo_core import analyze_single_url

class CompetitorAnalyzer:
    def __init__(self):
        self.ddgs = DDGS()
        
        # Platform-specific search templates (auto niche detection ke saath)
        self.platform_config = {
            'facebook.com': {
                'query_templates': [
                    'site:facebook.com "{niche}" page',
                    'site:facebook.com "{niche}" profile',
                    'site:facebook.com similar pages to "{name}"'
                ],
                'exclude_keywords': ['blog', 'article', 'post', 'news', 'how-to', 'guide', 'tips', 'alternatives', 'vs', 'review', 'list', 'top 10', 'best'],
                'url_pattern': r'facebook\.com/(?:profile\.php\?id=\d+|[^/]+/[^/]+/?$)'
            },
            'pinterest.com': {
                'query_templates': [
                    'site:pinterest.com "{niche}" creator',
                    'site:pinterest.com "{niche}" profile',
                    'site:pinterest.com pin "{name}"'
                ],
                'exclude_keywords': ['blog', 'article', 'ideas', 'inspiration', 'guide', 'tips', 'how to', 'tutorial'],
                'url_pattern': r'pinterest\.com/[^/]+/?$'
            },
            'etsy.com': {
                'query_templates': [
                    'site:etsy.com/shop "{niche}"',
                    'site:etsy.com "{niche}" handmade',
                    'site:etsy.com shop similar to "{name}"'
                ],
                'exclude_keywords': ['blog', 'article', 'guide', 'tips', 'how to', 'review', 'alternatives'],
                'url_pattern': r'etsy\.com/(?:shop/)?[^/]+/?$'
            },
            'instagram.com': {
                'query_templates': [
                    'site:instagram.com "{niche}" profile',
                    'site:instagram.com "{niche}" creator',
                    'site:instagram.com "{name}"'
                ],
                'exclude_keywords': ['blog', 'article', 'news', 'guide', 'tips', 'how to', 'review'],
                'url_pattern': r'instagram\.com/[^/]+/?$'
            },
            'youtube.com': {
                'query_templates': [
                    'site:youtube.com/c "{niche}"',
                    'site:youtube.com/channel "{niche}"',
                    'site:youtube.com "@{name}"'
                ],
                'exclude_keywords': ['blog', 'article', 'news', 'review', 'vs', 'alternatives', 'top 10'],
                'url_pattern': r'youtube\.com/(?:c/|channel/|@)?[^/]+/?$'
            },
            'default': {
                'query_templates': [
                    'site:{domain} "{niche}"',
                    'similar websites to {domain}',
                    '{niche} {domain_type}'
                ],
                'exclude_keywords': ['blog', 'article', 'news', 'review', 'vs', 'alternatives', 'comparison'],
                'url_pattern': None
            }
        }
    
    def extract_smart_niche(self, url, html_content=None):
        """
        URL + optional HTML content se smart niche extract karega
        Returns: niche_keywords (string)
        """
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        path_parts = [p for p in parsed.path.split('/') if p and p not in ['profile.php', 'shop', 'blog', 'page', 'home', 'about', 'contact', 'posts']]
        
        # 1. Pehle URL path se keywords nikalo
        if path_parts:
            # Remove numbers and special chars, keep meaningful words
            clean_parts = [re.sub(r'[^a-zA-Z\s-]', '', p).strip() for p in path_parts]
            clean_parts = [p for p in clean_parts if p and len(p) > 2]
            if clean_parts:
                return ' '.join(clean_parts[:3]).lower()
        
        # 2. Agar HTML content mila hai, toh title/meta se niche nikalo
        if html_content:
            # Title se keywords
            title_match = re.search(r'<title>([^<]+)</title>', html_content, re.I)
            if title_match:
                title = title_match.group(1)
                # Remove brand names, keep descriptive words
                words = re.findall(r'\b[a-zA-Z]{4,}\b', title)
                stop_words = {'the', 'and', 'for', 'with', 'from', 'home', 'page', 'profile', 'official', 'welcome'}
                meaningful = [w.lower() for w in words if w.lower() not in stop_words]
                if meaningful:
                    return ' '.join(meaningful[:4]).lower()
            
            # Meta description se
            meta_match = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', html_content, re.I)
            if meta_match:
                desc = meta_match.group(1)
                words = re.findall(r'\b[a-zA-Z]{5,}\b', desc)
                meaningful = [w.lower() for w in words if len(w) > 5]
                if meaningful:
                    return ' '.join(meaningful[:4]).lower()
        
        # 3. Fallback: Domain se clean keyword
        clean_domain = re.sub(r'[^a-zA-Z\s-]', ' ', domain.split('.')[0])
        return clean_domain.strip().lower() or "website"
    
    def detect_platform(self, url):
        """URL se platform detect karega"""
        domain = urlparse(url).netloc.replace('www.', '')
        for platform in self.platform_config:
            if platform in domain:
                return platform
        return 'default'
    
    def extract_name_from_url(self, url, platform):
        """URL se profile/shop name extract karega"""
        parsed = urlparse(url)
        
        if platform == 'facebook.com':
            if 'profile.php' in url:
                return parse_qs(parsed.query).get('id', ['profile'])[0]
            parts = [p for p in parsed.path.split('/') if p]
            return parts[-1] if parts else "profile"
        
        elif platform == 'pinterest.com':
            parts = [p for p in parsed.path.split('/') if p]
            return parts[0] if parts else "profile"
        
        elif platform == 'etsy.com':
            if '/shop/' in url:
                return url.split('/shop/')[-1].split('/')[0]
            return "shop"
        
        elif platform == 'instagram.com':
            parts = [p for p in parsed.path.split('/') if p]
            return parts[0] if parts else "profile"
        
        elif platform == 'youtube.com':
            if '/c/' in url:
                return url.split('/c/')[-1].split('/')[0]
            elif '/channel/' in url:
                return url.split('/channel/')[-1].split('/')[0]
            elif '/@' in url:
                return url.split('/@')[-1].split('/')[0]
            return "channel"
        
        # Default: domain name
        return urlparse(url).netloc.replace('www.', '').split('.')[0]
    
    def find_competitors(self, url, html_content=None, max_results=3):
        """Smart competitor search — auto niche detection + platform logic"""
        try:
            # Platform detect karo
            platform = self.detect_platform(url)
            config = self.platform_config[platform]
            
            # Niche aur name extract karo
            niche = self.extract_smart_niche(url, html_content)
            name = self.extract_name_from_url(url, platform)
            domain = urlparse(url).netloc.replace('www.', '')
            
            print(f"🔍 Platform detected: {platform}")
            print(f"🎯 Extracted niche: '{niche}'")
            print(f"📛 Extracted name: '{name}'")
            
            # Search queries generate karo
            queries = config['query_templates']
            search_query = queries[0].format(
                niche=niche,
                name=name,
                domain=domain,
                domain_type='website' if platform == 'default' else platform.split('.')[0]
            )
            
            print(f"🔎 Search query: '{search_query}'")
            
            # DuckDuckGo search
            results = list(self.ddgs.text(search_query, max_results=max_results + 5))
            
            competitors = []
            seen_urls = set()
            exclude_keywords = config['exclude_keywords']
            url_pattern = config.get('url_pattern')
            
            for result in results:
                comp_url = result.get('href', '')
                title = result.get('title', '').lower()
                
                # Basic filters
                if not comp_url or comp_url in seen_urls or url in comp_url:
                    continue
                
                # Exclude blog posts, articles, etc.
                if any(kw in title or kw in comp_url.lower() for kw in exclude_keywords):
                    continue
                
                # Platform-specific URL pattern match (agar defined hai)
                if url_pattern and platform != 'default':
                    if not re.search(url_pattern, comp_url):
                        continue
                
                # Only keep same-platform competitors for social sites
                if platform != 'default' and platform not in comp_url:
                    continue
                
                # Basic validation
                if any(ext in comp_url for ext in ['.pdf', '.jpg', '.png', '.zip', '.exe']):
                    continue
                
                competitors.append({
                    'url': comp_url,
                    'title': result.get('title', ''),
                    'description': result.get('body', '')[:150] + "..." if result.get('body') else ''
                })
                seen_urls.add(comp_url)
                
                if len(competitors) >= max_results:
                    break
            
            return competitors[:max_results]
            
        except Exception as e:
            print(f"⚠️  Error finding competitors: {e}")
            return []
    
    def compare_websites(self, target_url, competitor_urls, html_content=None):
        """Target aur competitors ka detailed comparison"""
        print("\n⚡ Running SEO Analysis...\n")
        
        # Target analysis
        print(f"📊 Analyzing: {target_url}")
        target_data = analyze_single_url(target_url)
        target_score = self._calculate_composite_score(target_data)
        
        # Competitors analysis
        competitors_data = []
        for i, comp_url in enumerate(competitor_urls, 1):
            print(f"\n📊 Analyzing Competitor {i}: {comp_url}")
            try:
                comp_data = analyze_single_url(comp_url)
                comp_score = self._calculate_composite_score(comp_data)
                competitors_data.append({
                    'url': comp_url,
                    'score': comp_score,
                    'data': comp_data,
                    'title': comp_data.get('title', '')[:60] if comp_data else 'N/A'
                })
            except Exception as e:
                print(f"  ⚠️  Skipped (blocked or error): {e}")
                competitors_data.append({
                    'url': comp_url,
                    'score': 0,
                    'data': None,
                    'title': 'N/A',
                    'error': str(e)
                })
        
        # Comparison generate karo
        return self._generate_comparison(target_url, target_data, target_score, competitors_data)
    
    def _calculate_composite_score(self, data):
        """Overall score calculate karo (0-100)"""
        if not data:
            return 0
        mobile = data.get('mobile_friendly', {}).get('score', 0)
        speed = data.get('page_speed', {}).get('performance_score', 0)
        tech_score = 0
        if data.get('title'): tech_score += 20
        if data.get('meta_desc'): tech_score += 20
        if data.get('h1_count', 0) == 1: tech_score += 20
        if data.get('schema_found'): tech_score += 20
        if data.get('images', {}).get('with_alt', 0) > 0: tech_score += 20
        return round((mobile + speed + tech_score) / 3)
    
    def _generate_comparison(self, target_url, target_data, target_score, competitors_data):
        """Professional comparison report generate karo"""
        comparison = {
            'target': {
                'url': target_url,
                'score': target_score,
                'mobile': target_data.get('mobile_friendly', {}).get('score', 0),
                'speed': target_data.get('page_speed', {}).get('performance_score', 0),
                'has_meta': bool(target_data.get('meta_desc')),
                'has_schema': target_data.get('schema_found', False),
                'h1_count': target_data.get('h1_count', 0),
                'h2_count': target_data.get('h2_count', 0),
                'title': target_data.get('title', '')[:50]
            },
            'competitors': [],
            'gap_analysis': {
                'strengths': [],
                'weaknesses': [],
                'opportunities': []
            }
        }
        
        # Competitors data add karo
        for comp in competitors_data:
            comparison['competitors'].append({
                'url': comp['url'],
                'score': comp['score'],
                'mobile': comp['data'].get('mobile_friendly', {}).get('score', 0) if comp['data'] else 0,
                'speed': comp['data'].get('page_speed', {}).get('performance_score', 0) if comp['data'] else 0,
                'has_meta': bool(comp['data'].get('meta_desc')) if comp['data'] else False,
                'has_schema': comp['data'].get('schema_found', False) if comp['data'] else False,
                'title': comp.get('title', 'N/A')
            })
        
        # Gap Analysis
        valid_competitors = [c for c in competitors_data if c['score'] > 0]
        avg_comp_score = sum(c['score'] for c in valid_competitors) / len(valid_competitors) if valid_competitors else 0
        
        # Strengths
        if target_score > avg_comp_score and valid_competitors:
            comparison['gap_analysis']['strengths'].append(f"Overall score ({target_score}) is ABOVE average competitor ({round(avg_comp_score)})")
        if target_data.get('mobile_friendly', {}).get('score', 0) == 100:
            comparison['gap_analysis']['strengths'].append("Perfect mobile optimization (100/100)")
        if target_data.get('page_speed', {}).get('performance_score', 0) >= 90:
            comparison['gap_analysis']['strengths'].append("Excellent page speed performance")
        if target_data.get('canonical'):
            comparison['gap_analysis']['strengths'].append("Canonical URL properly set")
        
        # Weaknesses
        if not target_data.get('meta_desc'):
            comparison['gap_analysis']['weaknesses'].append("Missing meta description (reduces CTR)")
        if not target_data.get('schema_found'):
            comparison['gap_analysis']['weaknesses'].append("No schema markup (missing rich snippets)")
        if target_data.get('h1_count', 0) == 0:
            comparison['gap_analysis']['weaknesses'].append("Missing H1 heading (core SEO issue)")
        elif target_data.get('h1_count', 0) > 1:
            comparison['gap_analysis']['weaknesses'].append("Multiple H1 tags (confuses search engines)")
        if target_data.get('h2_count', 0) == 0 and target_data.get('images', {}).get('total', 0) > 0:
            comparison['gap_analysis']['weaknesses'].append("No H2 subheadings (poor content structure)")
        
        # Opportunities
        comp_with_schema = sum(1 for c in valid_competitors if c['data'] and c['data'].get('schema_found'))
        if comp_with_schema > 0 and not target_data.get('schema_found'):
            comparison['gap_analysis']['opportunities'].append(f"{comp_with_schema}/{len(valid_competitors)} competitors use schema markup — add it to stand out!")
        
        comp_with_meta = sum(1 for c in valid_competitors if c['data'] and c['data'].get('meta_desc'))
        if comp_with_meta > 0 and not target_data.get('meta_desc'):
            comparison['gap_analysis']['opportunities'].append(f"Add meta description to match {comp_with_meta}/{len(valid_competitors)} competitors")
        
        avg_h2 = sum(c['data'].get('h2_count', 0) for c in valid_competitors if c['data']) / len(valid_competitors) if valid_competitors else 0
        if avg_h2 > 2 and target_data.get('h2_count', 0) < 2:
            comparison['gap_analysis']['opportunities'].append(f"Add more H2 subheadings (competitors average: {round(avg_h2)})")
        
        return comparison
    
    def print_comparison(self, comparison):
        """Formatted comparison print karo"""
        print("\n" + "="*80)
        print("🏆 COMPETITIVE ANALYSIS REPORT")
        print("="*80)
        
        target = comparison['target']
        print(f"\n📍 YOUR SITE: {target['url'][:60]}{'...' if len(target['url'])>60 else ''}")
        print(f"   Title: {target['title']}")
        print(f"   Overall Score: {target['score']}/100")
        print(f"   📱 Mobile: {target['mobile']}/100 | ⚡ Speed: {target['speed']}/100")
        print(f"   📝 Meta: {'✅' if target['has_meta'] else '❌'} | 🔖 Schema: {'✅' if target['has_schema'] else '❌'} | H1: {target['h1_count']}")
        
        print(f"\n📊 COMPETITORS:")
        for i, comp in enumerate(comparison['competitors'], 1):
            status = "⚠️ Blocked" if comp['score'] == 0 and comp.get('error') else ""
            print(f"\n   {i}. {comp['url'][:55]}{'...' if len(comp['url'])>55 else ''} {status}")
            if comp['score'] > 0:
                print(f"      Title: {comp['title']}")
                print(f"      Score: {comp['score']}/100 | Mobile: {comp['mobile']} | Speed: {comp['speed']}")
                print(f"      Meta: {'✅' if comp['has_meta'] else '❌'} | Schema: {'✅' if comp['has_schema'] else '❌'}")
            else:
                print(f"      ⚠️  Could not analyze (site may block automated requests)")
        
        print(f"\n{'='*80}")
        print("📈 GAP ANALYSIS")
        print("="*80)
        
        if comparison['gap_analysis']['strengths']:
            print(f"\n✅ YOUR STRENGTHS:")
            for strength in comparison['gap_analysis']['strengths']:
                print(f"   • {strength}")
        
        if comparison['gap_analysis']['weaknesses']:
            print(f"\n⚠️  YOUR WEAKNESSES:")
            for weakness in comparison['gap_analysis']['weaknesses']:
                print(f"   • {weakness}")
        
        if comparison['gap_analysis']['opportunities']:
            print(f"\n🎯 OPPORTUNITIES:")
            for opp in comparison['gap_analysis']['opportunities']:
                print(f"   • {opp}")
        
        print("\n" + "="*80)
        return json.dumps(comparison, indent=2, ensure_ascii=False)

# CLI Interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python competitor_analyzer.py <URL> [max_competitors]")
        print("Example: python competitor_analyzer.py https://example.com 3")
        sys.exit(1)
    
    url = sys.argv[1]
    max_competitors = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    
    analyzer = CompetitorAnalyzer()
    
    # Fetch HTML content for better niche detection (optional)
    html_content = None
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            html_content = resp.read().decode('utf-8', errors='ignore')
    except:
        pass  # Agar fetch na ho sake, toh bhi chalega
    
    competitors = analyzer.find_competitors(url, html_content=html_content, max_results=max_competitors)
    
    if not competitors:
        print("❌ No relevant competitors found!")
        print("💡 Tip: Try with a different URL or check if the site blocks automated requests.")
        sys.exit(1)
    
    print(f"\n✅ Found {len(competitors)} relevant competitors:")
    for i, comp in enumerate(competitors, 1):
        print(f"   {i}. {comp['url']}")
    
    comparison = analyzer.compare_websites(url, [c['url'] for c in competitors], html_content=html_content)
    analyzer.print_comparison(comparison)