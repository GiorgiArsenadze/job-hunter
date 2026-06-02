# 🎯 JobHunter — Multi-City Job Aggregator

A personal job search tool that aggregates listings from **Adzuna** and generates **LinkedIn deep-links** across **20 cities in Germany and the USA**, filtered for English-speaking roles, with **free AI-powered CV matching** via Groq (Llama 3).

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![Flask](https://img.shields.io/badge/Flask-3.0-green) ![Groq](https://img.shields.io/badge/AI-Groq%20free-orange) ![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

- 🔍 **Multi-source search** — Adzuna job board API + LinkedIn pre-filtered deep-links
- 🌍 **20 cities** — 10 in Germany, 10 in the USA — pick one or many at once
- 🇬🇧 **English filter** — automatically skips jobs that explicitly require fluent German
- 🤖 **Free AI CV scoring** — Groq (Llama 3 70B) scores each job's relevance against your uploaded CV (0–100%)
- 🔘 **CV scoring toggle** — turn AI scoring on/off per search without removing your key
- 📄 **CV upload** — supports PDF, DOCX, and TXT
- 🎯 **5 job profiles** — Data Science, Science Policy, Grant Reviewer, Quant Analyst, Physics Teacher
- 📊 **Sort & filter** — by relevance, date, or source
- 🏠 **Runs locally** — your CV and API keys never leave your machine
- 🚀 **Auto-opens browser** — just run `python app.py` and it launches automatically

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/GiorgiArsenadze/job-hunter.git
cd job-hunter
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
python app.py
```

Your browser opens automatically. If it doesn't, paste the URL printed in the terminal into Chrome or Safari.

---

## 🔑 API Keys (all free)

### Adzuna (job listings)
1. Go to [developer.adzuna.com](https://developer.adzuna.com)
2. Sign up — free account gives ~250 requests/month
3. Copy your **App ID** and **App Key**
4. Paste them into the app's API Configuration section

> Without Adzuna keys the app still works — you'll get LinkedIn deep-links that open pre-filtered searches in your browser.

### Groq (free AI CV scoring)
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up (free, no credit card needed)
3. Click **API Keys** in the left menu → **Create API Key**
4. Paste the `gsk_...` key into the app's Groq API Key field

> Without a Groq key, jobs are still fetched but not scored against your CV. You can also turn scoring on/off per search using the toggle switch.

---

## 🌍 Cities

| 🇩🇪 Germany | 🇺🇸 USA |
|---|---|
| Bonn | New York |
| Berlin | Washington DC |
| Munich | San Francisco |
| Hamburg | Boston |
| Frankfurt | Chicago |
| Cologne | Los Angeles |
| Düsseldorf | Seattle |
| Stuttgart | Austin |
| Leipzig | New Haven |
| Heidelberg | Princeton / NYC Metro |

Use the **🇩🇪 All Germany**, **🇺🇸 All USA**, or **Select All** quick buttons to pick cities in one click.

---

## 🎯 Job Profiles

| Profile | Keywords searched |
|---|---|
| Data Scientist | data scientist, machine learning, data science |
| Science Policy | science policy, research policy, policy analyst |
| Grant Reviewer | grant reviewer, research funding, science reviewer |
| Quantitative Analyst | quantitative researcher, data analyst, statistician |
| Physics Teacher | physics teacher, IB physics, IGCSE physics |

---

## 📁 Project Structure

```
job-hunter/
├── app.py              # Flask backend — job fetching, filtering, CV scoring
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Web UI
├── uploads/            # Temporary CV storage (gitignored)
└── README.md
```

---

## 🔧 Customisation

**Add a new job profile** — edit `SEARCH_PROFILES` in `app.py`:

```python
{
    "id": "my_new_role",
    "label": "My New Role",
    "keywords": ["keyword one", "keyword two"],
    "adzuna_category": "it-jobs",
},
```

Available Adzuna categories: `it-jobs`, `scientific-qa-jobs`, `teaching-jobs`, `engineering-jobs`, `finance-jobs`, `healthcare-nursing-jobs`, `sales-jobs`, `graduate-jobs`

**Add a new city** — add an entry to `CITIES` in `app.py`:

```python
{
    "id": "amsterdam",
    "label": "Amsterdam, Netherlands",
    "flag": "🇳🇱",
    "adzuna_country": "nl",
    "search_locations": ["Amsterdam"],
    "linkedin_geo_id": "102890719",
    "german_filter": False,
},
```

---

## ⚠️ Notes

- Uses the **Adzuna public API** — legal, free tier available
- **LinkedIn links** open pre-filtered searches in your browser where live applicant counts are visible
- The German language filter catches explicit fluency requirements in job descriptions but isn't perfect — always check the full posting
- Selecting many cities at once uses more Adzuna API requests — with the free 250/month limit, search 2–3 cities at a time for regular use
- CV and API keys are stored only in your local session and the `uploads/` folder

---

## 📜 License

MIT — free to use, modify, and share.
