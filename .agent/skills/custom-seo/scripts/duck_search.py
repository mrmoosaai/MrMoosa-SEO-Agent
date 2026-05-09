from ddgs import DDGS
import requests
import json
import sys

class DuckDuckGoSEO:
    def __init__(self):
        self.ddgs = DDGS()
    
    def keyword_research(self, keyword, max_results=10):
        """Related keywords search karein using autocomplete"""
        try:
            # DuckDuckGo autocomplete API directly
            url = f"https://duckduckgo.com/ac/?q={keyword}&type=list"
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            data = response.json()
            
            suggestions = data[1] if len(data) > 1 else []
            results = []
            
            for i, suggestion in enumerate(suggestions[:max_results]):
                results.append({
                    "keyword": suggestion,
                    "relevance": 100 - (i * 10),
                    "position": i + 1
                })
            
            return results if results else [{"keyword": keyword, "relevance": 100, "position": 1}]
        except Exception as e:
            return {"error": str(e)}
    
    def serp_analysis(self, query, max_results=10):
        """Top 10 results analyze karein"""
        try:
            results = list(self.ddgs.text(query, max_results=max_results))
            
            analyzed = []
            for result in results:
                seo_data = {
                    "title": result.get("title", ""),
                    "url": result.get("href", result.get("link", "")),
                    "description": result.get("body", result.get("snippet", "")),
                    "title_length": len(result.get("title", "")),
                    "desc_length": len(result.get("body", result.get("snippet", "")))
                }
                analyzed.append(seo_data)
            
            return {
                "query": query,
                "total_results": len(analyzed),
                "top_competitors": analyzed,
                "avg_title_length": sum(r["title_length"] for r in analyzed) / len(analyzed) if analyzed else 0,
                "avg_desc_length": sum(r["desc_length"] for r in analyzed) / len(analyzed) if analyzed else 0
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_search_volume(self, keyword):
        """Search volume estimate"""
        try:
            url = f"https://duckduckgo.com/ac/?q={keyword}&type=list"
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            data = response.json()
            suggestions = data[1] if len(data) > 1 else []
            
            return {
                "keyword": keyword,
                "suggestions": suggestions,
                "popularity_score": len(suggestions) * 10
            }
        except:
            return {"keyword": keyword, "suggestions": [], "popularity_score": 0}
    
    def competitor_backlinks(self, url):
        """Backlinks check karein"""
        try:
            response = requests.get(f"https://api.backlinkchecker.com/?url={url}")
            if response.status_code == 200:
                return response.json()
            else:
                return {"note": "Backlink API required"}
        except Exception as e:
            return {"note": f"Backlink check unavailable: {str(e)}"}

# === CLI Interface ===
if __name__ == "__main__":
    seo = DuckDuckGoSEO()
    
    if len(sys.argv) < 2:
        print("Usage: python duck_search.py <command> <query>")
        print("Commands: keywords, serp, volume")
        sys.exit(1)
    
    command = sys.argv[1]
    query = sys.argv[2] if len(sys.argv) > 2 else ""
    
    if command == "keywords":
        print(json.dumps(seo.keyword_research(query), indent=2))
    elif command == "serp":
        print(json.dumps(seo.serp_analysis(query), indent=2))
    elif command == "volume":
        print(json.dumps(seo.get_search_volume(query), indent=2))
    else:
        print("Unknown command. Use: keywords, serp, volume")