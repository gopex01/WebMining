import json
import re
from bs4 import BeautifulSoup
import requests

STOP_WORDS = {
    'the', 'and', 'of', 'a', 'to', 'in', 'is', 'you', 'that', 'it', 'he', 
    'was', 'for', 'on', 'are', 'as', 'with', 'his', 'they', 'i', 'at', 'by', 
    'or', 'an', 'this', 'from', 'but', 'not', 'your', 'all', 'web',
    'na', 'u', 'i', 'za', 'se', 'je', 'da', 'sa', 'ne', 'bi', 'koji', 'koja', 'su'
}

def start_analyze(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'sr,en-US;q=0.7,en;q=0.3',
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
    except Exception as e:
        return {"status": "Error", "message": f"Connection failed: {str(e)}"}

    if response.status_code != 200:
        return {"status": "Error", "message": f"Website returned status code: {response.status_code}"}

    raw_html = response.text
    soup = BeautifulSoup(raw_html, "html.parser")

    # 1. DETEKCIJA JS / CSR BARIJERE
    is_spa_detected = False
    spa_framework = "None"
    if any(tag in raw_html for tag in ["ng-version", "<app-root>", "data-critters-container", "<ds-root>"]):
        is_spa_detected = True
        spa_framework = "Angular"
    elif "reactid" in raw_html or '<div id="root">' in raw_html:
        is_spa_detected = True
        spa_framework = "React"
    elif 'id="app"' in raw_html and "vue" in raw_html:
        is_spa_detected = True
        spa_framework = "Vue.js"

    # 2. TEKST IZ BODY DELA
    soup_copy = BeautifulSoup(raw_html, "html.parser")
    for noti_tag in soup_copy(["script", "style", "noscript", "svg"]):
        noti_tag.decompose()

    body_element = soup_copy.find("body")
    full_text = body_element.get_text(separator=" ") if body_element else ""
    plain_text = " ".join(full_text.split())

    # 3. ADVANCED SEO ANALYSIS
    title_tag = soup.find("title")
    title_text = title_tag.text.strip() if title_tag else ""
    title_length = len(title_text)

    # H1
    h1_tags = [h1.get_text().strip() for h1 in soup.find_all("h1") if h1.get_text().strip()]
    
    # Meta Description & Robots
    meta_desc = soup.find("meta", attrs={"name": "description"})
    meta_desc_text = meta_desc.get("content", "").strip() if meta_desc else ""
    
    meta_robots = soup.find("meta", attrs={"name": "robots"})
    meta_robots_text = meta_robots.get("content", "").strip() if meta_robots else "Index, Follow (Default)"

    # Canonical Link
    canonical_tag = soup.find("link", attrs={"rel": "canonical"})
    has_canonical = bool(canonical_tag)

    # Slike
    images = soup.find_all("img")
    total_images = len(images)
    images_without_alt = sum(1 for s in images if not s.get("alt") or s.get("alt").strip() == "")
    alt_score_percentage = 100 if total_images == 0 else int(((total_images - images_without_alt) / total_images) * 100)

    # Frame & iFrame
    frame = bool(soup.find("frame"))
    iframe = bool(soup.find("iframe"))

    # Tokenizacija
    all_words = re.findall(r'\b[a-zA-ZšđčćžŠĐČĆŽ]{3,}\b', plain_text.lower())
    important_words = [word for word in all_words if word not in STOP_WORDS]
    frequency = {}
    for word in important_words:
        frequency[word] = frequency.get(word, 0) + 1
    top_key_words = sorted(frequency.items(), key=lambda x: x[1], reverse=True)[:5]
    words_num = len(all_words)

    # --- LIGHTHOUSE-STYLE SCORE CALCULATION (0 - 100) ---
    score = 100
    penalties = []

    if not title_text:
        score -= 20
        penalties.append("Missing Title Tag (-20)")
    elif not (30 <= title_length <= 60):
        score -= 5
        penalties.append("Non-optimal Title Length (-5)")

    if len(h1_tags) == 0:
        score -= 15
        penalties.append("Missing H1 Heading (-15)")
    elif len(h1_tags) > 1:
        score -= 5
        penalties.append("Multiple H1 Headings Found (-5)")

    if not meta_desc_text:
        score -= 10
        penalties.append("Missing Meta Description (-10)")

    if is_spa_detected:
        score -= 25
        penalties.append(f"Client-Side Rendering Barrier ({spa_framework}) (-25)")

    if images_without_alt > 0:
        score -= 10
        penalties.append("Images Missing ALT Attributes (-10)")

    if words_num < 100:
        score -= 15
        penalties.append("Low Content Volume (<100 words) (-15)")

    score = max(0, score)

    return {
        "status": "Success",
        "url_skeniranja": url,
        "lighthouse_score": score,
        "penalties": penalties,
        "tehnicki_tagovi": {
            "title_tag": {"sadrzaj": title_text, "duzina": title_length},
            "meta_description": {"sadrzaj": meta_desc_text, "exists": bool(meta_desc_text)},
            "meta_robots": meta_robots_text,
            "has_canonical": has_canonical,
            "h1_headings": {"ukupno_h1": len(h1_tags), "sadrzaj": h1_tags},
            "slike_statistika": {
                "ukupno_slika": total_images,
                "slike_bez_alt_opisa": images_without_alt,
                "optimizovanost_procenat": f"{alt_score_percentage}%"
            },
            "tehnicke_barijere": {
                "koristi_frame": frame,
                "koristi_iframe": iframe,
                "javascript_client_side_rendering": is_spa_detected,
                "detected_framework": spa_framework
            }
        },
        "analiza_teksta": {
            "ukupan_broj_reci": words_num,
            "ispunjava_minimum_100_reci": words_num >= 100,
            "detektovane_kljucne_reci": [{"rec": r[0], "frekvencija": r[1]} for r in top_key_words]
        }
    }