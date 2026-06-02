"""
JobHunter - Bonn Area Job Aggregator with CV Matching
Searches Adzuna + generates LinkedIn deep-links, scores against your CV using Claude AI
"""

import os
import json
import time
import threading
import requests
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import anthropic
import PyPDF2
import docx2txt

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "jobhunter-secret-change-me")
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

# ── Job search configuration ──────────────────────────────────────────────────
SEARCH_PROFILES = [
    {
        "id": "data_science",
        "label": "Data Scientist",
        "keywords": ["data scientist", "machine learning", "data science"],
        "adzuna_category": "it-jobs",
    },
    {
        "id": "science_policy",
        "label": "Science Policy",
        "keywords": ["science policy", "research policy", "policy analyst science", "science advisor"],
        "adzuna_category": "scientific-qa-jobs",
    },
    {
        "id": "funding_reviewer",
        "label": "Science Funding / Grant Reviewer",
        "keywords": ["grant reviewer", "research funding", "science reviewer", "funding agency"],
        "adzuna_category": "scientific-qa-jobs",
    },
    {
        "id": "quant_researcher",
        "label": "Quantitative Researcher / Analyst",
        "keywords": ["quantitative researcher", "quantitative analyst", "data analyst", "statistician"],
        "adzuna_category": "it-jobs",
    },
    {
        "id": "physics_teacher",
        "label": "Physics Teacher (International School)",
        "keywords": ["physics teacher", "science teacher international", "IB physics teacher", "IGCSE physics"],
        "adzuna_category": "teaching-jobs",
    },
]

# ── City catalogue ────────────────────────────────────────────────────────────
# Each entry: id, label, adzuna_country (ISO), search_locations (fed to Adzuna),
#             linkedin_geo_id, german_filter (whether to strip German-req jobs)
CITIES = [
    # ── Germany ──
    {
        "id": "bonn", "label": "Bonn, Germany", "flag": "🇩🇪",
        "adzuna_country": "de",
        "search_locations": ["Bonn", "Cologne", "Koblenz"],
        "linkedin_geo_id": "104738515",
        "german_filter": True,
    },
    {
        "id": "berlin", "label": "Berlin, Germany", "flag": "🇩🇪",
        "adzuna_country": "de",
        "search_locations": ["Berlin"],
        "linkedin_geo_id": "103035651",
        "german_filter": True,
    },
    {
        "id": "munich", "label": "Munich, Germany", "flag": "🇩🇪",
        "adzuna_country": "de",
        "search_locations": ["Munich", "München"],
        "linkedin_geo_id": "106514261",
        "german_filter": True,
    },
    {
        "id": "hamburg", "label": "Hamburg, Germany", "flag": "🇩🇪",
        "adzuna_country": "de",
        "search_locations": ["Hamburg"],
        "linkedin_geo_id": "104399846",
        "german_filter": True,
    },
    {
        "id": "frankfurt", "label": "Frankfurt, Germany", "flag": "🇩🇪",
        "adzuna_country": "de",
        "search_locations": ["Frankfurt"],
        "linkedin_geo_id": "106399077",
        "german_filter": True,
    },
    {
        "id": "cologne", "label": "Cologne, Germany", "flag": "🇩🇪",
        "adzuna_country": "de",
        "search_locations": ["Cologne", "Köln"],
        "linkedin_geo_id": "104404008",
        "german_filter": True,
    },
    {
        "id": "dusseldorf", "label": "Düsseldorf, Germany", "flag": "🇩🇪",
        "adzuna_country": "de",
        "search_locations": ["Düsseldorf"],
        "linkedin_geo_id": "104561617",
        "german_filter": True,
    },
    {
        "id": "stuttgart", "label": "Stuttgart, Germany", "flag": "🇩🇪",
        "adzuna_country": "de",
        "search_locations": ["Stuttgart"],
        "linkedin_geo_id": "106320564",
        "german_filter": True,
    },
    {
        "id": "leipzig", "label": "Leipzig, Germany", "flag": "🇩🇪",
        "adzuna_country": "de",
        "search_locations": ["Leipzig"],
        "linkedin_geo_id": "104494399",
        "german_filter": True,
    },
    {
        "id": "heidelberg", "label": "Heidelberg, Germany", "flag": "🇩🇪",
        "adzuna_country": "de",
        "search_locations": ["Heidelberg", "Mannheim"],
        "linkedin_geo_id": "106969716",
        "german_filter": True,
    },
    # ── USA ──
    {
        "id": "new_york", "label": "New York, USA", "flag": "🇺🇸",
        "adzuna_country": "us",
        "search_locations": ["New York"],
        "linkedin_geo_id": "105080838",
        "german_filter": False,
    },
    {
        "id": "washington_dc", "label": "Washington DC, USA", "flag": "🇺🇸",
        "adzuna_country": "us",
        "search_locations": ["Washington DC"],
        "linkedin_geo_id": "103977389",
        "german_filter": False,
    },
    {
        "id": "san_francisco", "label": "San Francisco, USA", "flag": "🇺🇸",
        "adzuna_country": "us",
        "search_locations": ["San Francisco"],
        "linkedin_geo_id": "102277331",
        "german_filter": False,
    },
    {
        "id": "boston", "label": "Boston, USA", "flag": "🇺🇸",
        "adzuna_country": "us",
        "search_locations": ["Boston"],
        "linkedin_geo_id": "101567633",
        "german_filter": False,
    },
    {
        "id": "chicago", "label": "Chicago, USA", "flag": "🇺🇸",
        "adzuna_country": "us",
        "search_locations": ["Chicago"],
        "linkedin_geo_id": "103112676",
        "german_filter": False,
    },
    {
        "id": "los_angeles", "label": "Los Angeles, USA", "flag": "🇺🇸",
        "adzuna_country": "us",
        "search_locations": ["Los Angeles"],
        "linkedin_geo_id": "102448103",
        "german_filter": False,
    },
    {
        "id": "seattle", "label": "Seattle, USA", "flag": "🇺🇸",
        "adzuna_country": "us",
        "search_locations": ["Seattle"],
        "linkedin_geo_id": "103644278",
        "german_filter": False,
    },
    {
        "id": "austin", "label": "Austin, USA", "flag": "🇺🇸",
        "adzuna_country": "us",
        "search_locations": ["Austin"],
        "linkedin_geo_id": "104969812",
        "german_filter": False,
    },
    {
        "id": "new_haven", "label": "New Haven, USA", "flag": "🇺🇸",
        "adzuna_country": "us",
        "search_locations": ["New Haven"],
        "linkedin_geo_id": "104970567",
        "german_filter": False,
    },
    {
        "id": "princeton", "label": "Princeton / NYC Metro, USA", "flag": "🇺🇸",
        "adzuna_country": "us",
        "search_locations": ["Princeton", "New Jersey"],
        "linkedin_geo_id": "105080838",
        "german_filter": False,
    },
]

# Build a lookup dict for quick access
CITY_MAP = {c["id"]: c for c in CITIES}

LINKEDIN_FILTERS = {
    "data_science": "f_TP=1,2&f_E=3,4&keywords=data+scientist+OR+%22machine+learning%22",
    "science_policy": "keywords=%22science+policy%22+OR+%22research+policy%22",
    "funding_reviewer": "keywords=%22grant+reviewer%22+OR+%22research+funding%22+OR+%22science+reviewer%22",
    "quant_researcher": "keywords=%22quantitative+researcher%22+OR+%22data+analyst%22",
    "physics_teacher": "keywords=%22physics+teacher%22+OR+%22IB+physics%22",
}

# ── Utilities ──────────────────────────────────────────────────────────────────

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_cv_text(filepath: str) -> str:
    ext = filepath.rsplit(".", 1)[1].lower()
    if ext == "pdf":
        text = []
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text.append(page.extract_text() or "")
        return "\n".join(text)
    elif ext == "docx":
        return docx2txt.process(filepath)
    else:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()


def fetch_adzuna_jobs(profile: dict, app_id: str, app_key: str, city: dict) -> list:
    """Fetch jobs from Adzuna API for the selected city."""
    jobs = []
    country = city["adzuna_country"]
    for keyword in profile["keywords"][:2]:  # limit to avoid rate limits
        for location in city["search_locations"][:2]:
            try:
                url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
                params = {
                    "app_id": app_id,
                    "app_key": app_key,
                    "results_per_page": 10,
                    "what": keyword,
                    "where": location,
                    "distance": 30,
                    "content-type": "application/json",
                    "sort_by": "date",
                }
                resp = requests.get(url, params=params, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    for job in data.get("results", []):
                        desc = (job.get("description") or "").lower()
                        # Filter German-fluency requirements only for German cities
                        if city["german_filter"] and any(phrase in desc for phrase in [
                            "fließende deutschkenntnisse", "deutsch als muttersprache",
                            "c1 deutsch", "c2 deutsch", "verhandlungssicheres deutsch",
                            "muttersprachliche deutschkenntnisse"
                        ]):
                            continue

                        jobs.append({
                            "id": job.get("id", ""),
                            "title": job.get("title", "Unknown"),
                            "company": job.get("company", {}).get("display_name", "Unknown"),
                            "location": job.get("location", {}).get("display_name", location),
                            "url": job.get("redirect_url", "#"),
                            "description": (job.get("description") or "")[:800],
                            "salary_min": job.get("salary_min"),
                            "salary_max": job.get("salary_max"),
                            "created": job.get("created", ""),
                            "source": "Adzuna",
                            "profile_id": profile["id"],
                            "profile_label": profile["label"],
                            "city": city["label"],
                            "applicants": None,
                            "relevance_score": None,
                            "relevance_reason": None,
                        })
                time.sleep(0.3)  # be polite
            except Exception as e:
                print(f"Adzuna error for {keyword}/{location}: {e}")

    # Deduplicate by URL
    seen = set()
    unique = []
    for j in jobs:
        if j["url"] not in seen:
            seen.add(j["url"])
            unique.append(j)
    return unique


def build_linkedin_links(profile: dict, city: dict) -> list:
    """Generate pre-filtered LinkedIn job search URLs for the selected city."""
    base = "https://www.linkedin.com/jobs/search/?"
    filters = LINKEDIN_FILTERS.get(profile["id"], f"keywords={profile['keywords'][0].replace(' ', '+')}")
    geo = f"geoId={city['linkedin_geo_id']}"
    url = f"{base}{filters}&{geo}&distance=30&f_WT=1,2,3"
    return [{
        "id": f"li_{profile['id']}_{city['id']}",
        "title": f"LinkedIn: {profile['label']}",
        "company": "LinkedIn (open in browser)",
        "location": city["label"],
        "url": url,
        "description": f"Pre-filtered LinkedIn search for {profile['label']} jobs near {city['label']}. Click to open and see live applicant counts.",
        "source": "LinkedIn",
        "profile_id": profile["id"],
        "profile_label": profile["label"],
        "city": city["label"],
        "applicants": None,
        "relevance_score": None,
        "relevance_reason": "LinkedIn deep link — open to see live applicant counts",
    }]


def score_jobs_with_claude(jobs: list, cv_text: str, api_key: str) -> list:
    """Use Claude to score each job's relevance against the CV."""
    if not cv_text.strip() or not jobs:
        return jobs

    client = anthropic.Anthropic(api_key=api_key)

    # Score in batches of 5 to stay within token limits
    batch_size = 5
    scored = []

    for i in range(0, len(jobs), batch_size):
        batch = jobs[i:i + batch_size]
        jobs_text = "\n\n".join([
            f"JOB {idx+1}:\nTitle: {j['title']}\nCompany: {j['company']}\nLocation: {j['location']}\nDescription: {j['description'][:400]}"
            for idx, j in enumerate(batch)
        ])

        prompt = f"""You are a career advisor. Score each job's relevance to the candidate's CV.

CV SUMMARY (extract key skills, experience, education):
{cv_text[:2000]}

JOBS TO SCORE:
{jobs_text}

For each job, respond ONLY with valid JSON array (no markdown), like:
[
  {{"job_index": 1, "score": 85, "reason": "Strong match: CV shows Python/ML experience, role requires exactly that", "language_concern": false}},
  ...
]

Scoring guide:
- 90-100: Near-perfect match
- 70-89: Good match, minor gaps
- 50-69: Partial match
- 30-49: Weak match
- 0-29: Poor match

Set language_concern: true if job likely requires fluent German (even if not explicit).
Keep reasons concise (max 20 words)."""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response.content[0].text.strip()
            # Strip markdown fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            scores = json.loads(raw.strip())
            for s in scores:
                idx = s["job_index"] - 1
                if 0 <= idx < len(batch):
                    batch[idx]["relevance_score"] = s.get("score", 50)
                    batch[idx]["relevance_reason"] = s.get("reason", "")
                    if s.get("language_concern"):
                        batch[idx]["language_concern"] = True
        except Exception as e:
            print(f"Claude scoring error: {e}")
            for j in batch:
                if j["relevance_score"] is None:
                    j["relevance_score"] = 50
                    j["relevance_reason"] = "Could not score"

        scored.extend(batch)
        time.sleep(0.5)

    return scored


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", profiles=SEARCH_PROFILES, cities=CITIES)


@app.route("/upload_cv", methods=["POST"])
def upload_cv():
    if "cv" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["cv"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file. Use PDF, DOCX, or TXT."}), 400
    filename = secure_filename(file.filename)
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(path)
    try:
        text = extract_cv_text(path)
        session["cv_path"] = path
        session["cv_name"] = filename
        return jsonify({"success": True, "filename": filename, "preview": text[:300]})
    except Exception as e:
        return jsonify({"error": f"Could not read CV: {str(e)}"}), 500


@app.route("/search", methods=["POST"])
def search():
    data = request.json
    adzuna_id = data.get("adzuna_id", "").strip()
    adzuna_key = data.get("adzuna_key", "").strip()
    claude_key = data.get("claude_key", "").strip()
    use_cv_scoring = data.get("use_cv_scoring", True)
    selected_profiles = data.get("profiles", [p["id"] for p in SEARCH_PROFILES])
    selected_city_ids = data.get("cities", ["bonn"])  # list of city ids

    # Resolve city objects; fall back to Bonn if none selected
    selected_cities = [CITY_MAP[cid] for cid in selected_city_ids if cid in CITY_MAP]
    if not selected_cities:
        selected_cities = [CITY_MAP["bonn"]]

    all_jobs = []

    for profile in SEARCH_PROFILES:
        if profile["id"] not in selected_profiles:
            continue
        for city in selected_cities:
            if adzuna_id and adzuna_key:
                adzuna_jobs = fetch_adzuna_jobs(profile, adzuna_id, adzuna_key, city)
                all_jobs.extend(adzuna_jobs)
            all_jobs.extend(build_linkedin_links(profile, city))

    # Score with Claude if CV + API key available AND toggle is on
    cv_path = session.get("cv_path")
    if use_cv_scoring and claude_key and cv_path and os.path.exists(cv_path):
        try:
            cv_text = extract_cv_text(cv_path)
            # Only score real jobs (not LinkedIn links)
            real_jobs = [j for j in all_jobs if j["source"] != "LinkedIn"]
            li_jobs = [j for j in all_jobs if j["source"] == "LinkedIn"]
            if real_jobs:
                real_jobs = score_jobs_with_claude(real_jobs, cv_text, claude_key)
            all_jobs = real_jobs + li_jobs
        except Exception as e:
            print(f"Scoring failed: {e}")

    # Sort: scored jobs first (by relevance desc), then unscored, then LinkedIn links
    def sort_key(j):
        if j["source"] == "LinkedIn":
            return (2, 0)
        if j["relevance_score"] is not None:
            return (0, -j["relevance_score"])
        return (1, 0)

    all_jobs.sort(key=sort_key)

    # Deduplicate
    seen_ids = set()
    unique_jobs = []
    for j in all_jobs:
        key = j.get("url") or j.get("id")
        if key not in seen_ids:
            seen_ids.add(key)
            unique_jobs.append(j)

    return jsonify({
        "jobs": unique_jobs,
        "total": len(unique_jobs),
        "scored": sum(1 for j in unique_jobs if j.get("relevance_score") is not None),
    })


if __name__ == "__main__":
    import socket, webbrowser, threading

    Path("uploads").mkdir(exist_ok=True)

    # Find a free port starting at 5000
    def find_free_port(start=5000):
        for port in range(start, start + 10):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(("localhost", port)) != 0:
                    return port
        return start  # fallback

    port = find_free_port()
    url = f"http://localhost:{port}"

    print(f"\n🎯 JobHunter is starting!")
    print(f"   → Opening {url} in your browser...")
    print(f"   (If it doesn't open, paste that URL into your browser manually)\n")
    print("   Press Ctrl+C to stop.\n")

    # Open browser after a short delay so Flask is ready
    def open_browser():
        import time; time.sleep(1.2)
        webbrowser.open(url)
    threading.Thread(target=open_browser, daemon=True).start()

    app.run(debug=False, port=port, host="127.0.0.1")
