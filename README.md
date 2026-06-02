# 🎯 JobHunter — Bonn Area Job Aggregator

A personal job search tool that aggregates listings from **Adzuna** and generates **LinkedIn deep-links**, filtered for English-speaking roles within 30km of Bonn, with **AI-powered CV matching** via Claude.

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![Flask](https://img.shields.io/badge/Flask-3.0-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

- 🔍 **Multi-source search** — Adzuna job board API + LinkedIn pre-filtered deep-links
- 📍 **Bonn-area filter** — searches Bonn, Cologne, Koblenz + 30km radius
- 🇬🇧 **English filter** — skips jobs explicitly requiring fluent German
- 🤖 **AI CV scoring** — Claude scores each job's relevance against your uploaded CV (0–100%)
- 📄 **CV upload** — supports PDF, DOCX, and TXT
- 🎯 **5 job profiles** — Data Science, Science Policy, Grant Reviewer, Quant Analyst, Physics Teacher
- 📊 **Sort & filter** — by relevance, date, or source
- 🏠 **Runs locally** — your CV and API keys never leave your machine

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/job-hunter.git
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

Then open **http://localhost:5000** in your browser.

---

## 🔑 API Keys (all free tiers available)

### Adzuna (job listings)
1. Go to [developer.adzuna.com](https://developer.adzuna.com)
2. Sign up for a free account (~250 requests/month free)
3. Copy your **App ID** and **App Key**
4. Paste them in the app's API Configuration section

> Without Adzuna keys, the app still works — you'll get LinkedIn deep-links that open pre-filtered searches in your browser.

### Claude API (CV scoring)
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create an account and generate an API key
3. Paste it in the app's API Configuration section
4. Cost: ~$0.01–0.05 per search session (very cheap)

> Without a Claude key, jobs are still fetched but not scored against your CV.

---

## 📁 Project Structure

```
job-hunter/
├── app.py              # Flask backend + job fetching + CV scoring
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Web UI
├── uploads/            # Temporary CV storage (gitignored)
└── README.md
```

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

## 🔧 Customisation

To add new job profiles, edit the `SEARCH_PROFILES` list in `app.py`:

```python
{
    "id": "my_new_role",
    "label": "My New Role",
    "keywords": ["keyword one", "keyword two"],
    "adzuna_category": "it-jobs",  # see Adzuna docs for categories
},
```

Available Adzuna categories: `it-jobs`, `scientific-qa-jobs`, `teaching-jobs`, `engineering-jobs`, `finance-jobs`, `healthcare-nursing-jobs`, `sales-jobs`, `graduate-jobs`

---

## ⚠️ Notes

- This tool uses the **Adzuna public API** (legal, free tier available)
- **LinkedIn links** open pre-filtered searches in your browser — live applicant counts are visible there
- The German language filter removes jobs with explicit fluency requirements from descriptions, but isn't perfect — always check the full posting
- CV and API keys are stored only in your local session and `uploads/` folder

---

## 📜 License

MIT — free to use, modify, and share.
