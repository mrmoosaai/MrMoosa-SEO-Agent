---
name: custom-seo
description: Natural language SEO audit assistant with PDF reports
---

# 🎯 NATURAL LANGUAGE COMMANDS

Main aapke natural language commands samajh sakta hoon!

## Kaise Use Karein:

### 1. **Simple Audit Command**
Aap bolain:
- "Mujay iski SEO kar or report bana kar do"
- "Is website ka audit karo"
- "Pinterest ki SEO check karo"
- "Audit https://example.com"
- "SEO report chahiye"
- "Iska SEO dekhna hai"

Main automatically:
✅ URL extract karunga
✅ SEO script run karunga
✅ PDF report banaunga
✅ Results dikhata hoon

### 2. **Keyword Research**
Aap bolain:
- "Etsy SEO ke liye keywords chahiye"
- "Pinterest marketing ke keywords dikhao"
- "Keyword research karo"

Main:
✅ DuckDuckGo se keywords nikalunga
✅ Top 10 suggestions dunga

### 3. **Speed Check**
Aap bolain:
- "Is site ki speed check karo"
- "Page speed dekhna hai"

Main:
✅ Page speed analyze karunga
✅ Recommendations dunga

---

# 🔧 AUTO-EXECUTION RULES

## Step 1: URL Detect Karein
Jab bhi user koi URL de (kisi bhi format mein):
- "https://..." se shuru hone wala koi bhi text
- "www." se shuru hone wala text
- Koi bhi domain name (pinterest.com, etsy.com, etc.)

## Step 2: Command Samjhein
Agar user ne yeh keywords use kiye:
- "SEO" / "audit" / "check" / "report" / "analyze" / "dekhna" / "karna" / "bana" / "do"

Toh automatically:
1. SEO audit run karein
2. PDF generate karein (agar user ne "--pdf" kaha ho ya "report bana" kaha ho)
3. Results dikhayein

## Step 3: Execute Karein
Command run karein:
```bash
python .agent/skills/custom-seo/scripts/seo_core.py <URL> --pdf
```

## 🧠 AI Commands:
- `@smart <URL>` → AI-powered priority fixes + platform tips
- Agent automatically uses the `ai_recommendations` section in the chat report
## 🔥 COMPETITOR ANALYSIS COMMANDS:

Jab user bole:
- "Mere competitors ko analyze karo"
- "Is site ko compare karo competitors se"
- "Competitor analysis karo"
- "Mere se behtar kaun hai?"

Toh automatically:
1. Run: python .agent/skills/custom-seo/scripts/competitor_analyzer.py <URL> 3
2. Comparison table dikhao
3. Gap analysis batao
4. Actionable recommendations do