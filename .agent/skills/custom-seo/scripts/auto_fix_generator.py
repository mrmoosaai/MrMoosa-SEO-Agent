from urllib.parse import urlparse

class AutoFixGenerator:
    def __init__(self):
        self.fixes = []

    def generate_fixes(self, data):
        """Auto-fix code generate karega based on audit data"""
        self.fixes = []
        url = data.get('url', '')
        title = data.get('title', 'Your Page Title')
        meta_desc = data.get('meta_desc', '')
        h1_count = data.get('h1_count', 0)
        h2_count = data.get('h2_count', 0)
        images = data.get('images', {})
        total_imgs = images.get('total', 0)
        alt_imgs = images.get('with_alt', 0)
        schema = data.get('schema_found', False)
        canonical = data.get('canonical', '')
        
        # Domain extract karo
        domain = urlparse(url).netloc.replace('www.', '') if '//' in url else 'your-domain.com'

        # 1. Meta Description Fix
        if not meta_desc or len(meta_desc) < 50:
            generated_meta = f"{title} - Official page of {domain}. Discover top features, tools, and resources updated for 2026."
            self.fixes.append({
                "issue": "Missing/Short Meta Description",
                "code": f'<meta name="description" content="{generated_meta[:155]}">',
                "location": "<head> section",
                "instructions": "Replace or add this line inside your HTML <head> tag."
            })

        # 2. H1 Fix
        if h1_count == 0:
            self.fixes.append({
                "issue": "Missing H1 Tag",
                "code": f'<h1>{title}</h1>',
                "location": "Main content area",
                "instructions": "Add this as the main heading of your page."
            })
        elif h1_count > 1:
            self.fixes.append({
                "issue": "Multiple H1 Tags Detected",
                "code": "<!-- Change extra <h1> tags to <h2> or <h3> -->",
                "location": "HTML content",
                "instructions": "Keep only one <h1>. Change others to <h2> or <h3>."
            })

        # 3. H2 Structure Fix
        if h2_count == 0 and total_imgs > 3:
            self.fixes.append({
                "issue": "No H2 Subheadings",
                "code": """<h2>Key Features</h2>
<h2>How It Works</h2>
<h2>Frequently Asked Questions</h2>""",
                "location": "Content sections",
                "instructions": "Break your content into logical sections using these H2 tags."
            })

        # 4. Image Alt Text Fix
        missing_alt = total_imgs - alt_imgs
        if missing_alt > 0:
            self.fixes.append({
                "issue": f"Missing Alt Text ({missing_alt} images)",
                "code": '<img src="image.jpg" alt="Descriptive text about the image including keywords">',
                "location": "Image tags",
                "instructions": "Add descriptive alt text to all images for SEO and accessibility."
            })

        # 5. Schema Markup Fix
        if not schema:
            schema_code = f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "name": "{title}",
  "url": "{url}",
  "description": "{meta_desc if meta_desc else 'Official page of ' + domain}",
  "publisher": {{
    "@type": "Organization",
    "name": "{domain}"
  }}
}}
</script>"""
            self.fixes.append({
                "issue": "Missing Schema Markup",
                "code": schema_code,
                "location": "<head> or before </body>",
                "instructions": "Paste this JSON-LD script to enable rich snippets in search results."
            })

        # 6. Canonical Fix
        if canonical and url.split('/')[2] not in canonical:
            self.fixes.append({
                "issue": "Canonical URL Mismatch",
                "code": f'<link rel="canonical" href="{url}" />',
                "location": "<head> section",
                "instructions": "Replace the existing canonical tag with this to avoid duplicate content issues."
            })

        return self.fixes