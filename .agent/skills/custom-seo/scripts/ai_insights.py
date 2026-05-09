import re

class AIInsights:
    def __init__(self):
        # 100% Rule-Based (No API, No Cost, 100% Free)
        self.platform_rules = {
            "pinterest": ["Optimize board titles with keywords", "Enable Rich Pins for better CTR", "Add alt text to every pin image"],
            "etsy": ["Use all 13 tags in listings", "Front-load keywords in titles", "Renew listings weekly for freshness"],
            "shopify": ["Compress product images automatically", "Use structured data for products", "Optimize collection page meta"],
            "wordpress": ["Install Yoast/RankMath for auto-meta", "Enable caching plugin", "Fix broken links regularly"]
        }

    def generate_recommendations(self, data):
        recs = []
        url = data.get("url", "").lower()
        meta = data.get("meta_desc", "")
        h1 = data.get("h1_count", 0)
        h2 = data.get("h2_count", 0)
        imgs = data.get("images", {})
        total_imgs = imgs.get("total", 0)
        alt_imgs = imgs.get("with_alt", 0)
        mobile_score = data.get("mobile_friendly", {}).get("score", 0)
        speed_score = data.get("page_speed", {}).get("performance_score", 0)
        schema = data.get("schema_found", False)
        canonical = data.get("canonical", "")

        # 1. Meta Description
        if not meta or len(meta) < 50:
            recs.append({
                "priority": "🔴 HIGH",
                "issue": "Meta Description Missing/Too Short",
                "fix": "Add <meta name='description' content='150 chars with primary keyword'>",
                "impact": "+25% CTR in search results"
            })

        # 2. Heading Structure
        if h1 == 0:
            recs.append({"priority": "🔴 HIGH", "issue": "Missing H1 Tag", "fix": "Add exactly one <h1> with main keyword", "impact": "Core SEO requirement"})
        elif h1 > 1:
            recs.append({"priority": "🟠 MEDIUM", "issue": "Multiple H1 Tags", "fix": "Keep only one <h1>, change others to <h2>", "impact": "Better content hierarchy"})
        if h2 == 0 and total_imgs > 5:
            recs.append({"priority": "🟠 MEDIUM", "issue": "No H2 Subheadings", "fix": "Break content into sections with <h2> tags", "impact": "Readability + Featured Snippets"})

        # 3. Images & Alt Text
        missing_alt = total_imgs - alt_imgs
        if missing_alt > 0:
            recs.append({
                "priority": "🟠 MEDIUM",
                "issue": f"Missing Alt Text ({missing_alt} images)",
                "fix": "Add descriptive alt='keyword + context' to all images",
                "impact": "Image SEO + Accessibility + Core Web Vitals"
            })

        # 4. Performance
        if speed_score < 70:
            recs.append({"priority": " HIGH", "issue": "Slow Page Speed", "fix": "Compress images, enable browser caching, minify CSS/JS", "impact": "Higher rankings + Lower bounce rate"})
        if mobile_score < 80:
            recs.append({"priority": "🔴 HIGH", "issue": "Mobile Usability Issues", "fix": "Fix viewport, increase tap target size, remove intrusive popups", "impact": "Mobile-first indexing pass"})

        # 5. Schema & Canonical
        if not schema:
            recs.append({"priority": " LOW", "issue": "No Schema Markup", "fix": "Add JSON-LD structured data (Article, Product, or FAQ)", "impact": "Rich snippets in Google"})
        if canonical and url.split('/')[2] not in canonical:
            recs.append({"priority": "🟠 MEDIUM", "issue": "Canonical Mismatch", "fix": "Update <link rel='canonical'> to match current URL", "impact": "Prevents duplicate content penalties"})

        # 6. Platform-Specific Tips
        for platform, tips in self.platform_rules.items():
            if platform in url:
                for tip in tips:
                    recs.append({"priority": "💡 PLATFORM TIP", "issue": f"{platform.title()} Optimization", "fix": tip, "impact": "Platform-specific ranking boost"})
                break

        # Overall Score Calculation
        overall = round((mobile_score + speed_score + (80 if h1==1 else 40) + (80 if meta else 40)) / 4)

        return {
            "overall_score": overall,
            "recommendations": recs,
            "ai_mode": "Rule-Based Engine (100% Free)"
        }